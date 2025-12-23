from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import EventCategory, Location, Event, Ticket, Payment, UserInterest, ParticipationHistory

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    interests = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    class Meta:
        model = User
        fields = ('id','username','email','password','first_name','last_name','interests')
    def create(self, validated_data):
        interests = validated_data.pop('interests', [])
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            first_name=validated_data.get('first_name',''),
            last_name=validated_data.get('last_name',''),
        )
        for name in interests:
            UserInterest.objects.create(user=user, name=name)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','email','first_name','last_name')

class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    category = EventCategorySerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    class Meta:
        model = Event
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = Ticket
        fields = '__all__'
