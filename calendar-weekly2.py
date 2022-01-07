#!/home/bmondal/anaconda3/bin/ipython3
# coding: utf-8
"""
Created on Mon Jun 21 14:23:21 2021

@author: bmondal
"""

from icalendar import Calendar,prop
from datetime import datetime,  date, timedelta, time
from pytz import UTC      # timezone
from pytz import timezone # timezone
import numpy as np
import readgooglesheet as GS

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <=0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)

get_ipython().system('curl -s -o /tmp/basic.ics https://calendar.google.com/calendar/ical/..../basic.ics')
g = open('/tmp/basic.ics','rb')
gcal = Calendar.from_ical(g.read())
g.close()

now = datetime.now(timezone('Europe/Berlin')) #+timedelta(days=-1,hours=10,minutes=23)

template_payload=r"""payload={"icon_emoji":":group-image:","username": "my-group","text": ":speaking_head: \n ### Hi there! Morning!! \n
#### Looks like we have some event(s) this week :spiral_calendar: \nSUMMARY"}"""

#%%
SUmmary = {}

time_interval = 3600*24*7

replace_list1 =["'",'"','`','``','*']
replace_list2 =[",",',,',',',',,','']
rrulefreqdic = {'WEEKLY':7}
day_ind = {'SU':6,'MO':0, 'TU':1, 'WE':2, 'TH':3, 'FR':4,'SA':5}
count = 0
exdatelist_rid = {}
for component in gcal.walk('VEVENT'):
    if component.get('recurrence-id'):
        if component.get('uid') in exdatelist_rid.keys():
            exdatelist_rid[component.get('uid')].append(component.get('recurrence-id').dt)
        else:
            exdatelist_rid[component.get('uid')] = [component.get('recurrence-id').dt]

for component in gcal.walk('VEVENT'):

    if component.get('rrule') and 'WEEKLY' in component['rrule']['freq']:
        GetRrulKeys = component['rrule'].keys()
        heresummary = component.get('summary').strip()
        for I in range(len(replace_list1)):
            heresummary=heresummary.replace(replace_list1[I],replace_list2[I])
        Maxtimelimit = now+timedelta(days=7)
        if 'UNTIL' in GetRrulKeys and Maxtimelimit>component['rrule']['until'][0]: 
            Maxtimelimit = component['rrule']['until'][0]
        EXDATElist = []
        SS=component.get('dtstart').dt
        if component.get('EXDATE'): 
            if isinstance(component.get('EXDATE'),list): 
               EXDATElist = [prop.vDatetime.from_ical(JJ.to_ical()).replace(tzinfo=SS.tzinfo) for JJ in component.get('EXDATE')]
            else:
               EXDATElist = [prop.vDatetime.from_ical(component.get('EXDATE').to_ical()).replace(tzinfo=SS.tzinfo)] 
        if component.get('uid') in exdatelist_rid.keys():
            EXDATElist+=exdatelist_rid[component.get('uid')]
        if ('BYDAY' in GetRrulKeys):
            for I  in component['rrule']['BYDAY']:
                Start=component.get('dtstart').dt 
                nnow = now.replace(tzinfo=Start.tzinfo) if isinstance(Start,datetime) else now # For DST correction
                if day_ind[I] != Start.weekday(): Start = next_weekday(Start, day_ind[I]) # 0 = Monday, 1=Tuesday, 2=Wednesday...
                while True:
                    if Start not in EXDATElist:       
                        try:
                            diff = (Start - now).total_seconds()
                        except:
                            diff = (Start - date.today()).total_seconds()                    
                        if  diff< time_interval and diff>=0:
                            tStart=str(Start.year),'-',str(format(Start.month,'02d')),'-',str(format(Start.day,'02d'))
                            tStart=''.join(tStart)
                            SUmmary[count] = {'Event':heresummary, 'evtime':tStart}
                            count += 1
                    next_recday = next_weekday(Start, day_ind[I]) # 0 = Monday, 1=Tuesday, 2=Wednesday...
                    if next_recday>Maxtimelimit: break
                    if next_recday in EXDATElist: next_recday = next_weekday(next_recday, day_ind[I])
                    Start = next_recday
        elif ("BY" not in GetRrulKeys):
            Start=component.get('dtstart').dt
            while True:
                if Start not in EXDATElist:
                    try:
                        diff = (Start - now).total_seconds()
                    except:
                        diff = (Start - date.today()).total_seconds()
                    if  diff< time_interval and diff>=0:
                        tStart=str(Start.year),'-',str(format(Start.month,'02d')),'-',str(format(Start.day,'02d'))
                        tStart=''.join(tStart)
                        SUmmary[count] = {'Event':heresummary, 'evtime':tStart}
                        count += 1
                next_recday = Start+timedelta(days=7) # 0 = Monday, 1=Tuesday, 2=Wednesday...
                if next_recday>Maxtimelimit: break
                if next_recday in EXDATElist: next_recday = next_recday+timedelta(days=7)
                Start = next_recday
    elif component.get('rrule') and 'WEEKLY' not in component['rrule']['freq']:
        heresummary = component.get('summary').strip()
        for I in range(len(replace_list1)):
            heresummary=heresummary.replace(replace_list1[I],replace_list2[I])
        SUmmary[count]= {'Event':heresummary+'(This is a recurrence event but not implemented properly in code. So information could be missing.)','evtime':'0-0-0'}
        count += 1
    else:
        Start=component.get('dtstart').dt
        if isinstance(Start,datetime): 
            diff = (Start - now).total_seconds() 
        else:
            diff = (component.get('dtstart').dt - date.today()).total_seconds()
    
        Start=str(Start.year),'-',str(format(Start.month,'02d')),'-',str(format(Start.day,'02d'))
        Start=''.join(Start)
    
        if  diff< time_interval and diff>=0:
            heresummary = component.get('summary').strip()
            for I in range(len(replace_list1)):
               heresummary=heresummary.replace(replace_list1[I],replace_list2[I])
            
            SUmmary[count] = {'Event':heresummary, 'evtime':Start}
            count += 1       

