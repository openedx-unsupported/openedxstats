from rest_framework import serializers

from openedxstats.apps.slackdata.models import SlackUser

class SlackUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SlackUser
        fields = ('id', 'name', 'email', 'deleted')

class UserCountSerializer(serializers.Serializer):
    count = serializers.IntegerField(read_only=True)
    name = serializers.SerializerMethodField('get_user_name')

    def get_user_name(self, obj):
        return obj['user__name']
