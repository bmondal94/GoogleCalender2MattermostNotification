"""
Created on Thu May 20 19:17:43 2021

@author: bmondal
"""

#!/home/bmondal/anaconda3/bin/ipython3
# coding: utf-8
from icalendar import Calendar
from datetime import datetime, date
#from pytz import UTC      # timezone
from pytz import timezone # timezone
import re
import json
from apscheduler.scheduler import Scheduler

#%%
# Start the scheduler
sched = Scheduler()
sched.start()

#%%
replace_list1 =["'",'"','`','``','*']
replace_list2 =[",",',,',',',',,','']
DefaultLocation = "[Join Group Meeting Room](https://my.zoom.us/my) (mygroup)"
vlink = ['zoom.us','webconf','skype']
link_regex=r"\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b"
#link_regex = re.compile('((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)',re.DOTALL)
#link_regex = r'(https?://[^\s]+)'

#%%
def read_data():
    get_ipython().system('curl -s -o /tmp/basic.ics https://calendar.google.com/calendar/ical/.../basic.ics')
    g = open('/tmp/basic.ics','rb')
    gcal = Calendar.from_ical(g.read())
    g.close()
    return gcal

def read_database():
    with open('CalenderData.json') as f:
        data = json.load(f)
    return data

#%%
def calendar_week():
    gcal = read_data()
    #template_payload=r"""payload={"text": "### Upcoming Event @all\n **Title: ** SUMMARY \n **Description: ** DESCRIPTION \n **Starts :  ** STARTSAT \n **Ends :    ** ENDSAT\n **Location: ** LOCATION\n"}"""
    template_payload=r"""payload={"text": "### Upcoming this week events\nSUMMARY"}"""
    SUmmary = ''
    time_interval = 3600*24*7
    now = datetime.now(timezone('Europe/Berlin'))
    for component in gcal.walk('VEVENT'):
        Start=component.get('dtstart').dt
        if(component.get('summary').startswith('MM:')):
            if isinstance(Start,datetime): 
                diff = (Start - now).total_seconds() 
            else:
                diff = (component.get('dtstart').dt - date.today()).total_seconds()
    
            Start=str(Start.year),'-',str(format(Start.month,'02d')),'-',str(format(Start.day,'02d'))
            Start=''.join(Start)
    
            if  diff< time_interval and diff>0:
                heresummary = component.get('summary').strip()[3:]
                for I in range(len(replace_list1)):
                   heresummary=heresummary.replace(replace_list1[I],replace_list2[I])
                
                SUmmary += '**Event: **'+heresummary+' ('+Start+')\\n'
    if (len(SUmmary.strip())<1):
        SUmmary = '**Event: **No events for this week'           
    payload=template_payload.replace('SUMMARY',SUmmary)
    #print(payload)
    get_ipython().system("curl -s -k -X POST --data-urlencode '{payload}' Mattermost_web_address >/dev/null")
    # if (len(SUmmary.strip())>0): 
    #     payload=template_payload.replace('SUMMARY',SUmmary)
    #     get_ipython().system("curl -s -k -X POST --data-urlencode '{payload}' Mattermost_web_address >/dev/null")
    get_ipython().system('rm /tmp/basic.ics > /dev/null')