#%%
def make_datetime(mystr):
        rvalue = datetime.strptime(mystr, '%Y-%m-%d')
        return rvalue
SUlmmary = ''
if SUmmary:
    generator_value = np.array([make_datetime(SUmmary[item]['evtime']) for item in SUmmary ])
    sorted_index = np.argsort(generator_value)
    for i in sorted_index:
        SUlmmary+='**Event: **'+SUmmary[i]['Event']+' ('+SUmmary[i]['evtime']+')\\n'
else:
    template_payload=r"""payload={"icon_emoji":":group-image:","username": "my-group","text": ":speaking_head: \n ### Hi there! Good morning!! \n
#### I have a good news for you.  Looks like we have no scheduled events this week :spiral_calendar:\nSUMMARY"}"""
    SUlmmary = '**Event: **No events for this week\\n :cocktail: :tada:'  
         
payload=template_payload.replace('SUMMARY',SUlmmary)
#print(payload)
get_ipython().system("curl -s -k -X POST --data-urlencode '{payload}' Mattermost_hook_address >/dev/null")

#%%
# if (len(SUmmary.strip())>0): 
#     payload=template_payload.replace('SUMMARY',SUmmary)
#     get_ipython().system("curl -s -k -X POST --data-urlencode '{payload}' Mattermost_hook_address >/dev/null")

#%%
get_ipython().system('rm /tmp/basic.ics > /dev/null')

#%%----------------------------------------------------------------------------

fname = '/home/bmondal/GoogleSheetMeetingList.csv'
try:
    payloadGS = GS.SendWeeklyNotification(fname)
    #print(payloadGS)
    get_ipython().system("curl -s -k -X POST --data-urlencode '{payloadGS}' Mattermost_hook_address >/dev/null")
except:
    pass
