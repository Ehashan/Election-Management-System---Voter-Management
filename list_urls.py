import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ems_project.settings')
django.setup()

from django.urls import get_resolver

def show_urls(urlpatterns, prefix=''):
    for pattern in urlpatterns:
        if hasattr(pattern, 'url_patterns'):
            # This is an included URLconf
            show_urls(pattern.url_patterns, prefix + str(pattern.pattern))
        else:
            # This is a regular URL pattern
            print(f"{prefix}{pattern.pattern}")

resolver = get_resolver()
print("=== All registered URLs ===")
show_urls(resolver.url_patterns)
