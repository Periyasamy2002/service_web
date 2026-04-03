from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class Profile(models.Model):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("agent", "Agent"),
        ("user", "User"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default="user")

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Service(models.Model):
    name = models.CharField(max_length=250)
    charges = models.DecimalField(max_digits=10, decimal_places=2)
    documents_required = models.CharField(max_length=500, blank=True)
    tutorial_link = models.URLField(blank=True, null=True)
    apply_link = models.URLField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="services")
    created_at = models.DateTimeField(auto_now_add=True)

    def documents_list(self):
        return [doc.strip() for doc in self.documents_required.split(",") if doc.strip()]

    def __str__(self):
        return self.name


class DynamicPage(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="dynamic_pages")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
