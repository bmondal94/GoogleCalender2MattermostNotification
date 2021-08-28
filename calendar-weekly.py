#!/home/bmondal/anaconda3/bin/ipython3
# coding: utf-8
from icalendar import Calendar,prop
from datetime import datetime,  date, timedelta
from pytz import UTC      # timezone
from pytz import timezone # timezone

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <=0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)

#get_ipython().system('curl -s -o /tmp/basic.ics https://calendar.google.com/calendar/ical/.../basic.ics')
get_ipython().system('curl -s -o /tmp/basic.ics https://calendar.google.com/calendar/ical/.../basic.ics')
g = open('/tmp/basic.ics','rb')
gcal = Calendar.from_ical(g.read())
g.close()

now = datetime.now(timezone('Europe/Berlin')) #+timedelta(days=2,hours=10,minutes=23)

template_payload=r"""payload={"text": ":speaking_head: \n ### Hi there! Morning!! \n
#### Looks like we have some events this week :spiral_calendar: \nSUMMARY"}"""

#%%
SUmmary = ''

time_interval = 3600*24*7

replace_list1 =["'",'"','`','``','*']
replace_list2 =[",",',,',',',',,','']
rrulefreqdic = {'WEEKLY':7}
day_ind = {'SU':6,'MO':0, 'TU':1, 'WE':2, 'TH':3, 'FR':4,'SA':5}

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
        if component.get('EXDATE'): 
            if isinstance(component.get('EXDATE'),list): 
               EXDATElist = [prop.vDatetime.from_ical(JJ.to_ical()) for JJ in component.get('EXDATE')]
            else:
               EXDATElist = [prop.vDatetime.from_ical(component.get('EXDATE').to_ical())] 
        if component.get('uid') in exdatelist_rid.keys():
            EXDATElist+=exdatelist_rid[component.get('uid')]
        if ('BYDAY' in GetRrulKeys):
            for I  in component['rrule']['BYDAY']:
                Start=component.get('dtstart').dt 
                while True:
                    if day_ind[I] != Start.weekday(): Start = next_weekday(Start, day_ind[I]) # 0 = Monday, 1=Tuesday, 2=Wednesday...
                    try:
                        diff = (Start - now).total_seconds()
                    except:
                        diff = (Start - date.today()).total_seconds()                    
                    if  diff< time_interval and diff>=0:
                        tStart=str(Start.year),'-',str(format(Start.month,'02d')),'-',str(format(Start.day,'02d'))
                        tStart=''.join(tStart)
                        SUmmary += '**Event: **'+heresummary+' ('+tStart+')\\n'
                    next_recday = next_weekday(Start, day_ind[I]) # 0 = Monday, 1=Tuesday, 2=Wednesday...
                    if next_recday>Maxtimelimit: break
                    if next_recday in EXDATElist: next_recday = next_weekday(next_recday, day_ind[I])
                    Start = next_recday
        elif ("BY" not in GetRrulKeys):
            Start=component.get('dtstart').dt
            while True:
                    try:
                        diff = (Start - now).total_seconds()
                    except:
                        diff = (Start - date.today()).total_seconds()
                    if  diff< time_interval and diff>=0:
                        tStart=str(Start.year),'-',str(format(Start.month,'02d')),'-',str(format(Start.day,'02d'))
                        tStart=''.join(tStart)
                        SUmmary += '**Event: **'+heresummary+' ('+tStart+')\\n'
                    next_recday = Start+timedelta(days=7) # 0 = Monday, 1=Tuesday, 2=Wednesday...
                    if next_recday>Maxtimelimit: break
                    if next_recday in EXDATElist: next_recday = next_recday+timedelta(days=7)
                    Start = next_recday
    elif component.get('rrule') and 'WEEKLY' not in component['rrule']['freq']:
        heresummary = component.get('summary').strip()
        for I in range(len(replace_list1)):
            heresummary=heresummary.replace(replace_list1[I],replace_list2[I])
        SUmmary += '**Event: **'+heresummary+' ('+tStart+'): This is a recurrence event but not implemented properly in code. So information could be missing.\\n'
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
            
            SUmmary += '**Event: **'+heresummary+' ('+Start+')\\n'

#%%
if (len(SUmmary.strip())<1):
    template_payload=r"""payload={"text": ":speaking_head: \n ### Hi there! Good morning!! \n
    #### I have a good news for you.  Looks like we have no scheduled events this week :spiral_calendar:\nSUMMARY"}"""
    SUmmary = '**Event: **No events for this week\\n :cocktail: :tada:'           
payload=template_payload.replace('SUMMARY',SUmmary)
print(payload)
#get_ipython().system("curl -s -k -X POST --data-urlencode '{payload}' Mattermost_web_address >/dev/null")

#%%
# if (len(SUmmary.strip())>0): 
#     payload=template_payload.replace('SUMMARY',SUmmary)
#     get_ipython().system("curl -s -k -X POST --data-urlencode '{payload}' Mattermost_web_address >/dev/null")

#%%
get_ipython().system('rm /tmp/basic.ics > /dev/null')
