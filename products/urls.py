from django.urls import path
from .views import view_product, rate_product, add_wishlist, delete_from_wishlist

urlpatterns=[
    path('view_product/<uuid:product_id>/',view_product,name='view_product'),
    path('rate/<uuid:product_id>/',rate_product,name='rate_product'),
    path('add_wishlist/<uuid:product_id>/',add_wishlist,name='add_wishlist'),
    path('delete_from_wishlist/<uuid:product_id>/',delete_from_wishlist,name='delete_from_wishlist')
]