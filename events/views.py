from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from .models import Event, Ticket, EventCategory, Location, Payment, User, TransactionLog
from .serializers import EventSerializer, RegisterSerializer, EventCategorySerializer, LocationSerializer, TicketSerializer
from .utils_qr import generate_qr_for_ticket
import uuid
import json
from django.http import JsonResponse
from django.db.models import F
from django.db.models.functions import TruncDay

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('date')
    serializer_class = EventSerializer

class CategoryList(generics.ListAPIView):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer

class LocationList(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class BookTicketAPI(APIView):
    """Simule la création d'une session de paiement et crée une Payment (paid=False).
    Pour la demo, on marque paid=True directement et on crée le ticket.
    POST { user_id, event_id }
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        event_id = request.data.get('event_id')
        if not event_id:
            return Response({'detail':'event_id required'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if not user or not user.is_authenticated:
            return Response({'detail':'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        event = get_object_or_404(Event, pk=event_id)
        # capacity check
        tickets_sold = event.tickets.count()
        if event.capacity and tickets_sold >= event.capacity:
            return Response({'detail':'Event full'}, status=status.HTTP_400_BAD_REQUEST)
        # create ticket and payment (simulate paid)
        ref = str(uuid.uuid4()).replace('-','')[:12]
        ticket = Ticket.objects.create(user=user, event=event, reference=ref)
        payment = Payment.objects.create(ticket=ticket, amount=event.price, paid=True)
        # generate QR
        generate_qr_for_ticket(ticket)
        return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)

class ScanTicketAPI(APIView):
    def post(self, request):
        ref = request.data.get('reference')
        if not ref:
            return Response({'detail':'reference required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            ticket = Ticket.objects.get(reference=ref)
        except Ticket.DoesNotExist:
            return Response({'detail':'not found'}, status=status.HTTP_404_NOT_FOUND)
        if ticket.status != 'valid':
            return Response({'detail':'ticket not valid'}, status=status.HTTP_400_BAD_REQUEST)
        ticket.status = 'used'
        ticket.save()
        return Response({'detail':'ticket scanned', 'ticket': TicketSerializer(ticket).data})

class RecommendationsAPI(APIView):
    """Content-based simple: recommend events sharing categories with user's history/interests"""
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        # Collect user signals: interests, history categories, tickets categories
        interest_names = list(user.interests.values_list('name', flat=True))
        interest_names = [s.lower() for s in interest_names if s]

        ticket_cat_ids = list(user.tickets.select_related('event__category').values_list('event__category__id', flat=True))
        history_cat_ids = list(user.history.select_related('event__category').values_list('event__category__id', flat=True))
        preferred_cat_ids = set([c for c in (ticket_cat_ids + history_cat_ids) if c])

        # Candidate pool: upcoming events (future) and recent ones, excluding events user already has tickets for
        now = timezone.now()
        candidates = list(Event.objects.filter(date__gte=now).exclude(tickets__user=user).select_related('category','location'))

        # Score each event by matching category and interest keywords
        scored = []
        for ev in candidates:
            score = 0
            # category match
            if ev.category and ev.category.id in preferred_cat_ids:
                score += 5
            # interest-name matches against category name, title or description
            cname = ev.category.name.lower() if ev.category and ev.category.name else ''
            title = (ev.title or '').lower()
            desc = (ev.description or '').lower()
            for iname in interest_names:
                if iname in cname:
                    score += 4
                if iname in title:
                    score += 3
                if iname in desc:
                    score += 2
            # small boost for events created by same organizer as user's past events
            try:
                # if user had tickets from same creator
                past_creators = set(user.tickets.select_related('event__created_by').values_list('event__created_by', flat=True))
                if ev.created_by and ev.created_by.id in past_creators:
                    score += 1
            except Exception:
                pass
            scored.append((score, ev))

        # sort by score desc, then date asc
        scored.sort(key=lambda x: (-x[0], x[1].date if x[1].date else timezone.now()))
        top_events = [ev for score, ev in scored if score > 0][:10]
        # if no positive score, fallback to upcoming events
        if not top_events:
            top_events = list(Event.objects.filter(date__gte=now).exclude(tickets__user=user).order_by('date')[:10])

        return Response(EventSerializer(top_events, many=True).data)

class PaymentsWebhookAPI(APIView):
    """Endpoint demo to accept webhook payload and finalize payment -> create ticket if needed"""
    def post(self, request):
        payload = request.data
        # Log payload
        TransactionLog.objects.create(payment=None, payload=json.dumps(payload))
        # For demo assume payload contains { 'reference': '...', 'paid': True, 'user_id': X, 'event_id': Y }
        ref = payload.get('reference')
        paid = payload.get('paid', False)
        user_id = payload.get('user_id')
        event_id = payload.get('event_id')
        if not paid:
            return Response({'detail':'not paid'}, status=status.HTTP_400_BAD_REQUEST)
        # create ticket
        try:
            user = User.objects.get(pk=user_id)
            from .models import Event, Ticket, Payment
            event = Event.objects.get(pk=event_id)
            newref = ref or str(uuid.uuid4()).replace('-','')[:12]
            ticket = Ticket.objects.create(user=user, event=event, reference=newref)
            payment = Payment.objects.create(ticket=ticket, amount=event.price, paid=True)
            generate_qr_for_ticket(ticket)
            return Response({'detail':'ticket created', 'reference': ticket.reference})
        except Exception as e:
            return Response({'detail':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentCreateAPI(APIView):
    """Create a Payment record (paid=False) and return payment info for client to proceed to payment provider.
    POST { event_id }
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        event_id = request.data.get('event_id')
        if not event_id:
            return Response({'detail':'event_id required'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        event = get_object_or_404(Event, pk=event_id)
        # quantity: number of tickets user intends to buy
        try:
            quantity = int(request.data.get('quantity', 1))
        except (ValueError, TypeError):
            return Response({'detail':'quantity must be an integer'}, status=status.HTTP_400_BAD_REQUEST)
        if quantity < 1 or quantity > 5:
            return Response({'detail':'quantity must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)

        # per-user limit: cannot own more than 5 tickets per event
        already_owned = Ticket.objects.filter(user=user, event=event).count()
        if already_owned + quantity > 5:
            return Response({'detail':f'You already own {already_owned} tickets for this event. Maximum per user is 5.'}, status=status.HTTP_400_BAD_REQUEST)

        tickets_sold = event.tickets.count()
        remaining = (event.capacity - tickets_sold) if event.capacity else None
        if remaining is not None and remaining < quantity:
            return Response({'detail':'Not enough seats available'}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = event.price * quantity
        # create a placeholder payment representing this purchase intent
        payment = Payment.objects.create(ticket=None, amount=total_amount, paid=False, provider_session=str(uuid.uuid4()))
        return Response({'payment_id': payment.id, 'amount': str(payment.amount), 'provider_session': payment.provider_session, 'quantity': quantity})


class PaymentConfirmAPI(APIView):
    """Confirm a payment (simulate provider success) and create the Ticket + QR code.
    POST { payment_id }
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        payment_id = request.data.get('payment_id')
        if not payment_id:
            return Response({'detail':'payment_id required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            payment = Payment.objects.get(pk=payment_id)
        except Payment.DoesNotExist:
            return Response({'detail':'payment not found'}, status=status.HTTP_404_NOT_FOUND)
        if payment.paid:
            return Response({'detail':'payment already confirmed'}, status=status.HTTP_400_BAD_REQUEST)

        # optional 'no_card_ref' for 'paiement sans carte' (26 digits)
        no_card_ref = request.data.get('no_card_ref')
        if no_card_ref:
            # normalize to digits only and validate length
            digits = ''.join([c for c in str(no_card_ref) if c.isdigit()])
            if len(digits) != 26:
                return Response({'detail':'no_card_ref must contain exactly 26 digits'}, status=status.HTTP_400_BAD_REQUEST)
            no_card_ref = digits

        # require event_id and quantity to be explicit for confirmation
        event_id = request.data.get('event_id')
        try:
            quantity = int(request.data.get('quantity', 1))
        except (ValueError, TypeError):
            return Response({'detail':'quantity must be an integer'}, status=status.HTTP_400_BAD_REQUEST)
        if not event_id:
            return Response({'detail':'event_id required to confirm payment'}, status=status.HTTP_400_BAD_REQUEST)
        if quantity < 1 or quantity > 5:
            return Response({'detail':'quantity must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)

        event = get_object_or_404(Event, pk=event_id)
        user = request.user

        # re-check limits (defensive)
        already_owned = Ticket.objects.filter(user=user, event=event).count()
        if already_owned + quantity > 5:
            return Response({'detail':f'You already own {already_owned} tickets for this event. Maximum per user is 5.'}, status=status.HTTP_400_BAD_REQUEST)
        tickets_sold = event.tickets.count()
        remaining = (event.capacity - tickets_sold) if event.capacity else None
        if remaining is not None and remaining < quantity:
            return Response({'detail':'Not enough seats available'}, status=status.HTTP_400_BAD_REQUEST)

        # Determine next seat numbers (numeric). Use existing numeric seat_number values if any.
        existing_seats = event.tickets.exclude(seat_number__isnull=True).values_list('seat_number', flat=True)
        numeric = []
        for s in existing_seats:
            try:
                numeric.append(int(s))
            except Exception:
                continue
        next_seat = (max(numeric) + 1) if numeric else 1

        created = []
        for i in range(quantity):
            ref = str(uuid.uuid4()).replace('-','')[:12]
            seat = str(next_seat + i)
            ticket = Ticket.objects.create(user=user, event=event, reference=ref, seat_number=seat)
            # create payment per ticket (simpler model compatibility)
            Payment.objects.create(ticket=ticket, amount=event.price, paid=True)
            generate_qr_for_ticket(ticket)
            created.append(ticket)

        # mark the placeholder payment as paid and attach to the first ticket, then leave others as separate payments
        payment.paid = True
        if created:
            payment.ticket = created[0]
        payment.save()

        # Log transaction payload including optional no_card_ref
        try:
            payload = {'payment_id': payment.id, 'user_id': user.id, 'event_id': event.id, 'quantity': quantity}
            if no_card_ref:
                payload['no_card_ref'] = no_card_ref
            TransactionLog.objects.create(payment=payment, payload=json.dumps(payload))
        except Exception:
            pass

        return Response(TicketSerializer(created, many=True).data, status=status.HTTP_201_CREATED)

class StatsAPI(APIView):
    def get(self, request):
        total_tickets = Ticket.objects.count()
        revenue = Payment.objects.filter(paid=True).aggregate(total=Sum('amount'))['total'] or 0
        top_events = Event.objects.annotate(sold=Count('tickets')).order_by('-sold')[:5]
        top = [{'id':e.id,'title':e.title,'sold':e.sold} for e in top_events]
        return Response({'total_tickets': total_tickets, 'revenue': revenue, 'top_events': top})


@login_required
def profile_view(request):
    user = request.user
    # upcoming tickets
    now = timezone.now()
    upcoming_tickets = user.tickets.select_related('event').filter(event__date__gte=now)
    past_tickets = user.tickets.select_related('event').filter(event__date__lt=now)
    interests = user.interests.all()
    history = user.history.select_related('event').order_by('-attended_at')
    return render(request, 'registration/profile.html', {
        'user_obj': user,
        'upcoming_tickets': upcoming_tickets,
        'past_tickets': past_tickets,
        'interests': interests,
        'history': history,
    })


def bi_public(request):
    """Page publique qui affiche le dashboard BI (template standalone).
    Utilise `events/templates/bi_public.html`.
    """
    return render(request, 'bi_public.html')


def bi_data_public(request):
    """Public JSON endpoint returning BI datasets for the public page.
    Mirrors the data structure returned by the admin `bi_data` view but without admin restriction.
    """
    start = request.GET.get('start')
    end = request.GET.get('end')
    now = timezone.now()
    if start:
        try:
            start_dt = timezone.datetime.fromisoformat(start)
        except Exception:
            start_dt = now - datetime.timedelta(days=90)
    else:
        start_dt = now - datetime.timedelta(days=90)
    if end:
        try:
            end_dt = timezone.datetime.fromisoformat(end)
        except Exception:
            end_dt = now
    else:
        end_dt = now

    # Occupancy: tickets sold per event (last 10 events)
    events_qs = Event.objects.order_by('-date')[:10]
    occupancy = []
    for ev in events_qs:
        sold = Ticket.objects.filter(event=ev).count()
        occupancy.append({'event': ev.title, 'capacity': ev.capacity or 0, 'sold': sold})

    # Sales by category
    sales_cat = (
        Ticket.objects.values(category_name=F('event__category__name'))
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    sales_by_category = [{'category': s['category_name'] or 'Uncategorized', 'count': s['count']} for s in sales_cat]

    # Top events
    top_events_qs = (
        Ticket.objects.values(event_title=F('event__title'))
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    top_events = [{'event': t['event_title'] or 'Untitled', 'count': t['count']} for t in top_events_qs]

    # Sales by location
    sales_loc_qs = (
        Ticket.objects.values(location_name=F('event__location__name'))
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    sales_by_location = [{'location': s['location_name'] or 'Unknown', 'count': s['count']} for s in sales_loc_qs]

    # Daily sales totals
    daily = (
        Payment.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt, paid=True)
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(total=Sum('amount'))
        .order_by('day')
    )
    daily_sales = [{'day': p['day'].strftime('%Y-%m-%d'), 'total': float(p['total'] or 0)} for p in daily]

    return JsonResponse({
        'occupancy': occupancy,
        'sales_by_category': sales_by_category,
        'daily_sales': daily_sales,
        'top_events': top_events,
        'sales_by_location': sales_by_location,
    })
