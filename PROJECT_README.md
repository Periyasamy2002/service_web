# ServiceHub - Role-Based Dashboard System

A modern, full-stack web application built with Django that provides role-based access control for Admin, Agent, and User roles with a responsive, animated UI.

## 🎯 Features

### User Roles & Access

#### 👑 Admin Dashboard
- **Full System Control**: Complete access to all features
- **User Management**: Create, view, edit, and manage all users
- **Service Management**: Create, edit, and delete services
- **Role Assignment**: Assign and modify user roles (Admin, Agent, User)
- **System Analytics**: View user statistics and service metrics

#### 💼 Agent Dashboard
- **Service Management**: Create and manage services
- **Service Browsing**: View all available services across the platform
- **Limited Access**: Cannot access admin controls or user management
- **Service Metrics**: View services created and track activities

#### 👤 User Dashboard
- **Service Browsing**: Explore all available services
- **Service Details**: View complete service information including documents required
- **Service Requests**: Apply for services through tutorial and apply links
- **Read-Only Access**: No creation or modification permissions

### Authentication System

#### Dual Login System
- **Admin-Only Login**: Separate secure login interface for administrators
- **User/Agent Login**: Combined login for regular users and agents
- **Role-Based Redirection**: Automatic redirect to appropriate dashboard based on role
- **Session Management**: Secure session handling with logout support

#### Security Features
- Password hashing using Django's built-in authentication
- CSRF protection on all forms
- Secure session cookies
- Login required decorators on protected views

### UI/UX Features

#### Modern Design
- **Glassmorphism Effects**: Semi-transparent cards with backdrop blur
- **Gradient Backgrounds**: Beautiful gradient color schemes
- **Smooth Animations**: Fade-in, slide-up, and hover animations
- **Responsive Layout**: Mobile (📱), Tablet (📱), and Desktop (🖥️) optimized

#### Navigation
- **Top Navigation Bar**: Display user info and quick logout
- **Search Bar**: Real-time service search in navbar
- **Sidebar Menu**: Role-based navigation menu
- **Dynamic Pages**: Custom dynamic pages integration

#### Service Display
- **Card-Based Layout**: Attractive grid layout for services
- **Search & Filter**: Search services in real-time
- **Service Details**: Comprehensive service information display
- **Documents List**: Clear list of required documents
- **Action Buttons**: Tutorial and Apply links for each service

#### Data Presentation
- **Statistics Cards**: Dashboard at-a-glance metrics
- **Data Tables**: Sortable tables with hover effects
- **Badges**: Role and status indication badges
- **Alerts**: Success, error, and warning message displays

## 🏗️ Project Structure

```
service_web/
├── core/
│   ├── migrations/          # Database migrations
│   ├── templates/
│   │   └── core/
│   │       ├── base.html                    # Main template with navbar
│   │       ├── admin_dashboard.html         # Admin-only dashboard
│   │       ├── agent_dashboard.html         # Agent-specific dashboard
│   │       ├── user_dashboard.html          # User-specific dashboard
│   │       ├── login.html                   # User/Agent login
│   │       ├── admin_agent_login.html       # Admin login page
│   │       ├── login_board.html             # Login type selection
│   │       ├── register.html                # User registration
│   │       ├── service_form.html            # Create/Edit service
│   │       ├── user_list.html               # User management list
│   │       ├── edit_user.html               # Edit user roles
│   │       ├── add_page.html                # Create dynamic pages
│   │       ├── dynamic_page.html            # View dynamic pages
│   │       └── delete_confirm.html          # Deletion confirmation
│   ├── templatetags/
│   │   └── custom_filters.py                # Custom template filters
│   ├── models.py                            # Database models
│   ├── views.py                             # View logic
│   ├── urls.py                              # URL routing
│   ├── forms.py                             # Form definitions
│   ├── signals.py                           # Django signals (Profile creation)
│   └── admin.py                             # Django admin config
├── service_project/
│   ├── settings.py                          # Django settings
│   ├── urls.py                              # Project URL config
│   └── wsgi.py                              # WSGI configuration
├── env/                                     # Python virtual environment
├── db.sqlite3                               # Database file
├── manage.py                                # Django management script
└── requirements.txt                         # Python dependencies
```

## 📦 Models

### Profile Model
```python
- user (OneToOneField) → Django User
- role (CharField) → "admin", "agent", or "user"
```

### Service Model
```python
- name (CharField)
- charges (DecimalField)
- documents_required (CharField)
- tutorial_link (URLField)
- apply_link (URLField)
- created_by (ForeignKey) → User
- created_at (DateTimeField)
```

### DynamicPage Model
```python
- name (CharField)
- slug (SlugField) - Auto-generated
- description (TextField)
- created_by (ForeignKey) → User
- created_at (DateTimeField)
```

## 🔐 Security & Role-Based Access Control

### View Decorators
- `@login_required`: Requires user to be authenticated
- Role checks via helper functions:
  - `_user_role(user)` → Returns user's role
  - `_can_manage_services(user)` → Check if Admin or Agent
  - `_has_agent_permissions(user)` → Check if Admin or Agent

