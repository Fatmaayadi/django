from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, RegisterView, BookTicketAPI, ScanTicketAPI, RecommendationsAPI, CategoryList, LocationList, PaymentsWebhookAPI, StatsAPI
from .views import PaymentCreateAPI, PaymentConfirmAPI
from . import views
router = DefaultRouter()
router.register(r'events', EventViewSet, basename='events')

urlpatterns = [
    path('', include(router.urls)),
    path('users/register/', RegisterView.as_view(), name='register'),
    path('tickets/book/', BookTicketAPI.as_view(), name='book-ticket'),
    path('tickets/scan/', ScanTicketAPI.as_view(), name='scan-ticket'),
    path('recommendations/<int:user_id>/', RecommendationsAPI.as_view(), name='recommendations'),
    path('categories/', CategoryList.as_view()),
    path('locations/', LocationList.as_view()),
    path('payments/webhook/', PaymentsWebhookAPI.as_view(), name='payments-webhook'),
    path('payments/create/', PaymentCreateAPI.as_view(), name='payments-create'),
    path('payments/confirm/', PaymentConfirmAPI.as_view(), name='payments-confirm'),
    path('stats/', StatsAPI.as_view(), name='stats'),
    path('events/', views.events_api, name='api-events'),
    path('events/<int:event_id>/', views.event_detail_api, name='api-event-detail'),
    path('categories/', CategoryList.as_view(), name='api-categories'),
]
