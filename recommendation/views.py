from django.shortcuts import redirect
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
import torch
import torch.nn as nn
import torch.nn.functional as F
from products.models import Product
from search.models import browsing_history
from sklearn.metrics.pairwise import cosine_similarity

class RecommenderMLP(nn.Module):
    def __init__(self,input_dim):
        super().__init__()
        self.net=nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16,8),
            nn.ReLU(),
            nn.Linear(8,1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.net(x)

def get_info():
    history=browsing_history.objects.values('user_id','product_id','interaction_type','quantity')
    df=pd.DataFrame(list(history))

    df_wide=df.pivot_table(
        index=['user_id','product_id'],
        columns='interaction_type',
        values='quantity',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    df_wide.columns.name=None
    products=Product.objects.all().values('id','rating','rate_quantity','sold_quantity','category')
    prod_df=pd.DataFrame(list(products)).rename(columns={'id':'product_id'})
    final_df=pd.merge(df_wide,prod_df,on='product_id',how='left')

    #instead of one hot
    final_df['category']=final_df['category'].fillna('unknown')
    category_map={'cleaner':0,'serum': 1,'moisturizer':2,'unknown':3}
    final_df['category_encoded']=final_df['category'].map(category_map)

    return(final_df)

def train_model(request):
    final_df=get_info()
    
    feature_cols=["view","rating","rate_quantity","sold_quantity","cart","wishlist",'category_encoded']
    input_features=final_df[feature_cols].fillna(0).values
    input_dim=input_features.shape[1]
        
    X=torch.tensor(input_features, dtype=torch.float32)
    y=final_df['cart'].apply(lambda v: 1 if v > 0 else 0).values
    Y=torch.tensor(y, dtype=torch.float32).unsqueeze(1)


    model=RecommenderMLP(input_dim)

    loss_fn=nn.BCELoss()
    optimizer=torch.optim.Adam(model.parameters(), lr=0.01)
    for i in range(100):
        model.train()
        optimizer.zero_grad()
        outputs=model(X)
        loss=loss_fn(outputs,Y)
        loss.backward()
        optimizer.step()

    torch.save(model.state_dict(), "model.pt")
    return redirect(request.META.get('HTTP_REFERER', '/'))



def recommend_prods_content_based(request):
    feature_cols=["view", "rating", "rate_quantity", "sold_quantity", "cart", "wishlist",'category_encoded']
    final_df=get_info()
    input_features=final_df[feature_cols].fillna(0).values

    model=RecommenderMLP(input_features.shape[1])
    model.load_state_dict(torch.load("model.pt"))
    model.eval()
    user_id=request.user.id
    user_df=final_df[final_df['user_id']==user_id]

    feature_cols=["view", "rating", "rate_quantity", "sold_quantity", "cart", "wishlist",'category_encoded']
    X=user_df[feature_cols].fillna(0).values
    X_tensor=torch.tensor(X,dtype=torch.float32)

    with torch.no_grad():
        scores=model(X_tensor).squeeze().numpy()

    user_df=user_df.copy()
    user_df['score']=scores

    recommendations=user_df.sort_values(by='score',ascending=False).head(10)
    prod_ids=recommendations['product_id'].tolist()
    prod_ids=[str(pid) for pid in recommendations['product_id']]
    return prod_ids

def recommend_prods_collab(request):
    final_df=get_info()

    final_df['score']=final_df[['cart','wishlist']].sum(axis=1)

    user_item=final_df.pivot_table(index='user_id',columns='product_id',values='score',fill_value=0)

    if request.user.id not in user_item.index:
        return []

    user_sim=cosine_similarity(user_item)
    user_sim_df=pd.DataFrame(user_sim,index=user_item.index,columns=user_item.index)

    curr_user=request.user.id
    similar_users=user_sim_df[curr_user].drop(curr_user)
    similar_users=similar_users[similar_users>0].sort_values(ascending=False)

    unseen_items=user_item.loc[curr_user][user_item.loc[curr_user]==0].index
    if len(unseen_items)==0:
        return []
    #transpose and weighting
    scores=user_item.loc[similar_users.index,unseen_items].T.dot(similar_users)
    
    prod_ids=scores.sort_values(ascending=False).head(8).index.tolist()
    return [str(pid) for pid in prod_ids]
