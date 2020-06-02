#!/usr/bin/env python3

import os
import requests
import sys

con = "stevegttest12020"
key = os.environ['SCHED_API_KEY']

# add
notes_url = requests.utils.quote("http://asddksf.salkfdj/kjdsaflksjflksadfj")
url = "https://%s.sched.com/api/session/add?api_key=%s&session_key=kn1&name=Opening+Keynote&session_start=2020-07-01+10:00&session_end=2020-07-01+12:15&session_type=keynote&venue=Center+Hall&notes_url=%s" % (con, key, notes_url)
# res = requests.get(url=url)
print(res)

# modify
# https://your_conference.sched.com/api/session/mod?api_key=XXX&session_key=1&venue=Main+Auditorium
sk = "1"
venue = "Room C"
notes_url = requests.utils.quote("http://asddksf.salkfdj/kjdsaflksjflksadfj")
url = "https://%s.sched.com/api/session/mod?api_key=%s&session_key=%s&venue=%s&notes_url=%s" % (con, key, sk, venue, notes_url)
# https://your_conference.sched.com/api/session/mod?api_key=XXX&session_key=1&venue=Main+Auditorium
res = requests.get(url=url)
print(res)


# list
# https://stevegttest12020.sched.com/api/session/list?api_key=XXX&format=json&custom_data=Y
url = "https://%s.sched.com/api/session/list?api_key=%s&format=json&custom_data=Y" % (con, key)
res = requests.get(url=url)
js = res.json()
print(js)


