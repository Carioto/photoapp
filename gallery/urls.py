from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("albums/", views.album_list, name="album_list"),
    path("photos/", views.photo_browser, name="photo_browser"),
    path("album/<uuid:album_id>/", views.album_detail, name="album_detail"),
    path("photo/<uuid:photo_id>/", views.photo_detail, name="photo_detail"),
    path("photo/<uuid:photo_id>/favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("favorites/", views.favorites, name="favorites"),
    path("comments/", views.recent_comments, name="recent_comments"),
    path("photo/<uuid:photo_id>/tags/", views.edit_photo_tags, name="edit_photo_tags"),

]