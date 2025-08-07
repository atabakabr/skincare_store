from django.urls import path
from .views import get_quiz,second_quiz,show_routine

urlpatterns=[
    path('get_quiz/',get_quiz,name='get_quiz'),
    path('second_quiz/',second_quiz,name='second_quiz'),
    path('show_routine/',show_routine,name='show_routine')
]