from django.shortcuts import get_object_or_404, render, redirect
from .models import Album, Photo, Tag, Comment
from django.db.models import Count, Q

def album_list(request):
    albums = Album.objects.order_by("-created_at")
    return render(request, "gallery/album_list.html", {"albums": albums})


def album_detail(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    photos = album.photos.order_by("created_at")
    return render(request, "gallery/album_detail.html", {"album": album, "photos": photos})


def photo_detail(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)

    if request.method == "POST":
        text = (request.POST.get("text") or "").strip()
        if text:
            Comment.objects.create(photo=photo, user=request.user, text=text)
        return redirect("photo_detail", photo_id=photo.id)

    comments = photo.comments.filter(is_visible=True).order_by("-created_at")
    return render(request, "gallery/photo_detail.html", {"photo": photo, "comments": comments})

from django.db.models import Count, Q
from django.shortcuts import render
from .models import Photo, Tag


def photo_browser(request):
    selected = request.GET.getlist("tags")
    untagged = request.GET.get("untagged") == "1"

    photos = Photo.objects.select_related("album").prefetch_related("tags").order_by("-created_at")

    if untagged:
        photos = photos.filter(tags__isnull=True)

    if selected:
        photos = (
            photos.filter(tags__slug__in=selected)
            .annotate(matched=Count("tags", filter=Q(tags__slug__in=selected), distinct=True))
            .filter(matched=len(selected))
        )

    all_tags = Tag.objects.order_by("name")

    return render(
        request,
        "gallery/photo_browser.html",
        {"photos": photos.distinct(), "all_tags": all_tags, "selected": set(selected), "untagged": untagged},
    )

def home(request):
    stats = {
        "albums": Album.objects.count(),
        "photos": Photo.objects.count(),
        "tags": Tag.objects.count(),
        "comments": Comment.objects.count(),
    }
    latest_albums = Album.objects.order_by("-created_at")[:5]
    latest_photos = Photo.objects.order_by("-created_at")[:12]

    return render(request, "gallery/home.html", {
        "stats": stats,
        "latest_albums": latest_albums,
        "latest_photos": latest_photos,
    })