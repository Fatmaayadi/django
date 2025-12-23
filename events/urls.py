from django.urls import path
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def event_detail(request, pk):
    return render(request, 'event_detail.html', {'event_id': pk})

def register_page(request):
    return render(request, 'register.html')

def categories_page(request):
    # page simple; front-end will fetch categories via API if available
    return render(request, 'categories.html')

urlpatterns = [
    path('events/', index, name='events-list'),
    path('', index, name='index'),
    path('events/<int:pk>/', event_detail, name='event-detail'),
    path('categories/', categories_page, name='categories-page'),
    path('register/', register_page, name='register-page'),
]
