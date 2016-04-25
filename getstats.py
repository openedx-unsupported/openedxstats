import operator
import os

from slacker import Slacker

slack = Slacker(os.getenv('SLACK_API_TOKEN'))

response = slack.users.list()

users = response.body['members']

nonedx_user_msg_count = {}
edx_user_msg_count = {}

for user in users:
    response = slack.search.messages(query='from:@' + user['name'] +\
                                     ' after:2016-04-21')
    print user['name'] + "\t" + str(response.body['messages']['total'])
    if user['profile'].has_key('email') and user['profile']['email'] != None and\
            user['profile']['email'].endswith('edx.org'):
        edx_user_msg_count[user['name']] = response.body['messages']['total']
    else:
        nonedx_user_msg_count[user['name']] = response.body['messages']['total']

top_edx_users = sorted(edx_user_msg_count.items(), key=operator.itemgetter(1), reverse=True)
top_nonedx_users = sorted(edx_user_msg_count.items(), key=operator.itemgetter(1), reverse=True)

print
print
print "-----------------Top edX Slackers----------------"
print '\n'.join(t[0] + "\t" + str(t[1]) for t in top_edx_users[:10])
