from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DynamicPageForm, RegisterForm, ServiceForm
from .models import DynamicPage, Profile, Service


def _user_role(user):
    if not user.is_authenticated:
        return "anonymous"
    return getattr(user.profile, "role", "user")


def _can_manage_services(user):
    return _user_role(user) in ["admin", "agent"]


def _has_agent_permissions(user):
    return _user_role(user) in ["admin", "agent"]


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # profile created by signal, default role user
            login(request, user)
            messages.success(request, "Registration successful")
            return redirect("dashboard")
        messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()
    return render(request, "core/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "core/login.html", {"form": form})


def login_board(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "core/login_board.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    services = Service.objects.all().order_by("-created_at")
    pages = DynamicPage.objects.all().order_by("name")
    role = _user_role(request.user)
    context = {
        "services": services,
        "pages": pages,
        "role": role,
        "can_manage": _can_manage_services(request.user),
        "page_title": "Service Dashboard",
        "page_description": "Browse and manage services based on your role.",
    }
    return render(request, "core/dashboard.html", context)


@login_required
def add_service(request):
    if not _can_manage_services(request.user):
        messages.error(request, "You do not have permission to add services.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.created_by = request.user
            service.save()
            messages.success(request, "Service created successfully.")
            return redirect("dashboard")
    else:
        form = ServiceForm()
    return render(request, "core/service_form.html", {"form": form, "title": "Add Service"})


@login_required
def edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if not _can_manage_services(request.user):
        messages.error(request, "You do not have permission to edit services.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Service updated successfully.")
            return redirect("dashboard")
    else:
        form = ServiceForm(instance=service)
    return render(request, "core/service_form.html", {"form": form, "title": "Edit Service"})


@login_required
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if not _can_manage_services(request.user):
        messages.error(request, "You do not have permission to delete services.")
        return redirect("dashboard")

    if request.method == "POST":
        service.delete()
        messages.success(request, "Service deleted successfully.")
        return redirect("dashboard")
    return render(request, "core/delete_confirm.html", {"object": service, "item_name": service.name})


@login_required
def add_page(request):
    if not _has_agent_permissions(request.user):
        messages.error(request, "You do not have permission to add dynamic pages.")
        return redirect("dashboard")

    if request.method == "POST":
        form = DynamicPageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.created_by = request.user
            page.save()
            messages.success(request, "Page added successfully.")
            return redirect("dashboard")
    else:
        form = DynamicPageForm()

    pages = DynamicPage.objects.all().order_by("name")
    return render(
        request,
        "core/add_page.html",
        {"form": form, "pages": pages, "page_title": "Add Page", "page_description": "Create dynamic pages for quick navigation."},
    )


@login_required
def dynamic_page_view(request, slug):
    page = get_object_or_404(DynamicPage, slug=slug)
    services = Service.objects.all().order_by("-created_at")
    pages = DynamicPage.objects.all().order_by("name")
    return render(
        request,
        "core/dynamic_page.html",
        {
            "page": page,
            "services": services,
            "pages": pages,
            "role": _user_role(request.user),
            "can_manage": _can_manage_services(request.user),
            "page_title": page.name,
            "page_description": page.description or "Custom dynamic page",
        },
    )


@login_required
def user_list(request):
    if not _has_agent_permissions(request.user):
        messages.error(request, "You do not have permission to view users.")
        return redirect("dashboard")
    users = User.objects.all().order_by("username")
    pages = DynamicPage.objects.all().order_by("name")
    return render(request, "core/user_list.html", {"users": users, "pages": pages, "role": _user_role(request.user)})


@login_required
def edit_user(request, user_id):
    if not _has_agent_permissions(request.user):
        messages.error(request, "You do not have permission to edit users.")
        return redirect("dashboard")
    target = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        target.email = request.POST.get("email", target.email)
        target.first_name = request.POST.get("first_name", target.first_name)
        target.last_name = request.POST.get("last_name", target.last_name)
        target.save()
        role = request.POST.get("role", target.profile.role)
        target.profile.role = role
        target.profile.save()
        messages.success(request, "User updated.")
        return redirect("user_list")
    pages = DynamicPage.objects.all().order_by("name")
    return render(request, "core/edit_user.html", {"user_obj": target, "pages": pages, "role": _user_role(request.user)})
