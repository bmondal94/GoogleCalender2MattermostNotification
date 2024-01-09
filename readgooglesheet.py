#!/home/bmondal/anaconda3/envs/mattermost/bin/ipython3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 26 12:35:34 2021

@author: bmondal
"""

import os.path
import pandas as pd
from datetime import date, datetime
import time

#------------------------------------------------------------------------------
def ReadGsheetURL(sheeturl, headerline=7, usecolmns=[0,1,2,3,4,5],WeekString='Cal week'):
    df = pd.read_csv(sheeturl, skiprows=headerline, index_col=None, usecols=usecolmns) # 1st row comment line
    df = df.dropna(how='all').reset_index(drop=True)
    df.dropna(subset=[WeekString],inplace=True)
    df = df.fillna('')
    df[WeekString] = df[WeekString].astype(int)
    WeekNumber, _ = GetDateParameters()
    df = df[df.index[df[WeekString] == WeekNumber][0]:].reset_index(drop=True)   
    return df

def ReadDatabase(fname):
    df = pd.read_csv(fname, index_col=None) 
    df = df.fillna('')
    return df

def CheckUpdated(sheeturl, fname, payload=None, headerline=7,WeekString='Cal week'):
    df = ReadDatabase(fname)
    df_nnew = ReadGsheetURL(sheeturl, headerline=headerline,usecolmns=[0,1,2,3,4,5,6,7,8,9,10])
    if not df.equals(df_nnew):
        WeekNumber, _ = GetDateParameters()
        df_nnew.to_csv(fname, index=False)
        # On sunday the Calender week changes. ==> df_nnew changes apparently.
        # try, except: ensures no error raise in the begining of year. WeekNumber changes from 52 to 1.
        try:
            if not df[df.index[df[WeekString] == WeekNumber][0]:].reset_index(drop=True).equals(df_nnew):
                payload = SendMattermostNotification(df_nnew)
        except:
            pass
    return payload

def CreateTable(df, extra=None, LineNum=None):
    header='|'+'|'.join(df.columns)+'|\n'
    for _ in range(len(df.columns)):
        header+='| :-----:'
    header+='|\n'
    for i, I in enumerate(df.values):
        II = [extra+str(J)+extra if i==LineNum else str(J) for J in I]
        line='|'+'|'.join(II)+'|\n'
        header+=line
    return header
       
def SendMattermostNotification(df):
    header=CreateTable(df)
    todaydate = datetime.now().strftime('%Y-%m-%d  %H:%M:%S') #"%d %B,%Y  %H:%M:%S") #'%Y-%m-%d  %H:%M:%S')
    payload=f'payload={{"icon_emoji":":group-image:","username": "group","text": "### The group seminar schedule has been updated ({todaydate}) \n{header}"}}'
    return payload

def Ger2EngDayConversion(DD):
    EngDay = ['Su','Mo','Tu','We','Th','Fr','Sa']
    GerDay = ['So','Mo','Di','Mi','Do','Fr','Sa']
    if DD in GerDay: 
        return EngDay[GerDay.index(DD)]
    else:
        return DD

def GetDateParameters():
    DateToday = date.today() #+timedelta(days=1)
    WeekNumber = DateToday.isocalendar()[1]
    TodayWeekDay = DateToday.strftime('%a')[:2]
    return WeekNumber, TodayWeekDay

def UpdateDescription(fname, maxrepetation=2, Description=None,WeekString='Cal week'):  
    df = ReadDatabase(fname)
    WeekNumber, TodayWeekDay = GetDateParameters()
    if TodayWeekDay not in df.columns: TodayWeekDay = Ger2EngDayConversion(TodayWeekDay)
    TodaysList = df.iloc[df.index[df[WeekString] == WeekNumber]]
    if (TodayWeekDay in df.columns) and (not TodaysList.empty):
        personlist = [TodaysList.get(TodayWeekDay).item()]
        for I in range(1,maxrepetation):
            XX = TodaysList.get(TodayWeekDay+'.'+str(I))
            if XX is not None: personlist.append(XX.item())
    
        Persons = ' and '.join(personlist)
        Description = 'Talk by '+Persons
        
    return Description  

def UpdateDescription_v2(fname, maxrepetation=2, Description=None,WeekString='Cal week'):  
    df = ReadDatabase(fname)
    df = df.iloc[:,:-2]
    WeekNumber, TodayWeekDay = GetDateParameters()
    if TodayWeekDay not in df.columns: TodayWeekDay = Ger2EngDayConversion(TodayWeekDay)
    TodaysList = df.iloc[df.index[df[WeekString] == WeekNumber]]
    if (TodayWeekDay in df.columns) and (not TodaysList.empty):
        CoulmnIndexNeed = TodaysList.columns.get_loc(TodayWeekDay) + 1
        extra_ = 1 if TodayWeekDay == 'We' else 2
        Persons = ' and '.join(filter(None, list(TodaysList.iloc[:, CoulmnIndexNeed:CoulmnIndexNeed+extra_].values[0])))
        Description = 'Talk by '+Persons
        
    return Description

def SendWeeklyNotification(fname,WeekString='Cal week'):
    df = ReadDatabase(fname)
    WeekNumber, _ = GetDateParameters()
    WeekPos = df.index[df[WeekString] == WeekNumber][0]
    maxcount = min(5,len(df.index))
    mytable=CreateTable(df[:maxcount], extra='**', LineNum=WeekPos)
    
    modification_time = os.path.getmtime(fname)
    local_time = time.ctime(modification_time)
    payload=f'payload={{"icon_emoji":":group-image:","username": "group","text": "### This week group seminar schedule (last updated on {local_time})\n{mytable}"}}'
    return payload
    
#%%----------------------------------------------------------------------------

if  __name__ == '__main__':
    GoogleSheet = 'https://docs.google.com/spreadsheets/d'
    SheetId = ''
    SheetNumber = 0
    sheeturl = f"{GoogleSheet}/{SheetId}/export?format=csv&gid={SheetNumber}"
    fname = '/home/bmondal/GoogleSheetMeetingList.csv'
    
    if not os.path.isfile(fname):
        df = ReadGsheetURL(sheeturl,headerline=1)
        df.to_csv(fname, index=False)
    
    
    payload = CheckUpdated(sheeturl, fname,headerline=1)
    print(payload)
    
    payload = SendWeeklyNotification(fname)
    print(payload)
    
    Description = UpdateDescription(fname)
    if Description:
        print(Description)

