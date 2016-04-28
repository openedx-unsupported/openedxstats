from rest_framework import serializers

from .models import SlackUser

class SlackUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SlackUser
        fields = ('id', 'name', 'email', 'deleted')
