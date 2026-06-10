from django.urls import path
from . import views

urlpatterns = [
    path('posts/naive', views.naive_posts, name='naive-posts'),
    path('posts/optimized', views.optimized_posts, name='optimized-posts'),
    path('posts/advanced', views.advanced_posts, name='advanced-posts'),
]
