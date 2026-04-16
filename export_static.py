"""
Export Django portfolio as static HTML files for Vercel deployment.
Run: python export_static.py
"""
import os
import sys
import shutil
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings')
django.setup()

from django.test import Client
from projects.models import Project
from blog.models import Post

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'dist')

# Clean output
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR)

client = Client()

# Pages to export
pages = {
    '/': 'index.html',
    '/projects/': 'projects/index.html',
    '/blog/': 'blog/index.html',
    '/about/': 'about/index.html',
    '/contact/': 'contact/index.html',
}

# Add project detail pages
for p in Project.objects.all():
    pages[f'/projects/{p.slug}/'] = f'projects/{p.slug}/index.html'

# Add blog post pages
for post in Post.objects.filter(published=True):
    pages[f'/blog/{post.slug}/'] = f'blog/{post.slug}/index.html'

# Export each page
for url, filepath in pages.items():
    response = client.get(url)
    if response.status_code == 200:
        full_path = os.path.join(OUTPUT_DIR, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        content = response.content.decode('utf-8')
        # Fix static file paths for Vercel (remove /static/ prefix, use relative)
        content = content.replace('/static/', '/static/')

        with open(full_path, 'w') as f:
            f.write(content)
        print(f'  Exported: {url} -> {filepath}')
    else:
        print(f'  FAILED: {url} (status {response.status_code})')

# Copy static files
static_src = os.path.join(os.path.dirname(__file__), 'static')
static_dst = os.path.join(OUTPUT_DIR, 'static')
shutil.copytree(static_src, static_dst)
print(f'  Copied static files')

print(f'\nDone! {len(pages)} pages exported to {OUTPUT_DIR}/')
print('Next: cd dist && vercel deploy')
