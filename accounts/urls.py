from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns=[
    path('login/',auth_views.LoginView.as_view(template_name='accounts/login.html'),name='login'),
    path('logout/',auth_views.LogoutView.as_view(),name='logout'),
    path('signup/',views.signup_view,name='signup'),
    path('show_profile/',views.show_profile,name='show_profile'),
    path('edit_profile/',views.edit_profile,name='edit_profile'),
    path('faq/',views.faq,name='faq'),
    path('show_purchase_items/',views.show_purchase_items,name='show_purchase_items')

]



