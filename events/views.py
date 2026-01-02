# API endpoint for event details (used by event_detail.html)
from rest_framework.decorators import api_view
from .serializers import EventSerializer
@api_view(['GET'])
def event_detail_api(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    serializer = EventSerializer(event)
    return Response(serializer.data)
# API endpoint for events_api (used in api_urls.py)
from rest_framework.decorators import api_view
from rest_framework.response import Response
@api_view(['GET'])
def events_api(request):
    return Response({'detail': 'events_api stub'})
from django.shortcuts import render, get_object_or_404
from .models import Event, EventCategory

# --------------------------
# Pages HTML
# --------------------------

def events_list(request):
    """Liste des événements (page HTML)"""
    events = Event.objects.all().order_by('date')
    return render(request, "events_list.html", {"events": events})

def event_detail(request, event_id):
    """Détail d'un événement (page HTML)"""
    event = get_object_or_404(Event, id=event_id)
    return render(request, "event_detail.html", {"event": event, "event_id": event_id})

def bi_public(request):
    """Page BI publique (HTML)"""
    return render(request, "bi_public.html")

def bi_data_public(request):
    """Données publiques pour la BI (JSON ou HTML selon besoin)"""
    # Example: return empty JSON, adapt as needed
    from django.http import JsonResponse
    return JsonResponse({"status": "success", "data": []})

def categories(request):
    return render(request, "categories.html")

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

def cgu(request):
    return render(request, "cgu.html")

# Missing views for urls.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def index(request):
    """Page d'accueil protégée"""
    if not request.user.is_authenticated:
        return redirect('/accounts/login/?next=/')
    return render(request, "index.html")

def register_page(request):
    """Page d'inscription"""
    return render(request, "register.html")

# --------------------------
# API Views (DRF)
# --------------------------
from rest_framework import viewsets, generics, views, status
from rest_framework.response import Response
from .models import Event, EventCategory, Location, Ticket, Payment, UserInterest, ParticipationHistory
from .serializers import EventSerializer, RegisterSerializer, EventCategorySerializer, LocationSerializer, TicketSerializer

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = Event.objects.all()
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class BookTicketAPI(views.APIView):
    def post(self, request):
        return Response({'detail': 'BookTicketAPI stub'}, status=status.HTTP_200_OK)

class ScanTicketAPI(views.APIView):
    def post(self, request):
        return Response({'detail': 'ScanTicketAPI stub'}, status=status.HTTP_200_OK)

class RecommendationsAPI(views.APIView):
    def get(self, request, user_id):
        return Response({'detail': 'RecommendationsAPI stub', 'user_id': user_id}, status=status.HTTP_200_OK)

class CategoryList(generics.ListAPIView):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'categories': serializer.data})

class LocationList(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class PaymentsWebhookAPI(views.APIView):
    def post(self, request):
        return Response({'detail': 'PaymentsWebhookAPI stub'}, status=status.HTTP_200_OK)

class StatsAPI(views.APIView):
    def get(self, request):
        return Response({'detail': 'StatsAPI stub'}, status=status.HTTP_200_OK)

class PaymentCreateAPI(views.APIView):
    def post(self, request):
        return Response({'detail': 'PaymentCreateAPI stub'}, status=status.HTTP_200_OK)

class PaymentConfirmAPI(views.APIView):
    def post(self, request):
        return Response({'detail': 'PaymentConfirmAPI stub'}, status=status.HTTP_200_OK)