### Permission Requirements
| Action | Admin | Agent | User |
|--------|:-----:|:-----:|:----:|
| View Dashboard | ✅ | ✅ | ✅ |
| View Services | ✅ | ✅ | ✅ |
| Create Services | ✅ | ✅ | ❌ |
| Edit Services | ✅ | ✅ | ❌ |
| Delete Services | ✅ | ✅ | ❌ |
| Manage Users | ✅ | ❌ | ❌ |
| Create Pages | ✅ | ✅ | ❌ |
| View User List | ✅ | ❌ | ❌ |

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone/Navigate to Project**
   ```bash
   cd service_web
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv env
   env\Scripts\activate  # Windows
   source env/bin/activate  # Mac/Linux
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create Superuser (Admin)**
   ```bash
   python manage.py createsuperuser
   # Follow the prompts to create admin account
   ```

6. **Create Test Data (Optional)**
   ```bash
   python manage.py shell
   >>> from django.contrib.auth.models import User
   >>> from core.models import Profile
   >>> 
   >>> # Create agent user
   >>> agent = User.objects.create_user('agent1', 'agent@example.com', 'password123')
   >>> agent.profile.role = 'agent'
   >>> agent.profile.save()
   >>> 
   >>> # Create regular user
   >>> user = User.objects.create_user('user1', 'user@example.com', 'password123')
   >>> # Profile role is 'user' by default
   >>> exit()
   ```

7. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Access Application**
   - Visit: `http://127.0.0.1:8000/`
   - Login Board: `http://127.0.0.1:8000/login-board/`
   - Admin Login: `http://127.0.0.1:8000/admin-login/`
   - Register: `http://127.0.0.1:8000/register/`

## 🎨 UI/UX Highlights

### Color Scheme
- **Primary**: #667eea (Purple) & #764ba2 (Violet)
- **Success**: #27ae60 (Green)
- **Danger**: #e74c3c (Red)
- **Warning**: #f39c12 (Orange)
- **Info**: #3498db (Blue)

### Animations
- **Slide Down**: Navbar entrance
- **Fade In**: Page content
- **Slide Up**: Cards and elements
- **Hover Effects**: All interactive elements
- **Smooth Transitions**: 0.3s ease animations

### Responsive Breakpoints
- **Desktop**: 1024px+ → Full sidebar
- **Tablet**: 768px - 1023px → Adjusted layout
- **Mobile**: < 768px → Collapsible sidebar

## 📝 Usage Examples

### Admin Workflow
1. Visit `/admin-login/`
2. Enter admin credentials
3. Access dashboard showing statistics
4. Manage users from "Manage Users" option
5. Create/Edit/Delete services
6. Add dynamic pages for navigation

### Agent Workflow
1. Visit `/login-board/` → Choose "Agent Login"
2. Enter agent credentials
3. View agent dashboard with service stats
4. Create new services using "Create Service"
5. View all services in card layout
6. Edit or delete own created services

### User Workflow
1. Visit `/login-board/` → Choose "User Login"
2. Enter user credentials (or register new account)
3. Browse available services
4. Search services using search bar
5. View service details and required documents
6. Apply for services using provided links

## 🔧 API Endpoints

### Authentication
- `GET/POST /login/` - User/Agent login
- `GET/POST /admin-login/` - Admin login
- `GET/POST /register/` - User registration
- `GET /logout/` - User logout
- `GET /login-board/` - Login type selector

### Dashboard
- `GET /` - Main dashboard (role-based routing)

### Services
- `GET /` - View services
- `POST /services/add/` - Create service
- `POST /services/<id>/edit/` - Edit service
- `POST /services/<id>/delete/` - Delete service

### Users (Admin Only)
- `GET /users/` - View all users
- `POST /users/<id>/edit/` - Edit user role

### Pages
- `POST /pages/add/` - Create dynamic page
- `GET /pages/<slug>/` - View dynamic page

## 🛠️ Customization

### Change Colors
Edit the `--primary-color` and other CSS variables in `base.html`:
```css
:root {
    --primary: #667eea;
    --secondary: #764ba2;
    --success: #27ae60;
    --danger: #e74c3c;
}
```

### Add New Roles
1. Update `Profile.ROLE_CHOICES` in `core/models.py`
2. Create new view functions with role checks
3. Create role-specific templates
4. Update sidebar navigation in `base.html`

### Customize Dashboard
Edit the dashboard templates:
- `admin_dashboard.html` → Add admin-specific widgets
- `agent_dashboard.html` → Add agent-specific features
- `user_dashboard.html` → Add user-specific content

## 📊 Database Schema

### Users Table
- Links to Profile (One-to-One)
- Contains: username, email, password, first_name, last_name, etc.

### Profile Table
- Links to User (One-to-One)
- Contains: role (admin/agent/user)

### Services Table
- Links to User via `created_by` (Many-to-One)
- Contains: name, charges, documents, links, timestamps

### DynamicPage Table
- Links to User via `created_by` (Many-to-One)
- Contains: name, slug, description, timestamps

## 🔒 Security Best Practices

✅ Implemented:
- Password hashing (Django's built-in)
- CSRF token protection
- Login required decorators
- Role-based access control
- SQL injection prevention (Django ORM)
- XSS protection (Django templates)

⚠️ Production Recommendations:
- Set `DEBUG = False` in production
- Use environment variables for SECRET_KEY
- Configure ALLOWED_HOSTS properly
- Use HTTPS only
- Set secure cookies: `SESSION_COOKIE_SECURE = True`
- Add rate limiting for login attempts
- Use a production database (PostgreSQL)

## 📱 Browser Compatibility
- Chrome/Edge 88+
- Firefox 85+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🤝 Contributing
1. Create feature branch: `git checkout -b feature/new-feature`
2. Commit changes: `git commit -am 'Add new feature'`
3. Push to branch: `git push origin feature/new-feature`
4. Create Pull Request

## 📄 License
This project is licensed under the MIT License.

## 👨‍💻 Author
Built with ❤️ for modern web applications.

## 📞 Support
For issues or questions, please contact the development team.

---

**Last Updated**: April 8, 2026
**Version**: 1.0.0
