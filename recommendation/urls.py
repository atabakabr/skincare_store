from django.urls import path
from . import views
urlpatterns=[
    path('train_model/',views.train_model,name='train_model'),
    path('recommendation/',views.recommend_prods_content_based,name='recommendation')
]