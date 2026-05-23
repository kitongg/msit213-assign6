from django.urls import path
from . import views

app_name = 'albums'

urlpatterns = [
    path('', views.AlbumListView.as_view(), name='album-list'),
    path('accounts/register/', views.RegisterView.as_view(), name='register'),
    path('album/add/', views.AlbumCreateView.as_view(), name='album-add'),
    path('album/<int:pk>/', views.AlbumDetailView.as_view(), name='album-detail'),
    path('album/<int:pk>/edit/', views.AlbumUpdateView.as_view(), name='album-edit'),
    path('album/<int:pk>/delete/', views.AlbumDeleteView.as_view(), name='album-delete'),
    path('album/<int:album_pk>/photo/add/', views.PhotoCreateView.as_view(), name='photo-add'),
    path('photo/<int:pk>/edit/', views.PhotoUpdateView.as_view(), name='photo-edit'),
    path('photo/<int:pk>/delete/', views.PhotoDeleteView.as_view(), name='photo-delete'),
]
