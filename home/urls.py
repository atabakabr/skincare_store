from django.urls import path,include
from .views import home_page, admin_home, product_delete, wishlist, edit_product

urlpatterns=[
    path('',home_page,name='home'),
    path('admin-home/',admin_home,name='admin_home'),
    path('product-delete/<uuid:product_id>/',product_delete,name='product_delete'),
    path('wishlist/',wishlist,name='wishlist'),
    path('recommendation/', include('recommendation.urls')),
    path("edit-product/<uuid:product_id>/",edit_product, name="edit_product"),
]
