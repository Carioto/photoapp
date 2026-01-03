from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("albums/", views.album_list, name="album_list"),
    path("photos/", views.photo_browser, name="photo_browser"),
    path("album/<uuid:album_id>/", views.album_detail, name="album_detail"),
    path("photo/<uuid:photo_id>/", views.photo_detail, name="photo_detail"),
]