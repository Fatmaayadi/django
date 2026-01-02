from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from events import views
from events import admin as events_admin
from events import views as events_views

urlpatterns = [
    # Redirects vers l’admin dashboard
    path('admin/dashboard/', RedirectView.as_view(url='/admin/')),
    path('admin//dashboard/', RedirectView.as_view(url='/admin/')),

    # Admin stats & BI (protégés par admin_view)
    path(
        'admin/stats-data/',
        admin.site.admin_view(events_admin.admin_stats_data),
        name='admin-stats-data'
    ),
    path(
        'admin/bi-data/',
        admin.site.admin_view(events_admin.bi_data),
        name='admin-bi-data'
    ),
    path(
        'admin/bi/',
        admin.site.admin_view(events_admin.bi_view),
        name='admin-bi'
    ),

    # BI public
    path('bi/', events_views.bi_public, name='bi-public'),
    path('bi/data/', events_views.bi_data_public, name='bi-data-public'),

    # Admin principal
    path('admin/', admin.site.urls),

    # Auth Django (login, logout, password reset, etc.)
    # Redirection standard pour profile
    path(
        'accounts/profile/',
        RedirectView.as_view(url='/'),
        name='account-profile'
    ),
    path('accounts/', include('django.contrib.auth.urls')),

    # API
    path('api/', include('events.api_urls')),

    # Frontend (events app)
    path('', include('events.urls')),
     path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('cgu/', views.cgu, name='cgu'),
    path('categories/', views.categories, name='categories'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
