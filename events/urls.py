from django.urls import path
from . import views  # toutes les vues sont dans views.py

urlpatterns = [
    path('', views.index, name='index'),  # page d'accueil
    path('events/', views.events_list, name='events-list'),  # liste des events (HTML)
    path('events/<int:event_id>/', views.event_detail, name='event-detail'),  # détail HTML
    path('categories/', views.categories, name='categories-page'),  # page catégories
    path('register/', views.register_page, name='register-page'),  # page register
    path('bi/', views.bi_public, name='bi-public'),  # page BI publique
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('cgu/', views.cgu, name='cgu'),
]
