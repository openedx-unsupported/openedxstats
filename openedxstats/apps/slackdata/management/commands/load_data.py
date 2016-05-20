import datetime
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from slackdata.models import SlackUser, MessageCountByDay

class Command(BaseCommand):
    help = 'Load data from api to db'

    def handle(self, *args, **options):
        SlackUser.populate_from_api()
        MessageCountByDay.populate_from_api(after_date=\
                                            datetime.strptime(\
                                                              '2016-04-25',\
                                                              '%Y-%m-%d'),\
                                            force=True,\
                                            )

