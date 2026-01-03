from django.contrib import admin
from .models import Album, Photo, Comment, Tag


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "album", "title", "created_at")
    list_filter = ("album", "title", "tags")
    search_fields = ("id",)
    filter_horizontal = ("tags",)  # makes a nice multi-select UI


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "photo_link", "is_visible", "short_text")
    list_filter = ("is_visible", "created_at")
    search_fields = ("text", "user__username", "photo__id", "photo__album__title")
    ordering = ("-created_at",)

    actions = ["hide_comments", "show_comments"]

    @admin.action(description="Hide selected comments")
    def hide_comments(self, request, queryset):
        queryset.update(is_visible=False)

    @admin.action(description="Show selected comments")
    def show_comments(self, request, queryset):
        queryset.update(is_visible=True)

    @admin.display(description="Photo")
    def photo_link(self, obj):
        return f"{obj.photo.album.title}"

    @admin.display(description="Comment")
    def short_text(self, obj):
        t = obj.text.strip().replace("\n", " ")
        return (t[:60] + "…") if len(t) > 60 else t