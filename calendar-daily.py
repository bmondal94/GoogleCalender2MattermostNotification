#!/home/bmondal/anaconda3/bin/ipython3
# coding: utf-8
from icalendar import Calendar,prop
from datetime import datetime, date, timedelta,time
from pytz import UTC      # timezone
from pytz import timezone # timezone
import re
import json
import numpy as np

get_ipython().system('curl -s -o /tmp/basic.ics https://calendar.google.com/calendar/ical/.../basic.ics')
g = open('/tmp/basic.ics','rb')
gcal = Calendar.from_ical(g.read())
g.close()

nnow = datetime.now(timezone('Europe/Berlin')) #+timedelta(days=10,hours=-2,minutes=20)
#%%
link_regex=r"\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b"
#link_regex = re.compile('((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)',re.DOTALL)
#link_regex = r'(https?://[^\s]+)'
time_interval = 86400 #in sec
DefaultLocation = "[Join Group Meeting Room](https://my.zoom.us/my) (mygroup)"
vlink = ['zoom.us','webconf','skype']
data = {}; count=0
replace_list1 =["'",'"','`','``','*']
replace_list2 =[",",',,',',',',,','']
day_ind = {'SU':6,'MO':0, 'TU':1, 'WE':2, 'TH':3, 'FR':4,'SA':5}
exdatelist_rid = {}
for component in gcal.walk('VEVENT'):
    if component.get('recurrence-id'):
        if component.get('uid') in exdatelist_rid.keys():
            exdatelist_rid[component.get('uid')].append(component.get('recurrence-id').dt)
        else:
            exdatelist_rid[component.get('uid')] = [component.get('recurrence-id').dt]
            
for component in gcal.walk('VEVENT'):
    Start=component.get('dtstart').dt
    looppass=False; updatenedt = False
    if isinstance(Start,datetime):    # Check Future
        CheckDate = Start.date()  
        now = nnow.replace(tzinfo=Start.tzinfo) # This condition is to avaoid recurrence event Daylight time correction.
    else:
        CheckDate = Start
    if CheckDate<=now.date() and component.get('rrule') and 'WEEKLY' in component['rrule']['freq']:
        EXDATElist = []
        GetRrulKeys = component['rrule'].keys()
        if component.get('EXDATE'): 
            if isinstance(component.get('EXDATE'),list): 
               EXDATElist = [prop.vDatetime.from_ical(JJ.to_ical()).replace(tzinfo=Start.tzinfo) for JJ in component.get('EXDATE')]
            else:
               EXDATElist = [prop.vDatetime.from_ical(component.get('EXDATE').to_ical()).replace(tzinfo=Start.tzinfo)] 
        if component.get('uid') in exdatelist_rid.keys():
            EXDATElist+=exdatelist_rid[component.get('uid')]
        if ('BYDAY' in GetRrulKeys):
            for I  in component['rrule']['BYDAY']:
                startweekdays = component.get('dtstart').dt
                days_ahead = day_ind[I] - startweekdays.weekday()
                if days_ahead < 0: # Target day already happened this week
                    days_ahead += 7
                Startp=(startweekdays+timedelta(days=days_ahead))
                if Startp.weekday() == now.weekday():
                        myshiftdays = (now-startweekdays).days
                        Startnn=startweekdays+timedelta(days=myshiftdays+1)
                        if (Startnn not in EXDATElist):
                            if ('UNTIL' in GetRrulKeys) and Startnn>component['rrule']['until'][0]: 
                                pass
                            else:
                                Start = Startnn
                                updatenedt = True 
        elif ("BY" not in GetRrulKeys):
            startweekdays = component.get('dtstart').dt
            if startweekdays.weekday() == now.weekday(): 
                myshiftdays = (now-startweekdays).days
                Startnn=startweekdays+timedelta(days=myshiftdays+1)
                if (Startnn not in EXDATElist):
                        if ('UNTIL' in GetRrulKeys) and Startnn>component['rrule']['until'][0]: 
                            pass
                        else:
                            Start = Startnn
                            updatenedt = True  

    elif CheckDate<=now.date() and component.get('rrule') and 'WEEKLY' not in component['rrule']['freq']:
        pass
    else:
        if isinstance(Start,datetime): 
            Start=Start.astimezone()
            now=nnow
        
    if isinstance(Start,datetime): 
        diff = Start - now
        if  diff.total_seconds()< time_interval and diff.total_seconds()>=0:
            looppass=True
            # Adjust for the local time zone
            # if no such info exist in the object
            End=component.get('dtend').dt
            if updatenedt: End += timedelta(days=myshiftdays+1)
            End=End.astimezone(Start.tzinfo)
            Start=str(Start.year),'-',str(format(Start.month,'02d')),'-',str(format(Start.day,'02d')),' at ', str(format(Start.hour,'02d')),':',str(format(Start.minute,'02d'))
            Start=''.join(Start)
            
            
            End=str(End.year),'-',str(format(End.month,'02d')),'-',str(format(End.day,'02d')),' at ', str(format(End.hour,'02d')),':',str(format(End.minute,'02d'))
            End = ''.join(End)
    else:
        if Start == date.today(): 
            looppass=True
            Start = 'Full day event'
            End = '----------'

    if looppass:
        SUmmary=component.get('summary').strip() #[3:]
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
                    if 'Full day event' in Start: LOcation= ''
            else:
                LOcation= DefaultLocation
                if 'Full day event' in Start: LOcation= ''
                
        for I in range(len(replace_list1)): # Replace some non compatible signs
            SUmmary=SUmmary.replace(replace_list1[I],replace_list2[I])
            DEscription=DEscription.replace(replace_list1[I],replace_list2[I])
            LOcation=LOcation.replace(replace_list1[I],replace_list2[I])  
        
        # Two events can have same 'stime'. 'stime' can't be used as key
        data[count] = {'summary':SUmmary,'stime':Start,'etime':End,'location':LOcation} 
        if DEscription.strip():
            data[count].update({'description': DEscription})
        if component.get("attach"):
            attachment = component.get("attach")
            if isinstance(attachment, list):
                attachment = ', '.join(attachment)
                
            for I in range(len(replace_list1)): # Replace some non compatible signs
                attachment = attachment.replace(replace_list1[I],replace_list2[I])  
            data[count].update({'attachment': attachment})
            
        count+=1
                
#%%
def make_datetime(mystr):
    if 'Full day event' in mystr:
        rvalue = datetime.combine(date.today(), time(0,0,1))
    else:
        rvalue = datetime.strptime(mystr, '%Y-%m-%d at %H:%M')
    return rvalue

generator_value = np.array([make_datetime(data[item]['stime']) for item in data ])
sorted_index = np.argsort(generator_value)
sortdata = {str(i):data[i] for i in sorted_index}

with open('/home/bmondal/CalenderData.json', 'w', encoding='utf8') as f:
    json.dump(sortdata, f)
                    
#get_ipython().system('rm /tmp/basic.ics > /dev/null')


