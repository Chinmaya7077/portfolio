from django.contrib import admin
from django.urls import path
from core import views as core_views
from projects import views as project_views
from blog import views as blog_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.home, name='home'),
    path('about/', core_views.about, name='about'),
    path('contact/', core_views.contact, name='contact'),
    path('projects/', project_views.project_list, name='project_list'),
    path('projects/<slug:slug>/', project_views.project_detail, name='project_detail'),
    path('blog/', blog_views.post_list, name='blog_list'),
    path('blog/<slug:slug>/', blog_views.post_detail, name='blog_detail'),
]
