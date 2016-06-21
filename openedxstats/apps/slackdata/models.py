from __future__ import unicode_literals

from django.db import models
from datetime import datetime
from . import slackapi

# Create your models here.

class SlackUser(models.Model):
    """
    A model describing a user on Slack
    """

    name = models.CharField(unique=True, max_length=255)
    email = models.EmailField(null=True)
    deleted = models.BooleanField(default=False)

    @classmethod
    def populate_from_api(cls):
        for user in slackapi.get_users():
            (row, created) = SlackUser.objects.get_or_create(name=user['name'])
            row.email = user['email']
            row.deleted = True if user['deleted'] else False
            row.save()

class MessageCountByDay(models.Model):
    """
    A model recording how many messages each user posted each day
    """

    user = models.ForeignKey(SlackUser, on_delete=models.CASCADE)
    date = models.DateField()
    count = models.IntegerField(null=True)

    class Meta:
        unique_together = (('user', 'date'),)
        index_together = (('user', 'date'),)

    @classmethod
    def populate_from_api(cls, after_date, before_date=datetime.today(), force=False, username=None):
        if(not username):
            users = SlackUser.objects.all()
        else:
            users = [SlackUser.objects.get(name=username)]
        for user in users:
            d = after_date
            one_day = datetime.timedelta(days=1)
            while d <= before_date:
                (row, created) = MessageCountByDay.objects.get_or_create(user=user, date=d)
                if created or force:
                    count = slackapi.get_message_count_by_username(user.name, d, d + one_day)
                    if(count):
                        row.count = count
                        row.save()
                d += one_day