def calendar_daily():
    gcal = read_data()
    now = datetime.now(timezone('Europe/Berlin'))

    time_interval = 86400 #in sec
    
    data = {}; count=0
    for component in gcal.walk('VEVENT'):
            Start=component.get('dtstart').dt
            looppass=False
            if(component.get('summary').startswith('MM:')):
                if isinstance(Start,datetime): 
                    diff = Start - now
                    if  diff.total_seconds()< time_interval and diff.total_seconds()>=0: 
                        looppass=True
                        # Adjust for the local time zone
                        # if no such info exist in the object
                        Start=Start.astimezone()
                        Start=str(Start.year),'-',str(format(Start.month,'02d')),'-',str(format(Start.day,'02d')),' at ', str(format(Start.hour,'02d')),':',str(format(Start.minute,'02d'))
                        Start=''.join(Start)
                        End=component.get('dtend').dt
                        End=End.astimezone()
                        End=str(End.year),'-',str(format(End.month,'02d')),'-',str(format(End.day,'02d')),' at ', str(format(End.hour,'02d')),':',str(format(End.minute,'02d'))
                        End = ''.join(End)
                else:
                    if component.get('dtstart').dt == date.today(): 
                        looppass=True
                        Start = 'Full day event'
                        End = '----------'
    
                if looppass:
                    SUmmary=component.get('summary').strip()[3:]
                    DEscription=re.sub('<[^<]+?>', '',component.get('description').strip())
                    LOcation=component.get('location').strip()
                    
                    if not LOcation:
                        if DEscription:
                            allurl=re.findall(link_regex, DEscription)
                            if allurl:
                                weblink = []
                                for vurl in allurl:
                                    if any(ext in vurl for ext in vlink):
                                        weblink.append(vurl)
                                if weblink:
                                    LOcation = ', '.join(weblink)
                            else:
                                LOcation= DefaultLocation
                        else:
                            LOcation= DefaultLocation
                            
                    for I in range(len(replace_list1)): # Replace some non compatible signs
                        SUmmary=SUmmary.replace(replace_list1[I],replace_list2[I])
                        DEscription=DEscription.replace(replace_list1[I],replace_list2[I])
                        LOcation=LOcation.replace(replace_list1[I],replace_list2[I])  
                        
                    data[count] = {'summary':SUmmary,'description':DEscription,'stime':Start,'etime':End,'location':LOcation} 
                    if component.get("attach"):
                        attachment = component.get("attach")
                        if isinstance(attachment, list):
                            attachment = ', '.join(attachment)
                            
                        for I in range(len(replace_list1)): # Replace some non compatible signs
                            attachment = attachment.replace(replace_list1[I],replace_list2[I])  
                        data[count].update({'attachment': attachment})
                        
                    count+=1
                    
    with open('CalenderData.json', 'w', encoding='utf8') as f:
        json.dump(data, f)
                        
    get_ipython().system('rm /tmp/basic.ics > /dev/null')

def calendar_morning():
    data = read_database()
    payload=r"""payload={"text": "### Upcoming today events\nsummary"}"""
    #payload=r"""payload={"text": "### Upcoming today events @all\n **Title: ** summary\n"}"""
    sum_text = ''
    for i in data:
        eventtime = data[i]['stime']
        if not 'Full day event' in  eventtime: eventtime=eventtime[-5:]
        sum_text += '**Event: **'+data[i]['summary']+' ('+eventtime+')\\n'
        if 'Full day event' in  eventtime:sum_text+='              '+data[i]['location']+'; '+data[i]['description']+'\\n'
    
    if (len(sum_text.strip())>0):
        payload=payload.replace('summary',sum_text)
        #print(payload)
        get_ipython().system("curl -s -k -i -X POST --data-urlencode '{payload}' Mattermost_web_address >/dev/null")
   
def calendar_hourly():
    data = read_database()
    #payload=r"""payload={"text": "### Upcoming Event @all\n **Title: ** SUMMARY \n **Description: ** DESCRIPTION \n **Starts :  ** STARTSAT \n **Ends :    ** ENDSAT\n **Location: ** LOCATION\n"}"""
    payload=r"""payload={"text": "### Upcoming Event \n **Title: ** summary \n **Description: ** description \n **Starts :  ** stime \n **Ends :    ** etime\n **Location: ** location\n"}"""
    now = datetime.now(timezone('Europe/Berlin'))
    time_limit = 1 # Collects events within next time_limit hour
    for i in data:
        compareT = data[i]['stime']
        if not 'Full day event' in compareT:
            diff = int(compareT[-5:-3])-now.hour # Event time difference in hour
            if diff==time_limit: # Collects events within next time_limit hour
                keyword_dict = list(data[i].keys())
                for j in range(len(keyword_dict)):
                    payload=payload.replace(keyword_dict[j],data[i][keyword_dict[j]])
                if 'attachment' in  keyword_dict:
                    payload=payload[:-2]+' **Attachment: ** '+data[i]['attachment']+'"}'
                #print(payload)
                get_ipython().system("curl -s -k -i -X POST --data-urlencode '{payload}' Mattermost_web_address >/dev/null")
                
# Schedules job_function to be run on the third Friday
# of June, July, August, November and December at 00:00, 01:00, 02:00 and 03:00
sched.add_cron_job(calendar_week(), day='mon', hour='6')
sched.add_interval_job(calendar_daily(), minutes=255) # 4hours 15 minute
sched.add_cron_job(calendar_morning(), hour=6, minutue=1)
sched.add_interval_job(calendar_daily(), hours=1)
