# Dashboard Restructuring - Implementation Reference

## Overview

This document provides detailed reference information about all changes made to restructure your Django dashboard application.

---

## 1. New Views Added

### service_detail() view in core/views.py

```python
@login_required
def service_detail(request, service_id):
    """Display detailed information about a service"""
    service = get_object_or_404(Service, id=service_id)
    related_services = Service.objects.all().order_by("-created_at")[:6]
    pages = DynamicPage.objects.all().order_by("name")
    
    context = {
        "service": service,
        "related_services": related_services,
        "pages": pages,
        "role": _user_role(request.user),
        "can_manage": _can_manage_services(request.user),
    }
    
    return render(request, "core/service_detail.html", context)
```

**Features:**
- Retrieves single service by ID
- Gets related services for display
- Determines if user can manage (admin/agent)
- Passes all context to template

---

## 2. Updated Dashboard View

### Old dashboard() view
```python
# Routed to different templates based on role:
if role == "admin":
    return render(request, "core/admin_dashboard.html", context)
elif role == "agent":
    return render(request, "core/agent_dashboard.html", context)
else:  # regular user
    return render(request, "core/user_dashboard.html", context)
```

### New dashboard() view
```python
# All roles use unified template:
return render(request, "core/unified_dashboard.html", context)
```

**Context Data Provided:**
```python
context = {
    "services": services,          # All services or filtered
    "pages": pages,                # All dynamic pages
    "role": role,                  # User's role
    "can_manage": can_manage,      # Can user create/edit/delete?
    "page_title": title,           # Page title
    "page_description": desc,      # Page description
    "search_query": search_query,  # Current search query
    "service_count": count,        # Number of services
}

# Additional for admin:
"users": users,                    # All users
"total_users": count,              # Total user count
"total_agents": count,             # Total agent count
"total_regular_users": count,      # Total regular user count

# Additional for agent:
"user_services_count": count,      # Services created by agent
```

---

## 3. URL Configuration Changes

### core/urls.py

```python
# Before:
path("services/add/", views.add_service, name="add_service"),
path("services/<int:service_id>/edit/", views.edit_service, name="edit_service"),
path("services/<int:service_id>/delete/", views.delete_service, name="delete_service"),

# After:
path("services/add/", views.add_service, name="add_service"),
path("services/<int:service_id>/", views.service_detail, name="service_detail"),
path("services/<int:service_id>/edit/", views.edit_service, name="edit_service"),
path("services/<int:service_id>/delete/", views.delete_service, name="delete_service"),
```

**Important:** Order matters! The detail route must come before edit/delete routes.

---

## 4. New Templates

### A. unified_dashboard.html

**Location:** `core/templates/core/unified_dashboard.html`

**Key Features:**
- Responsive grid layout
- Service cards (not tables)
- Top-right search bar
- Filter dropdown
- Role-based statistics
- Dynamic JavaScript filtering
- Action buttons (conditional)
- User management table (admin only)

**CSS Classes Added:**
```css
.dashboard-header          /* Main header with search */
.search-bar-container      /* Search input + dropdown + button */
.filter-dropdown           /* Sort/filter dropdown */
.stats-container           /* Statistics cards grid */
.stat-card                 /* Individual stat card */
.stat-card.admin           /* Admin-specific color */
.stat-card.agent           /* Agent-specific color */
.service-cards-container   /* Grid of service cards */
.service-card              /* Individual service card */
.service-card:hover        /* Hover animation */
.service-card-header       /* Card header with title */
.service-card-body         /* Card content area */
.service-meta              /* Price and creator info */
.service-documents        /* Required documents section */
.service-actions          /* Edit/Delete or Apply button */
```

**JavaScript Functions:**
```javascript
filterServices()           /* Main filter function */
                          /* Uses search + dropdown values */
                          /* Re-renders cards dynamically */
```

**Statistics Shown:**
- Admin: Total Users, Agents, Regular Users, Services
- Agent: Total Services, Created By You
- User: (No extra stats, read-only view)

---

### B. service_detail.html

**Location:** `core/templates/core/service_detail.html`

**Key Features:**
- Service header with gradient background
- Detailed service information
- Required documents list
- Service provider information
- Tutorial and apply links
- Edit/Delete buttons (admin/agent)
- Apply button (users)
- Related services carousel
- Back to dashboard button

**CSS Classes Added:**
```css
.service-detail-header     /* Top header section */
.service-detail-content    /* Main content grid */
.service-info-card         /* Info section */
.sidebar                   /* Right sidebar */
.sidebar-card              /* Sidebar item */
.price-display             /* Large price display */
.info-item                 /* Information item */
.info-label                /* Item label */
.info-value                /* Item value */
.documents-list            /* Documents list styling */
.related-services          /* Related services grid */
```

**Content Sections:**
1. Service Header
2. Service Information
   - Description
   - Required Documents
   - Useful Links
   - Created Date
