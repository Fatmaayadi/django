from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from events.views import profile_view
from events import admin as events_admin
from events import views as events_views

urlpatterns = [
    # Friendly dashboard URLs -> redirect to admin index (where custom charts live)
    path('admin/dashboard/', RedirectView.as_view(url='/admin/')),
    path('admin//dashboard/', RedirectView.as_view(url='/admin/')),
    # admin stats data endpoint used by custom admin dashboard (place before admin.urls)
    path('admin/stats-data/', admin.site.admin_view(events_admin.admin_stats_data), name='admin-stats-data'),
    # BI pages
    path('admin/bi-data/', admin.site.admin_view(events_admin.bi_data), name='admin-bi-data'),
    path('admin/bi/', admin.site.admin_view(events_admin.bi_view), name='admin-bi'),
    # Public BI page (standalone)
    path('bi/', events_views.bi_public, name='bi-public'),
    # Public BI JSON data (used by /bi/)
    path('bi/data/', events_views.bi_data_public, name='bi-data-public'),
    # Main admin (catch-all for admin app)
    path('admin/', admin.site.urls),
    path('accounts/profile/', profile_view, name='account-profile'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include('events.api_urls')),
    path('', include('events.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
