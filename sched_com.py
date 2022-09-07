#!/usr/bin/env python3

import os
import json
import pickle
import re
import requests
# import sys
import time
import tempfile

year = 2022
# con = "stevegttest12020"
con = "nomcon2022"
key = os.environ['SCHED_API_KEY']
first_mcp_num = 250

conffn = "sched_com-%d.conf.json" % year
conf = json.load(open(conffn))
redir = conf['redirect']

# XXX move db into sqlite
dbfn = "sched_com-%d.db" % year

try:
    db = pickle.load(open(dbfn, 'rb'))
except:
    db = {}
    db['sk2mcp'] = {}

if db.get('sk2doc') is None:
    db['sk2doc'] = {}

# mcp_index_url = "https://script.google.com/a/t7a.org/macros/s/AKfycbx4RA9gKTs8feuWgiE2QMuu_xCgkp3sgldZJvecmMN9PmreW0ei/exec"
mcp_index_url = "http://mcp.systems/"

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
    notes_url = get_notes_url(session, mcp_num)

    if notes_url is None:
        print("SKIPPING -- re-run after destination url is populated in db")
        x = input()
        return False
    print("notes_url %s" % (notes_url))

    sk = session['event_key']
    db['sk2doc'][sk] = notes_url

    title = session['name']
    start = session['event_start']
    venue_id = session.get('venue_id', '')
    url = "https://%s.sched.com/api/session/mod?api_key=%s&session_key=%s&venue_id=%s&Session_Notes_URL=%s" % (
            con, key, sk, venue_id, notes_url)
    print(session)
    print("%s" % url)
    q = requests.utils.quote
    existing_url = session.get("Session Notes URL")
    if existing_url:
        existing_url = q(existing_url)
        if existing_url == notes_url:
            print("MATCHED %s %s" % (start, title))
        else:
            print("CHANGED %s %s" % (start, title))
            ckurl = "%s/doc/mcp-%d" % (mcp_index_url, mcp_num)
            ckres = requests.get(url=ckurl)
            print("CHANGED -- %s status %d" % (ckurl, ckres.status_code))
            print("CHANGED -- if there is no doc for mcp-%d, then remove URL from sched and re-run" % mcp_num)
            print("old: %s" % existing_url)
            print("new: %s" % notes_url)
            x = input()
        return False
    print("pending %s %s" % (start, title))
    x = input()
    
    # insert the notes doc URL
    # - comment out when testing
    res = requests.get(url=url)

    time.sleep(1)
    list_sessions()
    print("res:", res)
    print("verify %s %s" % (start, title))
    x = input()
    return True

def get_notes_url(session, mcp_num):

    # handle redirects, possibly daisy-chained
    # XXX sorta redundant with the thing in main()
    sk = session['event_key']
    redir_count = 0
    while True:
        newsk = redir.get(sk)
        if newsk is None:
            notes_url = db['sk2doc'].get(sk)
            if notes_url is not None:
                return notes_url
            break
        redir_count += 1
        sk = newsk

    title = session['name']

    if redir_count > 0:
        print("redirected but no destination url yet: ", title)
        return None

    start = session['event_start']
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
    return notes_url


def main():

    sessions = list_sessions()
    sessions = sorted(sessions, key=lambda x: x['event_start'])
    print(len(sessions))

    '''
    print("======")
    for session in list_sessions():
        print(session)
    sys.exit(1)
    '''

    # detect missing rooms
    for a in sessions:
        venue = a.get("venue")
        if venue == "TBA" or venue is None or venue == "":
            print("MISSING VENUE (%s) %s" % (a.get("event_start"), a.get("name")))
            x = input()

    # detect shared zoom sessions
    for a in sessions:
        akey = a.get("event_key")
        for b in sessions:
            bkey = b.get("event_key")
            if akey == bkey:
                continue
            if a.get("venue") != b.get("venue"):
                continue
            if a.get("venue") == "TBA":
                continue
            if a.get("venue") is None:
                continue
            if a.get("event_end") != b.get("event_start"):
                continue
            print("SHARED ZOOM (%s) %s | (%s) %s" % (
                a.get("event_key"), a.get("name"),
                b.get("event_key"), b.get("name")))
            if redir.get(akey) or redir.get(bkey):
                continue
            print("...add an entry to %s to redirect %s to %s or vice versa so they share the same doc" % (
                        conffn, a.get("event_key"), b.get("event_key")))
            x = input()

    # assign mcp numbers
    for session in sessions:
        sk = session['event_key']
        if db['sk2mcp'].get(sk):
            continue
        # don't assign an mcp number is session is redirected to another
        newsk = redir.get(sk)
        if newsk is not None:
            continue
        # get next available mcp number
        for mcp_num in range(first_mcp_num, 999):
            if mcp_num in db['sk2mcp'].values():
                continue
            db['sk2mcp'][sk] = mcp_num
            break

    # handle redirects, possibly daisy-chained
    for session in sessions:
        sk = session['event_key']
        while True:
            newsk = redir.get(sk)
            if newsk is None:
                break
            print("REDIRECT session %s to %s" % (sk, newsk))
            oldmcp = db['sk2mcp'].get(sk)
            newmcp = db['sk2mcp'].get(newsk)
            if oldmcp is not None and oldmcp != newmcp:
                print("REDIRECT CHANGED MCP: mcp was %d, now %d -- <enter> to confirm" % (oldmcp, newmcp))
                x = input()
            db['sk2mcp'][sk] = newmcp
            sk = newsk

    pickle.dump(db, open(dbfn, 'wb'))

    for sk, mcp in db['sk2mcp'].items():
        print(mcp, sk)

    for session in sessions:
        # print(session['event_start'], session['name'])
        # if session['event_key'] != "47":
        #   continue
        sk = session['event_key']
        mcp_num = db['sk2mcp'][sk]
        assert(mcp_num >= first_mcp_num)
        add_link(session, mcp_num)
        pickle.dump(db, open(dbfn, 'wb'))



if __name__ == "__main__":
    main()
