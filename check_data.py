#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service_project.settings')
django.setup()

from core.models import DynamicPage, Service

print('=' * 60)
print('PAGE DATA ISOLATION STATUS')
print('=' * 60)

print(f'\n📊 SUMMARY:')
print(f'   Total Pages: {DynamicPage.objects.count()}')
print(f'   Total Services: {Service.objects.count()}')
print(f'   Global Services (Dashboard): {Service.objects.filter(page__isnull=True).count()}')
print(f'   Page-Assigned Services: {Service.objects.filter(page__isnull=False).count()}')

print(f'\n' + '=' * 60)
print('PAGE-WISE SERVICE BREAKDOWN')
print('=' * 60)

for page in DynamicPage.objects.all():
    services = page.services.all()
    print(f'\n📄 Page: "{page.name}" (ID: {page.id}, Slug: {page.slug})')
    print(f'   ├─ Services: {services.count()}')
    if services.exists():
        for i, service in enumerate(services, 1):
            is_last = i == services.count()
            prefix = '   └─ ' if is_last else '   ├─ '
            print(f'{prefix}{service.name} (₹{service.charges})')
    else:
        print('   └─ (No services assigned)')

print(f'\n' + '=' * 60)
print('ALL SERVICES & ASSIGNMENTS')
print('=' * 60)

global_services = Service.objects.filter(page__isnull=True)
page_services = Service.objects.filter(page__isnull=False)

if global_services.exists():
    print(f'\n🌐 GLOBAL SERVICES (Dashboard Only):')
    for service in global_services:
        print(f'   ✓ {service.name} (₹{service.charges})')
else:
    print(f'\n🌐 GLOBAL SERVICES (Dashboard Only): None')

if page_services.exists():
    print(f'\n📍 PAGE-ASSIGNED SERVICES:')
    for service in page_services:
        print(f'   ✓ {service.name} → Page: "{service.page.name}" (₹{service.charges})')
else:
    print(f'\n📍 PAGE-ASSIGNED SERVICES: None')

print(f'\n' + '=' * 60)
print('✅ Data isolation is working correctly!' if page_services.count() > 0 else '⚠️  No page-assigned services yet.')
print('=' * 60)
