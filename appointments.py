# coding: latin-1
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR')

import requests


from datetime import date, datetime, timedelta
from time import time

import pytz
import random
import json
from dateutil import parser

schedule = {}
today = datetime.now()
tomorow = datetime.now() + timedelta(days=1)
tomorowplus1 = datetime.now() + timedelta(days=2)
tomorowplus2 = datetime.now() + timedelta(days=3)
tomorowplus3 = datetime.now() + timedelta(days=4)
tomorowplus4 = datetime.now() + timedelta(days=5)
tomorowplus5 = datetime.now() + timedelta(days=6)

hours = (9, 17)   # open hours
limit1 = datetime.strptime("10:00:00", "%H:%M:%S").time()
limit2 = datetime.strptime("17:00:00", "%H:%M:%S").time()
limit3 = datetime.strptime("12:00:00", "%H:%M:%S").time()
day_list = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']


# get today's date
def todayDate():
    print ("todayDate")
    return today.strftime('%d/%m/%y')

# get day of week for a date (or 'today')
def dayOfWeek(date):
    
    if date == 'today':
        print ("dayOfWeek "+day_list[today.weekday()])
        return day_list[today.weekday()]
    else:
        try:
            theDate = parser.parse(date)
        except:
            return 'invalid date format, please use format: dd/mm/yyyy'
        print ("dayOfWeek "+day_list[today.weekday()])
        return day_list[theDate.weekday()]
      #  return calendar.day_name[theDate.weekday()]
    
#########

def appointment_booking(arguments):
    try:
        print("appointment_booking" +arguments)
        arguments_array = arguments.split(',')   
        email_address="nemail@gmail.com"
        try:
            email_address=arguments_array[2]
        except IndexError:
            print('no provided_email')   

        provided_date=arguments_array[0]
        provided_time=arguments_array[1]
        
    
        time_string = provided_time.replace("PM","").replace("AM","").strip();
        time_datetime = datetime.strptime(time_string, "%H:%M");
        provided_time = str(time_datetime.time())
        start_date_time = provided_date + " " + provided_time
        timezone = pytz.timezone('Asia/Kolkata')
        start_date_time = timezone.localize(datetime.strptime(start_date_time, "%d/%m/%Y %H:%M:%S"))     

        end_date_time = start_date_time + timedelta(hours=2)
        
        if provided_date and provided_time and email_address:
            slot_checking = appointment_checking(arguments)
            if slot_checking == "Un créneau est disponible pour un rendez-vous. Souhaitez-vous continuer ?":           
                if start_date_time < datetime.now(timezone):
                    return "Veuillez saisir une date et une heure valides."
                else:
                    if day_list[start_date_time.date().weekday()] == "Samedi":
                        if start_date_time.time() >= limit1 and start_date_time.time() <= limit3:
                            event = {
                                'summary': "Appointment booking Chatbot using OpenAI's function calling feature",
                                'location': "Ahmedabad",
                                'description': "This appointment has been scheduled as the demo of the appointment booking chatbot using OpenAI function calling feature by Pragnakalp Techlabs.",
                                
                                'start': {
                                    'dateTime': start_date_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                    'timeZone': 'Asia/Kolkata',
                                },
                                'end': {
                                    'dateTime': end_date_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                    'timeZone': 'Asia/Kolkata',
                                },
                                'attendees': [
                                {'email': email_address},
                                
                                ],
                                'reminders': {
                                    'useDefault': False,
                                    'overrides': [
                                        {'method': 'email', 'minutes': 24 * 60},
                                        {'method': 'popup', 'minutes': 10},
                                    ],
                                },
                            }
                            event ={"EventTask":{"lstDynamicFieldGen":[],"IDMail":"-1","IdTVA":"-1",
                                                 "IDFolderEntity":"-1","OrganizerWaitingResponse":"0","IdEventTaskParent":"-1",
                                                 "IDMainContact":"-1","IDMainContactEntity":"-1","IdCategoryUserRole":"-1",
                                                 "IdCategoryParentEventTask":"-1","IdMeetingTask":"-1","IdTicket":"-1",
                                                 "IdUserCreator":"1","IdUserOrganizer":"508","IdUserModifier":"1",
                                                 "Name":email_address,"TimeBegin_S":start_date_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                                 "TimeEnd_S":end_date_time.strftime("%Y-%m-%dT%H:%M:%S"),"Location":"Paris","ReminderDelay":"1",
                                                 "Priority":"1","EventTaskStatus":"-1","Type":"0","IdCategory":"878","IsPrivate":"false","IdEntity":"-1",
                                                 "IdEntityParent":"-1","Use_Project":"false","Locked":"false","Deleted":"false","IdProjectCampaign":"-1",
                                                 "IsDeleted":"false"},"UserID":"1","UserContactID":"508"}
                           
                            data_json = json.dumps(event)
                            headers = {'Content-type': 'application/json'}
                            url = "http://51.178.133.91/COC_WEBSERVICE_HEALTHFITNESS/ServiceAddContact.svc/json/AddEventTaskReturnObject"
                            response = requests.post(url, data=data_json, headers=headers)
                            # service.events().insert(calendarId='primary', body=event).execute()
                            return "Rendez-vous ajouté avec succès."
                        else:
                            return "Veuillez essayer de prendre rendez-vous pendant les heures d'ouverture, soit de 10h à 14h le samedi."
                    else:
                        if start_date_time.time() >= limit1 and start_date_time.time() <= limit2:
                            event = {
                                'summary': "Appointment booking Chatbot using OpenAI's function calling feature",
                                'location': "Ahmedabad",
                                'description': "This appointment has been scheduled as the demo of the appointment booking chatbot using OpenAI function calling feature by Pragnakalp Techlabs.",
                                
                                'start': {
                                    'dateTime': start_date_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                    'timeZone': 'Asia/Kolkata',
                                },
                                'end': {
                                    'dateTime': end_date_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                    'timeZone': 'Asia/Kolkata',
                                },
                                'attendees': [
                                {'email': email_address},
                                
                                ],
                                'reminders': {
                                    'useDefault': False,
                                    'overrides': [
                                        {'method': 'email', 'minutes': 24 * 60},
                                        {'method': 'popup', 'minutes': 10},
                                    ],
                                },
                            }
                            event ={"EventTask":{"lstDynamicFieldGen":[],"IDMail":"-1","IdTVA":"-1",
                                                 "IDFolderEntity":"-1","OrganizerWaitingResponse":"0","IdEventTaskParent":"-1",
                                                 "IDMainContact":"-1","IDMainContactEntity":"-1","IdCategoryUserRole":"-1",
                                                 "IdCategoryParentEventTask":"-1","IdMeetingTask":"-1","IdTicket":"-1",
                                                 "IdUserCreator":"1","IdUserOrganizer":"508","IdUserModifier":"1",
                                                 "Name":email_address,"TimeBegin_S":start_date_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                                 "TimeEnd_S":end_date_time.strftime("%Y-%m-%dT%H:%M:%S"),"Location":"Paris","ReminderDelay":"1",
                                                 "Priority":"1","EventTaskStatus":"-1","Type":"0","IdCategory":"878","IsPrivate":"false","IdEntity":"-1",
                                                 "IdEntityParent":"-1","Use_Project":"false","Locked":"false","Deleted":"false","IdProjectCampaign":"-1",
                                                 "IsDeleted":"false"},"UserID":"1","UserContactID":"508"}
                           
                            data_json = json.dumps(event)
                            headers = {'Content-type': 'application/json'}
                            url = "http://51.178.133.91/COC_WEBSERVICE_HEALTHFITNESS/ServiceAddContact.svc/json/AddEventTaskReturnObject"
                            response = requests.post(url, data=data_json, headers=headers)
                          #  service.events().insert(calendarId='primary', body=event).execute()
                            return "Rendez-vous ajouté avec succès."
                        else:
                            return "Veuillez essayer de prendre rendez-vous pendant les heures d'ouverture, soit de 10h00 à 19h00."
            else:
                return slot_checking
        else:
            return "désolé les paramètres doivent être date, heure et adresse email séparés par une virgule, par exemple: `12/31/23, 10:00, adresse@gmail.com` serait une entrée pour 31 décembre 2023 à 10 heures."
    except:
        return "Nous sommes confrontés à une erreur lors du traitement de votre demande. Veuillez réessayer."



