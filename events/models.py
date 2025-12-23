from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    bio = models.TextField(blank=True, null=True)

class UserInterest(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='interests')
    name = models.CharField(max_length=100)
    def __str__(self): return f"{self.user.username} - {self.name}"

class EventCategory(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    def __str__(self): return self.name

class Location(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(default=0)
    def __str__(self): return self.name

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, related_name='events')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='events')
    date = models.DateTimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    capacity = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title

class Ticket(models.Model):
    STATUS_CHOICES = [('valid','valid'),('used','used'),('expired','expired')]
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='tickets')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    reference = models.CharField(max_length=120, unique=True)
    seat_number = models.CharField(max_length=20, null=True, blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='valid')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.reference} - {self.event.title}"

class Payment(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    paid = models.BooleanField(default=False)
    provider_session = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class TransactionLog(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='logs')
    payload = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class ParticipationHistory(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='history')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    attended_at = models.DateTimeField(null=True, blank=True)
    def __str__(self): return f"{self.user.username} - {self.event.title}"
