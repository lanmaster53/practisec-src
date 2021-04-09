from urllib.request import urlopen
from icalendar import Calendar
from datetime import timedelta
import json

def get_google_calendar_events():
    resp = urlopen('https://calendar.google.com/calendar/ical/c_24gd888cef2nd7ni0vk7av9v4c%40group.calendar.google.com/public/basic.ics')
    data = resp.read()
    cal = Calendar.from_ical(data)
    events = []
    for event in cal.walk('vevent'):
        events.append(dict(
            summary = event.get('summary'),
            dtstart = event.get('dtstart').dt,
            dtend = event.get('dtend').dt - timedelta(days=1),
            location = event.get('location'),
            description = event.get('description'),
        ))
    return events
