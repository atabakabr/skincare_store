from django.shortcuts import redirect
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from products.models import Product
from search.models import browsing_history

def get_info(use_cache=True, cache_timeout=3600):
    if use_cache:
        cached_data = cache.get('get_info_data')
        if cached_data is not None:
            return cached_data

    thirty_days_ago = timezone.now() - timedelta(days=30)

    history_qs = browsing_history.objects.filter(
        timestamp__gte=thirty_days_ago
    ).values('user_id', 'product_id', 'interaction_type', 'quantity')

    history_data = list(history_qs.iterator())

    if not history_data:
        empty_df = pd.DataFrame(columns=[
            'user_id', 'product_id', 'view', 'cart', 'wishlist', 'purchased',
            'rating', 'rate_quantity', 'sold_quantity', 'category_encoded'
        ])
        if use_cache:
            cache.set('get_info_data', empty_df, cache_timeout)
        return empty_df

    df = pd.DataFrame(history_data)

    df['purchased'] = (df['interaction_type'] == 'purchase').astype(int)

    df_wide = df.pivot_table(
        index=['user_id', 'product_id'],
        columns='interaction_type',
        values='quantity',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    for col in ['view', 'cart', 'wishlist']:
        if col not in df_wide.columns:
            df_wide[col] = 0

    purchase_df = df.groupby(['user_id', 'product_id'])['purchased'].max().reset_index()
    df_wide = pd.merge(df_wide, purchase_df, on=['user_id', 'product_id'], how='left')
    df_wide['purchased'] = df_wide['purchased'].fillna(0).astype('int8')

    products_qs = Product.objects.all().values('id', 'rating', 'rate_quantity', 'sold_quantity', 'category')
    prod_data = list(products_qs.iterator())
    prod_df = pd.DataFrame(prod_data).rename(columns={'id': 'product_id'})

    category_map = {'cleaner': 0, 'serum': 1, 'moisturizer': 2, 'unknown': 3}
    prod_df['category'] = prod_df['category'].fillna('unknown')
    prod_df['category_encoded'] = prod_df['category'].map(category_map).fillna(3).astype('int8')

    final_df = pd.merge(df_wide, prod_df[['product_id', 'rating', 'rate_quantity', 'sold_quantity', 'category_encoded']],
                        on='product_id', how='left')

    for col in ['rating', 'rate_quantity', 'sold_quantity']:
        final_df[col] = final_df[col].fillna(0).astype('float32')

    final_columns = [
        'user_id', 'product_id', 'view', 'cart', 'wishlist', 'purchased',
        'rating', 'rate_quantity', 'sold_quantity', 'category_encoded'
    ]
    final_df = final_df[final_columns]

    final_df['user_id'] = final_df['user_id'].astype('int32')
    final_df['product_id'] = final_df['product_id'].astype('int32')
    final_df['view'] = final_df['view'].astype('int16')
    final_df['cart'] = final_df['cart'].astype('int16')
    final_df['wishlist'] = final_df['wishlist'].astype('int16')
    final_df['purchased'] = final_df['purchased'].astype('int8')

    if use_cache:
        cache.set('get_info_data', final_df, cache_timeout)

    return final_df


def recommend_prods_content_based(request):
    user_id = request.user.id

    try:
        model = joblib.load('xgboost_model.joblib')
        feature_cols = ["view", "rating", "rate_quantity", "sold_quantity", 
                        "cart", "wishlist", "category_encoded"]
    except FileNotFoundError:
        popular = Product.objects.order_by('-sold_quantity')[:15]
        return [str(p.id) for p in popular]

    all_products = Product.objects.all().values('id', 'rating', 'rate_quantity', 'sold_quantity', 'category')
    prod_df = pd.DataFrame(list(all_products)).rename(columns={'id': 'product_id'})

    category_map = {'cleaner': 0, 'serum': 1, 'moisturizer': 2, 'unknown': 3}
    prod_df['category_encoded'] = prod_df['category'].fillna('unknown').map(category_map).fillna(3).astype(int)

    user_history = browsing_history.objects.filter(user_id=user_id).values('product_id', 'interaction_type', 'quantity')
    hist_df = pd.DataFrame(list(user_history))

    if not hist_df.empty:
        hist_pivot = hist_df.pivot_table(
            index='product_id',
            columns='interaction_type',
            values='quantity',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        for col in ['view', 'cart', 'wishlist']:
            if col not in hist_pivot.columns:
                hist_pivot[col] = 0
        hist_pivot = hist_pivot[['product_id', 'view', 'cart', 'wishlist']]
    else:
        hist_pivot = pd.DataFrame(columns=['product_id', 'view', 'cart', 'wishlist'])

    user_features = prod_df.merge(hist_pivot, on='product_id', how='left')
    user_features[['view', 'cart', 'wishlist']] = user_features[['view', 'cart', 'wishlist']].fillna(0)

    X = user_features[feature_cols].fillna(0)

    proba = model.predict_proba(X)[:, 1]
    user_features['purchase_prob'] = proba * 100

    recommendations = user_features.sort_values('purchase_prob', ascending=False)

    purchased_products = browsing_history.objects.filter(
        user_id=user_id, interaction_type='purchase'
    ).values_list('product_id', flat=True)
    recommendations = recommendations[~recommendations['product_id'].isin(purchased_products)]

    top_15 = recommendations.head(8)
    prod_ids = top_15['product_id'].astype(str).tolist()
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
