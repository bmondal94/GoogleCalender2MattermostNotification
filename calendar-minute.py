#!/home/bmondal/anaconda3/bin/ipython3
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
#payload=r"""payload={"text": "### Upcoming Event @all\n **Title: ** SUMMARY \n **Starts :  ** STARTSAT \n **Ends :    ** ENDSAT\n **Location: ** LOCATION\n"}"""
payload=r"""payload={"icon_emoji":":group-image:","username": "group","text": "### Meeting in 1 min @all\n **Title: ** summary \n **Starts :  ** stime \n **Ends :    ** etime\n **Location: ** location\n"}"""
now = datetime.now(timezone('Europe/Berlin'))

time_limit = 1 # Collects events within next time_limit minute

for i in data:
    compareT = data[i]['stime']
    if not 'Full day event' in compareT:
        if int(compareT[-5:-3])==0 and int(compareT[-2:])==0: compareT='24:00' # Midnight
        time_diff = (int(compareT[-5:-3])*60+int(compareT[-2:]))-(now.hour*60+now.minute)
        if time_diff==time_limit: # Collects events within next time_limit minute
            keyword_dict = list(data[i].keys())
            payloadtmp=payload
            for j in range(len(keyword_dict)):
                payloadtmp=payloadtmp.replace(keyword_dict[j],data[i][keyword_dict[j]])
                
            if 'description' in  keyword_dict:
                payloadtmp=payloadtmp[:-2]+' **Description: ** '+data[i]['description']+'\\n"}'
            if 'attachment' in  keyword_dict:
                payloadtmp=payloadtmp[:-2]+' **Attachment: ** '+data[i]['attachment']+'\\n"}'
            
            #print(payloadtmp)
            get_ipython().system("curl -s -k -i -X POST --data-urlencode '{payloadtmp}' <Mattermost_web_address> >/dev/null")
            
