from django.contrib import admin

from .models import DynamicPage, Profile, Service


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "charges", "created_by", "created_at")
    search_fields = ("name", "documents_required")


@admin.register(DynamicPage)
class DynamicPageAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_by", "created_at")
