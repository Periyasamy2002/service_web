#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service_project.settings')
django.setup()

from core.models import DynamicPage, Service

print('\n' + '='*70)
print('TESTING PAGE DATA ISOLATION - ADD SERVICE TO SPECIFIC PAGE')
print('='*70)

# Get first page
page = DynamicPage.objects.first()
if not page:
    print('❌ No pages found! Create a page first.')
    exit()

print(f'\n📄 Selected Page: "{page.name}" (ID: {page.id})')

# Create a test service for this page
test_service = Service.objects.create(
    name='TEST SERVICE FOR ' + page.name.upper(),
    charges=999.99,
    documents_required='Test Document',
    page=page  # 🔑 ASSIGNED TO SPECIFIC PAGE
)

print(f'✅ Created Service: "{test_service.name}" and assigned to page "{page.name}"')

print('\n' + '-'*70)
print('CHECKING SERVICE VISIBILITY ACROSS PAGES')
print('-'*70)

# Check if service appears on its own page
own_page_services = page.services.filter(id=test_service.id)
print(f'\n1️⃣  Service on OWN page ("{page.name}"):')
if own_page_services.exists():
    print(f'   ✅ VISIBLE - Service found on {page.name}')
else:
    print(f'   ❌ NOT VISIBLE - Service NOT found on {page.name}')

# Check if service appears on other pages
other_pages = DynamicPage.objects.exclude(id=page.id)
print(f'\n2️⃣  Service on OTHER pages:')
for other_page in other_pages:
    services_on_other = other_page.services.filter(id=test_service.id)
    if services_on_other.exists():
        print(f'   ⚠️  LEAKED - Service found on {other_page.name} (WRONG!)')
    else:
        print(f'   ✅ ISOLATED - Service NOT on {other_page.name}')

# Check if service appears on dashboard (global services only)
global_services = Service.objects.filter(page__isnull=True, id=test_service.id)
print(f'\n3️⃣  Service on DASHBOARD (Global Services):')
if global_services.exists():
    print(f'   ⚠️  LEAKED - Service found on Dashboard (WRONG!)')
else:
    print(f'   ✅ ISOLATED - Service NOT on Dashboard')

print('\n' + '='*70)
if own_page_services.exists() and not global_services.exists() and not other_pages.filter(services__id=test_service.id).exists():
    print('✅ DATA ISOLATION IS WORKING PERFECTLY!')
else:
    print('❌ DATA ISOLATION HAS ISSUES - SEE ABOVE')
print('='*70 + '\n')
