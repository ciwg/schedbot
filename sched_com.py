#!/usr/bin/env python3

import os
import json
import re
import requests
import sys
import time
import tempfile

year = 2020
# con = "stevegttest12020"
con = "nomcon2020"
key = os.environ['SCHED_API_KEY']
# next_mcp_num = 69
next_mcp_num = 139

mcp_index_url = "https://script.google.com/a/t7a.org/macros/s/AKfycbx4RA9gKTs8feuWgiE2QMuu_xCgkp3sgldZJvecmMN9PmreW0ei/exec"

'''
# add
notes_url = requests.utils.quote("http://asddksf.salkfdj/kjdsaflksjflksadfj")
url = "https://%s.sched.com/api/session/add?api_key=%s&session_key=kn1&name=Opening+Keynote&session_start=2020-07-01+10:00&session_end=2020-07-01+12:15&session_type=keynote&venue=Center+Hall&notes_url=%s" % (con, key, notes_url)
# res = requests.get(url=url)
print(res)
'''
def list_sessions():
    # https://stevegttest12020.sched.com/api/session/list?api_key=XXX&format=json&custom_data=Y
    url = "https://%s.sched.com/api/session/list?api_key=%s&format=json&custom_data=Y" % (con, key)
    # print(url)
    res = requests.get(url=url)
    # print(res)
    fh = tempfile.NamedTemporaryFile(mode='w+b', prefix='sched', dir="/tmp/sched", delete=False)
    sessions = res.json()
    # pickle.dump(sessions, fh)
    fh.write(json.dumps(sessions).encode())
    fh.close()
    return sessions

def add_link(session, mcp_num):
    # https://your_conference.sched.com/api/session/mod?api_key=XXX&session_key=1&venue=Main+Auditorium
    print("===")
    sk = session['event_key']
    title = session['name']
    start = session['event_start']
    venue = session.get('venue', '')
    venue_id = session.get('venue_id', '')
    speakers = session.get('speakers', '')
    artists = session.get('artists', '')
    if len(speakers) == 0 and len(artists) > 0:
        speakers = artists
    if not venue_id:
        print("MISSING venue_id", start, title)
    if session.get("Session Notes URL"):
        print("skipping", start, title)
        return False
    filename = "mcp-%d-nomcon-%d-%s" % (mcp_num, year, title)
    filename = filename.lower()
    filename = re.sub('\W', '-', filename) 
    filename = re.sub('\-+', '-', filename) 
    filename = filename[:80]
    q = requests.utils.quote
    parms = "submit=create&session_year=%d&session_title=%s&session_filename=%s&session_date=%s&session_speakers=%s" % (
                year, q(title), filename, q(start), q(speakers))
    notes_url = q("%s?%s" % (mcp_index_url, parms))
    url = "https://%s.sched.com/api/session/mod?api_key=%s&session_key=%s&venue_id=%s&Session_Notes_URL=%s" % (
            con, key, sk, venue_id, notes_url)
    print(session)
    print("%s" % url)
    print("pending %s %s" % (start, title) )
    x = input()
    res = requests.get(url=url)
    time.sleep(1)
    list_sessions()
    print("res:", res)
    print("verify %s %s" % (start, title) )
    x = input()
    return True

def main():

    mcp_num = next_mcp_num
    sessions = list_sessions()
    # print(len(sessions))
    # sys.exit(1)
    for session in sessions:
        if add_link(session, mcp_num):
            mcp_num += 1

    '''
    print("======")

    for session in list_sessions():
        print(session)
    '''

if __name__ == "__main__":
    main()
