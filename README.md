# GoogleCalender2MattermostNotification
This reads google calendar and send notification to mattermost. The project is not complete yet. The project was halted for several reasons reaching to it's minimum goal. The scripts are still not the best pythonic way. **main.pdf** will give you an overview of the limitations of the implementations.

* The project uses crontab settings for the timings. This is not available in windows system.
* **APscheduler.py** was meant to develop in the purpose of system independence. Unfortunately, its development was halted for several reasons. 

## Scripts description
* **calendar-weekly.py:** Sends a brief overview of all the events for the upcoming whole week. The events are not in perfect order. 
* **calendar-weekly2.py:** Updated version of **calendar-weekly.py:**. Use this one instead of **calendar-weekly.py**. (*Type: Soft notification*)
* **calendar-daily.py:** Creates the database for all the events at a particular day.
* **calendar-morning.py:** Reads the database and sends an overview notification of all the events at that particular day. (*Type: Soft notification*)
* **calendar-hourly.py:** Reads the database and sends the details of an event 'the' hour before the event schedule. (*Type: Pushed notification*)
* **calendar-minute.py:** Reads the database and sends the details of an event 1 minute before the event schedule. (*Type: Pushed notification*)
* **readgooglesheet.py:** Contains the function definitions for reading Google sheet. Please check **TestGoogleSheet.xlsx** for the template Google sheet.
* **crontab_settings.txt:** Sets the different timings.
