from urllib import request
from django.shortcuts import get_object_or_404, render, redirect
from .models import Album, Photo, Tag, Comment, Favorite
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.contrib.auth.decorators import permission_required
from .forms import PhotoTagsForm, CreateTagForm
import logging
logger = logging.getLogger(__name__)



def album_list(request):
    albums = Album.objects.order_by("-created_at")
    return render(request, "gallery/album_list.html", {"albums": albums})


def album_detail(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    photos = album.photos.order_by("created_at")
    return render(request, "gallery/album_detail.html", {"album": album, "photos": photos})


def photo_detail(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    is_favorited = Favorite.objects.filter(user=request.user, photo=photo).exists()
    next_url = request.GET.get("next", "")
    if request.method == "POST":
        text = (request.POST.get("text") or "").strip()
        if text:
            Comment.objects.create(photo=photo, user=request.user, text=text)
        return redirect("photo_detail", photo_id=photo.id)

    comments = photo.comments.filter(is_visible=True).order_by("-created_at")
    return render(request, "gallery/photo_detail.html", {"photo": photo, "comments": comments, "is_favorited": is_favorited,"next_url": next_url,})

@login_required
def toggle_favorite(request, photo_id):
    if request.method != "POST":
        return redirect("photo_detail", photo_id=photo_id)

    photo = get_object_or_404(Photo, id=photo_id)

    fav = Favorite.objects.filter(user=request.user, photo=photo).first()
    if fav:
        fav.delete()
    else:
        Favorite.objects.create(user=request.user, photo=photo)
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url:
        return redirect(next_url)

    return redirect("photo_detail", photo_id=photo_id)


def photo_browser(request):
    selected = request.GET.getlist("tags")
    untagged = request.GET.get("untagged") == "1"

    photos = (
        Photo.objects
        .select_related("album")
        .prefetch_related("tags")
        .order_by("-created_at")
    )

    if untagged:
        photos = photos.filter(tags__isnull=True)

    if selected:
        photos = (
            photos.filter(tags__slug__in=selected)
            .annotate(
                matched=Count(
                    "tags",
                    filter=Q(tags__slug__in=selected),
                    distinct=True,
                )
            )
            .filter(matched=len(selected))
        )

    photos = photos.distinct()
    
    if request.user.is_authenticated:
        photos = photos.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(user=request.user, photo_id=OuterRef("pk"))
            )
        )

    # Pagination
    paginator = Paginator(photos, 40)  # show 48 photos per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    all_tags = Tag.objects.order_by("name")

    return render(
        request,
        "gallery/photo_browser.html",
        {
            "photos": page_obj.object_list,
            "page_obj": page_obj,
            "all_tags": all_tags,
            "selected": set(selected),
            "untagged": untagged,
        },
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


@login_required
def favorites(request):
    photos = (
        Photo.objects.filter(favorited_by__user=request.user)
        .select_related("album")
        .prefetch_related("tags")
        .order_by("-favorited_by__created_at")
        .distinct()
    )
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return render(request, "gallery/favorites.html", {"photos": photos})


def recent_comments(request):
    comments = (
        Comment.objects
        .select_related("photo", "user")
        .order_by("-created_at")[:100]
    )
    return render(request, "gallery/recent_comments.html", {"comments": comments})


@permission_required("gallery.can_modify_tags", raise_exception=True)
def edit_photo_tags(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    next_url = request.GET.get("next") or request.POST.get("next") or ""

    try:
        if request.method == "POST":
            if "create_tag" in request.POST:
                create_form = CreateTagForm(request.POST)
                form = PhotoTagsForm(instance=photo)
                if create_form.is_valid():
                    create_form.save()
                    return redirect("edit_photo_tags", photo_id=photo.id)
            else:
                form = PhotoTagsForm(request.POST, instance=photo)
                create_form = CreateTagForm()
                if form.is_valid():
                    form.save()
                    return redirect("photo_detail", photo_id=photo.id)
        else:
            form = PhotoTagsForm(instance=photo)
            create_form = CreateTagForm()

        return render(request, "gallery/edit_photo_tags.html", {
            "photo": photo,
            "form": form,
            "create_form": create_form,
            "next_url": next_url,
        })

    except Exception:
        logger.exception("edit_photo_tags failed (photo_id=%s, user=%s)", photo_id, getattr(request.user, "username", None))
        raise

