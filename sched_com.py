#!/usr/bin/env python3

import os
import json
import pickle
import re
import requests
import sys
import time
import tempfile

year = 2021
# con = "stevegttest12020"
con = "nomcon2021"
key = os.environ['SCHED_API_KEY']
first_mcp_num = 170

dbfn = "sched_com-%d.db" % year

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
    filename = "mcp-%d-nomcon-%d-%s" % (mcp_num, year, title)
    filename = filename.lower()
    filename = re.sub('\W', '-', filename) 
    filename = re.sub('\-+', '-', filename) 
    filename = filename[:80]
    q = requests.utils.quote
    parms = "submit=create&session_year=%d&session_title=%s&session_filename=%s&session_date=%s&session_speakers=%s" % (
                year, q(title), filename, q(start), q(speakers))
    notes_url = q("%s?%s" % (mcp_index_url, parms))
    print("%s?%s" % (mcp_index_url, parms))
    url = "https://%s.sched.com/api/session/mod?api_key=%s&session_key=%s&venue_id=%s&Session_Notes_URL=%s" % (
            con, key, sk, venue_id, notes_url)
    print(session)
    print("%s" % url)
    existing_url = session.get("Session Notes URL")
    if existing_url:
        existing_url = q(existing_url)
        if existing_url == notes_url:
            print("MATCHED %s %s" % (start, title) )
        else:
            print("CHANGED -- if there is no doc for mcp-%d, then remove URL from sched and re-run" % mcp_num)
            print("CHANGED %s %s" % (start, title) )
            print("old: %s" % existing_url)
            print("new: %s" % notes_url)
            x = input()
        return False
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

    try:
        db = pickle.load(open(dbfn, 'rb'))
    except:
        db = {}
        db['sk2mcp'] = {}

    sessions = list_sessions()
    sessions = sorted(sessions, key=lambda x: x['event_start'])
    print(len(sessions))
    # sys.exit(1)

    # assign mcp numbers
    for session in sessions:
        sk = session['event_key']
        if db['sk2mcp'].get(sk):
            continue
        # get next available mcp number
        for mcp_num in range(first_mcp_num, 999):
            if mcp_num in db['sk2mcp'].values():
                continue
            db['sk2mcp'][sk] = mcp_num
            break

    pickle.dump(db, open(dbfn, 'wb'))

    for session in sessions:
        # print(session['event_start'], session['name'])
        # if session['event_key'] != "47":
        #   continue
        sk = session['event_key']
        mcp_num = db['sk2mcp'][sk]
        assert(mcp_num >= first_mcp_num)
        add_link(session, mcp_num)

    '''
    print("======")

    for session in list_sessions():
        print(session)
    '''

if __name__ == "__main__":
    main()