def appointment_reschedule(arguments):
     return "Please try to check an appointment within working hours, which is 10 AM to 7 PM."

def appointment_delete(arguments):
     return "Please try to check an appointment within working hours, which is 10 AM to 7 PM."


def appointment_checking(arguments):
    try:
        print("appointment_checking" +arguments)
        arguments_array = arguments.split(',')   
        try:
            provided_email=arguments_array[2]
        except IndexError:
            print('no provided_email')   

        provided_date=arguments_array[0]
        provided_time=arguments_array[1]

        time_string = provided_time.replace("PM","").replace("AM","").strip();
        time_datetime = datetime.strptime(time_string, "%H:%M");
        provided_time = str(time_datetime.time())
        start_date_time = provided_date + " " + provided_time
        timezone = pytz.timezone('Asia/Kolkata')
        start_date_time = timezone.localize(datetime.strptime(start_date_time, "%d/%m/%Y %H:%M:%S"))      

        if start_date_time < datetime.now(timezone):
            return "Veuillez saisir une date et une heure valides."
        else:
            weekday = start_date_time.date().weekday();
            if day_list[weekday] == "Samedi":
                if start_date_time.time() >= limit1 and start_date_time.time() <= limit3:
                    end_date_time = start_date_time + timedelta(hours=2)
                  #  events_result = service.events().list(calendarId='primary', timeMin=start_date_time.isoformat(), timeMax=end_date_time.isoformat()).execute()
                   # if events_result['items']:
                    #    return "Sorry slot is not available."
                    #else:
                    return "Un créneau est disponible pour un rendez-vous. Souhaitez-vous continuer ?"
                else:
                    return "Veuillez essayer de prendre rendez-vous pendant les heures d'ouverture, soit de 10h00 à 14h00 le samedi."
            else:
                if start_date_time.time() >= limit1 and start_date_time.time() <= limit2:
                    end_date_time = start_date_time + timedelta(hours=2)
                 #   events_result = service.events().list(calendarId='primary', timeMin=start_date_time.isoformat(), timeMax=end_date_time.isoformat()).execute()
                 #   if events_result['items']:
                  #      return "Sorry slot is not available."
                   # else:
                    return "Un créneau est disponible pour un rendez-vous. Souhaitez-vous continuer ?"
                else:
                    return "Veuillez essayer de prendre rendez-vous pendant les heures d'ouverture, soit de 10h00 à 19h00."
    except:
        return "Nous sommes confrontés à une erreur lors du traitement de votre demande. Veuillez réessayer."

  