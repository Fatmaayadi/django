from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html
from .models import User, UserInterest, EventCategory, Location, Event, Ticket, Payment, TransactionLog, ParticipationHistory

from django.http import JsonResponse
from django.db.models import Count, Sum
from django.utils import timezone
import datetime
from django.shortcuts import render
from django.db.models import F
from django.db import models


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'image_tag')
	readonly_fields = ('image_tag',)
	search_fields = ('name',)

	def image_tag(self, obj):
		if obj.image:
			return format_html('<img src="{}" style="width:80px;height:auto;border-radius:6px" />', obj.image.url)
		return '-'
	image_tag.short_description = 'Image'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
	list_display = ('name', 'capacity')
	search_fields = ('name',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
	list_display = ('title', 'category', 'location', 'date', 'price', 'capacity', 'created_by')
	list_filter = ('category', 'location', 'date')
	search_fields = ('title', 'description')
	readonly_fields = ('created_at',)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
	list_display = ('reference', 'user', 'event', 'seat_number', 'status', 'created_at')
	list_filter = ('status', 'event')
	search_fields = ('reference', 'user__username', 'event__title')
	readonly_fields = ('created_at', 'qr_preview')

	def qr_preview(self, obj):
		if obj.qr_code:
			return format_html('<img src="{}" style="width:120px;height:auto" />', obj.qr_code.url)
		return '-'
	qr_preview.short_description = 'QR Code'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
	list_display = ('id', 'ticket_link', 'amount', 'paid', 'created_at')
	list_filter = ('paid',)
	search_fields = ('ticket__reference',)
	readonly_fields = ('created_at',)

	def ticket_link(self, obj):
		if obj.ticket:
			return format_html('<a href="/admin/events/ticket/{}/change/">{}</a>', obj.ticket.id, obj.ticket.reference)
		return '-'
	ticket_link.short_description = 'Ticket'


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
	list_display = ('id', 'payment', 'created_at')
	search_fields = ('payment__id',)


@admin.register(ParticipationHistory)
class ParticipationHistoryAdmin(admin.ModelAdmin):
	list_display = ('user', 'event', 'attended_at')
	search_fields = ('user__username', 'event__title')


@admin.register(User)
class CustomUserAdmin(DjangoUserAdmin):
	fieldsets = DjangoUserAdmin.fieldsets + (
		('Extra', {'fields': ('bio',)}),
	)
	list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')


admin.site.register(UserInterest)

# Use a custom admin index template (will be created under templates/admin/custom_index.html)
admin.site.index_template = 'admin/custom_index.html'


def admin_stats_data(request):
	# tickets per event
	tickets = (
		Ticket.objects.values('event__title')
		.annotate(count=Count('id'))
		.order_by('-count')[:20]
	)
	tickets_data = [{'event': t['event__title'] or 'Untitled', 'count': t['count']} for t in tickets]

	# payments sum per month (last 6 months)
	now = timezone.now()
	start = now - datetime.timedelta(days=180)
	payments = (
		Payment.objects.filter(created_at__gte=start)
		.annotate(month=models.functions.TruncMonth('created_at'))
		.values('month')
		.annotate(total=Sum('amount'))
		.order_by('month')
	)
	payments_data = [{'month': p['month'].strftime('%Y-%m'), 'total': float(p['total'] or 0)} for p in payments]

	return JsonResponse({'tickets': tickets_data, 'payments': payments_data})


def bi_data(request):
	"""Return JSON with multiple BI datasets: occupancy, sales by category, daily sales."""
	# date range params
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

	# Occupancy: tickets sold per event vs capacity (last 10 events by date)
	# include recent and upcoming events so occupancy is meaningful
	events_qs = (
		Event.objects.order_by('-date')[:10]
	)
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

	# Top events (tickets sold)
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
		.annotate(day=models.functions.TruncDay('created_at'))
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


def bi_view(request):
	return render(request, 'admin/bi_dashboard.html')
