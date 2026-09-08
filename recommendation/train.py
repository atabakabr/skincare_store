import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
import joblib
import pathlib

def train():
    cpth = pathlib.Path().absolute()

    df = pd.read_csv(f"{cpth}/skincare_store/recommendation/xgboost_recommender_synthetic_80000.csv")
    X = df.drop('target_cart', axis=1)
    Y = df['target_cart']

    num_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    cat_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()

    num_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    cat_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_transformer, num_cols),
            ('cat', cat_transformer, cat_cols)
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=.2)

    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', xgb.XGBClassifier(
            n_estimators=150,
            learning_rate=0.1,
            max_depth=5,
            random_state=42,
            eval_metric='logloss',
            use_label_encoder=False
        ))
    ])

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    accuracy_percent = accuracy * 100

    print(f"✅ : {accuracy_percent:.2f}%")

    print("\n📊")
    print(classification_report(y_test, y_pred))

    joblib.dump(model, 'xgboost_model.joblib')
    print("Model saved!")


if __name__ == "__main__" :
    train()
    