3. Sidebar
   - Service Fee (price)
   - Edit/Delete buttons (admin/agent)
   - Apply button (users)
   - Service Status
   - Service Provider Info
4. Related Services

---

## 5. Template Inheritance Structure

### Base Template (base.html)
```
base.html
├── navigation bar (all pages)
├── sidebar (authenticated users)
└── content section ({% block content %})
     └── Filled by child templates
```

### Child Templates Structure
```
unified_dashboard.html extends base.html
└── {% block content %}
    ├── Dashboard header
    ├── Statistics cards
    ├── Action buttons
    ├── Service cards container
    │   ├── For each service:
    │   │   └── Service card
    │   │       ├── header
    │   │       ├── body (meta, docs, actions)
    │   │       └── buttons
    │   └── Empty state (if no services)
    └── User management table (admin only)

service_detail.html extends base.html
└── {% block content %}
    ├── Back button
    ├── Detail header
    ├── Content grid (2 columns)
    │   ├── Left: Service info
    │   │   ├── description
    │   │   ├── documents
    │   │   └── links
    │   └── Right: Sidebar
    │       ├── price
    │       ├── buttons
    │       ├── status
    │       └── provider
    └── Related services grid
```

---

## 6. JavaScript Implementation

### Search & Filter Logic

```javascript
// Event listeners
document.getElementById('serviceSearch').addEventListener('keyup', filterServices);
document.getElementById('filterDropdown').addEventListener('change', filterServices);

// Main filtering function
function filterServices() {
    // 1. Get current search query
    const searchQuery = document.getElementById('serviceSearch').value.toLowerCase();
    
    // 2. Get filter type
    const filterType = document.getElementById('filterDropdown').value;
    
    // 3. Get all service cards
    const cards = Array.from(document.querySelectorAll('.service-card'));
    
    // 4. Filter by search term
    let filtered = cards.filter(card => {
        const title = card.querySelector('.service-card-title').textContent.toLowerCase();
        return title.includes(searchQuery);
    });
    
    // 5. Sort based on filter
    if (filterType === 'newest') {
        // Keep original order
    } else if (filterType === 'oldest') {
        filtered.reverse();
    } else if (filterType === 'price-low') {
        // Sort by price ascending
    } else if (filterType === 'price-high') {
        // Sort by price descending
    }
    
    // 6. Re-render container
    container.innerHTML = '';
    if (filtered.length === 0) {
        // Show empty state
    } else {
        // Add filtered cards to container
    }
}
```

**How It Works:**
1. User types in search box → keyup event fires
2. User selects filter → change event fires
3. Both call filterServices()
4. Function collects all cards
5. Filters by search term
6. Sorts by selected filter
7. Re-renders container with results
8. **No page reload!**

---

## 7. Conditional Rendering Logic

### In Templates (Django Template Language)

```django
{% if can_manage %}
    <!-- Show edit/delete buttons -->
    <a href="{% url 'edit_service' service.id %}" class="btn btn-primary">
        <i class="fas fa-edit"></i> Edit
    </a>
{% else %}
    <!-- Show apply button for users -->
    <a href="{{ service.apply_link }}" class="btn btn-success">
        <i class="fas fa-external-link-alt"></i> Apply
    </a>
{% endif %}

<!-- Admin-only content -->
{% if role == 'admin' %}
    <!-- User management table -->
    <div class="card">
        <!-- Table content -->
    </div>
{% endif %}

<!-- Statistics based on role -->
{% if role == 'admin' %}
    <!-- Admin stats -->
{% elif role == 'agent' %}
    <!-- Agent stats -->
{% endif %}
```

### In Views (Python)

```python
# Check permissions
if not _can_manage_services(request.user):
    messages.error(request, "Permission denied")
    return redirect("dashboard")

# Add conditional context
if role == "admin":
    context['users'] = User.objects.all()
elif role == "agent":
    context['user_services_count'] = count
```

---

## 8. Service Card Structure

### HTML Structure

```html
<div class="service-card">
    <!-- Header -->
    <div class="service-card-header">
        <h3 class="service-card-title">Service Name</h3>
    </div>
    
    <!-- Body -->
    <div class="service-card-body">
        <!-- Meta info -->
        <div class="service-meta">
            <span class="service-price">₹ 500</span>
            <small class="text-muted">by Creator</small>
        </div>
        
        <!-- Documents -->
        <div class="service-documents">
            <strong>Required:</strong> PAN, Aadhar...
        </div>
        
        <!-- Actions -->
        <div class="service-actions">
            <a href="/services/1/edit/" class="btn btn-primary">Edit</a>
            <a href="/services/1/delete/" class="btn btn-danger">Delete</a>
        </div>
    </div>
</div>
```

### Click Behavior

