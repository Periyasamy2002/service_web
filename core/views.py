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


def admin_login(request):
    """Admin-only login page"""
    if request.user.is_authenticated:
        if _user_role(request.user) == "admin":
            return redirect("dashboard")
        return redirect("login_board")
    
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Check if user is admin
            if hasattr(user, 'profile') and user.profile.role == "admin":
                login(request, user)
                messages.success(request, f"Welcome, {user.first_name or user.username}!")
                return redirect("dashboard")
            else:
                messages.error(request, "You do not have admin access. Please use the regular login.")
                return render(request, "core/admin_agent_login.html", {"form": form, "is_admin": True})
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "core/admin_agent_login.html", {"form": form, "is_admin": True})


def login_board(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "core/login_board.html")


def logout_view(request):
    logout(request)
    return redirect("login_board")


@login_required
def dashboard(request):
    role = _user_role(request.user)
    
    # Redirect to login board if user is not authenticated
    if role == "anonymous":
        return redirect("login_board")
    
    # Only Admin and Agent dashboards are available
    # Regular users are redirected to a landing page or can view it as read-only
    if role not in ["admin", "agent"]:
        # Users can still view the dashboard but in read-only mode
        pass
    
    # Get base context data
    # Only show global services (without a page assigned) on dashboard
    services = Service.objects.filter(page__isnull=True).order_by("-created_at")
    pages = DynamicPage.objects.all().order_by("name")
    
    # Filter services based on search query
    search_query = request.GET.get('search', '')
    if search_query:
        services = services.filter(name__icontains=search_query)
    
    context = {
        "services": services,
        "pages": pages,
        "role": role,
        "can_manage": _can_manage_services(request.user),
        "page_title": f"{role.capitalize()} Dashboard",
        "page_description": f"Welcome to your {role} dashboard.",
        "search_query": search_query,
        "service_count": services.count(),
    }
    
    # Add role-specific context
    if role == "admin":
        context.update({
            "users": User.objects.all().order_by("-date_joined"),
            "total_users": User.objects.count(),
            "total_agents": User.objects.filter(profile__role="agent").count(),
            "total_regular_users": User.objects.filter(profile__role="user").count(),
        })
    elif role == "agent":
        # Count services created by this agent
        user_services = Service.objects.filter(created_by=request.user)
        context.update({
            "user_services_count": user_services.count(),
        })
    
    # Use unified dashboard template for all authenticated users
    return render(request, "core/unified_dashboard.html", context)


@login_required
def add_service(request):
    if not _can_manage_services(request.user):
        messages.error(request, "You do not have permission to add services.")
        return redirect("dashboard")

    # Get page_id from query parameter if provided (for adding from a dynamic page)
    page_id = request.GET.get('page_id')
    initial_data = {}
    if page_id:
        try:
            page = DynamicPage.objects.get(id=page_id)
            initial_data['page'] = page
        except DynamicPage.DoesNotExist:
            pass

    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.created_by = request.user
            service.save()
            messages.success(request, "Service created successfully.")
            # Redirect to the page if page was specified
            if service.page:
                return redirect("dynamic_page", slug=service.page.slug)
            return redirect("dashboard")
    else:
        form = ServiceForm(initial=initial_data)
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
            # Redirect to the page if page is assigned
            if service.page:
                return redirect("dynamic_page", slug=service.page.slug)
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
def service_detail(request, service_id):
    """Display detailed information about a service"""
    service = get_object_or_404(Service, id=service_id)
    
    # Get related services - show only services from the same page (or global if no page)
    if service.page:
        related_services = service.page.services.all().exclude(id=service_id).order_by("-created_at")[:6]
    else:
        related_services = Service.objects.filter(page__isnull=True).exclude(id=service_id).order_by("-created_at")[:6]
    
    pages = DynamicPage.objects.all().order_by("name")
    
    context = {
        "service": service,
        "related_services": related_services,
        "pages": pages,
        "role": _user_role(request.user),
        "can_manage": _can_manage_services(request.user),
    }
    
    return render(request, "core/service_detail.html", context)


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
    services = page.services.all().order_by("-created_at")
    pages = DynamicPage.objects.all().order_by("name")
    
    # Get other pages (all except current)
    other_pages = DynamicPage.objects.exclude(id=page.id).order_by("name")
    
    # Filter services based on search query
    search_query = request.GET.get('service_search', '')
    if search_query:
        services = services.filter(name__icontains=search_query)
    
    return render(
        request,
        "core/dynamic_page.html",
        {
            "page": page,
            "services": services,
            "pages": pages,
            "other_pages": other_pages,
            "role": _user_role(request.user),
            "can_manage": _can_manage_services(request.user),
            "page_title": page.name,
            "page_description": page.description or "Custom dynamic page",
            "search_query": search_query,
        },
    )


@login_required
def pages_list(request):
    """Display all pages in card format"""
    pages = DynamicPage.objects.all().order_by("name")
    
    # Filter pages based on search query
    search_query = request.GET.get('search', '')
    if search_query:
        pages = pages.filter(name__icontains=search_query)
    
    return render(
        request,
        "core/pages_list.html",
        {
            "pages": pages,
            "role": _user_role(request.user),
            "can_manage": _can_manage_services(request.user),
            "search_query": search_query,
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
