from django.urls import path
from .views import add_to_cart, delete_from_cart, cart, finalize_order, success_page

urlpatterns=[
    path('add_to_cart/<uuid:product_id>/',add_to_cart,name='add_to_cart'),
    path('delete_from_cart/<uuid:product_id>/',delete_from_cart,name='delete_from_cart'),
    path('cart/',cart,name='cart'),
    path('finalize_order/',finalize_order,name='finalize_order'),
    path('cart/success/',success_page, name='success_page')

]