```html
<!-- Clicking card navigates to detail page -->
<div class="service-card" onclick="window.location='{% url 'service_detail' service.id %}'">
    ...
</div>

<!-- Buttons use stopPropagation to prevent card click -->
<a href="/services/1/edit/" onclick="event.stopPropagation();">
    Edit
</a>
```

---

## 9. Responsive Design

### Breakpoints

```css
/* Desktop (1200px+) */
.service-cards-container {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}

/* Tablet (768px - 1199px) */
@media (max-width: 768px) {
    .dashboard-header {
        flex-direction: column;
    }
    .service-cards-container {
        grid-template-columns: 1fr;
    }
}

/* Mobile (<768px) */
@media (max-width: 576px) {
    .service-detail-content {
        grid-template-columns: 1fr;
    }
}
```

---

## 10. Access Control Reference

### Helper Functions (in views.py)

```python
def _user_role(user):
    """Get user's role"""
    if not user.is_authenticated:
        return "anonymous"
    return getattr(user.profile, "role", "user")

def _can_manage_services(user):
    """Check if user can create/edit/delete services"""
    return _user_role(user) in ["admin", "agent"]

def _has_agent_permissions(user):
    """Check if user has admin/agent permissions"""
    return _user_role(user) in ["admin", "agent"]
```

### Permission Matrix

| Action | Admin | Agent | User |
|--------|-------|-------|------|
| View Dashboard | ✓ | ✓ | ✓ |
| Create Service | ✓ | ✓ | ✗ |
| Edit Any Service | ✓ | ✓ | ✗ |
| Delete Any Service | ✓ | ✓ | ✗ |
| View Users | ✓ | ✗ | ✗ |
| Edit User Role | ✓ | ✗ | ✗ |
| Create Page | ✓ | ✓ | ✗ |

---

## 11. Database Queries Used

### In dashboard()

```python
# Get all services
Service.objects.all().order_by("-created_at")

# Get all pages
DynamicPage.objects.all().order_by("name")

# Filter services by name
services.filter(name__icontains=search_query)

# Count total users
User.objects.count()

# Count agents
User.objects.filter(profile__role="agent").count()

# Get all users
User.objects.all().order_by("-date_joined")

# Count user's services
Service.objects.filter(created_by=request.user)
```

### In service_detail()

```python
# Get single service
get_object_or_404(Service, id=service_id)

# Get related services
Service.objects.all().order_by("-created_at")[:6]
```

**Performance Note:** All queries are simple and efficient. Consider caching if you have >1000 services.

---

## 12. Testing Code Snippets

### Create Test User

```python
from django.contrib.auth.models import User

# Create user
user = User.objects.create_user('testuser', 'test@example.com', 'pass123')

# Set role to agent
user.profile.role = 'agent'
user.profile.save()

# Or admin
user.profile.role = 'admin'
user.profile.save()
```

### Create Test Service

```python
from core.models import Service
from django.contrib.auth.models import User

user = User.objects.first()
service = Service.objects.create(
    name="Tax Filing",
    charges=500,
    documents_required="PAN, Aadhar",
    tutorial_link="https://example.com/tutorial",
    apply_link="https://example.com/apply",
    created_by=user
)
```

---

## 13. Debugging Tips

### Check Template Rendering

```python
# In views.py
print(f"Role: {role}")
print(f"Services: {services.count()}")
print(f"Can manage: {_can_manage_services(request.user)}")
```

### Check URL Reverse

```python
# In Python shell
from django.urls import reverse
print(reverse('service_detail', args=[1]))
# Output: /services/1/
```

### Check Permissions

```python
# In views.py
print(f"User role: {_user_role(request.user)}")
print(f"Can manage: {_can_manage_services(request.user)}")
print(f"Is admin/agent: {_has_agent_permissions(request.user)}")
```

---

## 14. Common Customizations

### Change Card Layout

In `unified_dashboard.html`, change:
```css
.service-cards-container {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));  /* Current */
    /* Change to: */
    grid-template-columns: repeat(2, 1fr);  /* 2 columns */
    grid-template-columns: repeat(4, 1fr);  /* 4 columns */
}
```

### Add More Statistics

In `unified_dashboard.html`:
```html
<div class="stat-card admin">
    <div class="stat-label">New Stat</div>
    <div class="stat-value">{{ new_stat_value }}</div>
</div>
```

In `views.py`, add to context:
```python
context['new_stat_value'] = calculated_value
```

### Customize Colors

In template CSS, change gradient:
```css
.service-card-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    /* Change to your colors */
}
```

---

## Summary

**Total Changes:**
- ✅ 1 new view (service_detail)
- ✅ 1 updated view (dashboard)
- ✅ 1 new URL route
- ✅ 2 new templates
- ✅ 300+ lines of new code
- ✅ Responsive design
- ✅ Real-time search/filter
- ✅ Proper access control

**No Breaking Changes:**
- All existing URLs still work
- All existing data preserved
- Backward compatible

---

**Created:** April 8, 2026  
**Last Updated:** Implementation Reference Complete
