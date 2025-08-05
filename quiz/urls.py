from django.urls import path
from .views import get_quiz

urlpatterns=[
    path('get_quiz/',get_quiz,name='get_quiz')
]