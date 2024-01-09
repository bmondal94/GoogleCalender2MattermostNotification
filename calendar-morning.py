#!/home/bmondal/anaconda3/envs/mattermost/bin/ipython3
# -*- coding: utf-8 -*-
"""
Created on Wed May 19 10:29:06 2021

@author: bmondal
"""


import json
from datetime import datetime
#from pytz import UTC      # timezone
from pytz import timezone # timezone


with open('CalenderData.json') as f:
    data = json.load(f)

#%%
payload=r"""payload={"icon_emoji":":group-image:","username": "group","text": "### Upcoming today`s event(s)\nsummary"}"""

sum_text = ''
for i in data:
    eventtime = data[i]['stime']
    if not 'Full day event' in  eventtime: eventtime=eventtime[-5:]
    sum_text += '**Event: **'+data[i]['summary']+' ('+eventtime+')\\n'
    if 'Full day event' in  eventtime:
        keyword_dict = list(data[i].keys())
        if data[i]['location']: sum_text+='              '+data[i]['location']+'\\n'
        if 'description' in  keyword_dict: sum_text+='              '+data[i]['description']+'\\n'
            
if (len(sum_text.strip())>0):
    payload=payload.replace('summary',sum_text)
    #print(payload)
    get_ipython().system("curl -s -k -i -X POST --data-urlencode '{payload}' <Mattermost_web_address> >/dev/null")

