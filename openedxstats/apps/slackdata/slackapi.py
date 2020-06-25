"""
Accessing select data from the Slack API
"""
from slacker import Slacker
from django.conf import settings

def get_users():
    slack_api = Slacker(settings.SLACK_API_TOKEN)
    response = slack_api.users.list()
    users_response = response.body['members']

    for user in users_response:
        name = user['name']
        deleted = False
        if 'email' in user['profile']:
            email = user['profile']['email']
        else:
            email = None
            deleted = True if user['deleted'] else False
        yield {'name': name, 'email': email, 'deleted': deleted}

def get_message_count_by_username(username, after_date, before_date=None):
    slack_api = Slacker(settings.SLACK_API_TOKEN)
    after_date = after_date.strftime('%Y-%m-%d')
    if(before_date is None):
        before_date = 'today'
    else:
        before_date = before_date.strftime('%Y-%m-%d')
    query_string = "from:@{user_name} after:{after_date} before:{before_date}".format(user_name=username,\
                                       after_date=after_date,\
                                       before_date=before_date)
    response = slack_api.search.messages(query=query_string)
    if response.body['ok'] is True:
        return response.body['messages']['total']
    else:
        return False
