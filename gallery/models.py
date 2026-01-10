import uuid
from django.conf import settings
from django.db import models


class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


class Photo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="photos")

    title = models.CharField(max_length=200, blank=True)
    year = models.IntegerField(null=True, blank=True)
    tags = models.ManyToManyField("Tag", blank=True, related_name="photos")

    class Meta:
        permissions = [
            ("can_modify_tags", "Can add/remove tags on photos"),
        ]
    
    image_web = models.CharField(max_length=500)
    image_thumb = models.CharField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title or str(self.id)


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    photo = models.ForeignKey(
        "Photo",
        on_delete=models.CASCADE,
        related_name="favorited_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "photo"], name="unique_user_photo_favorite")
        ]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["photo"]),
        ]

    def __str__(self):
        return f"{self.user} ❤️ {self.photo_id}"


class Comment(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    text = models.TextField()
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user} on {self.photo}"


class Tag(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True)

    def __str__(self) -> str:
        return self.name
