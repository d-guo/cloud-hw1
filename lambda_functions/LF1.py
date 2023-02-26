import boto3
import datetime

def greetingHandler():
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'ElicitIntent'
            }
        },
        'messages': [
            {
            'contentType': 'PlainText',
            'content': 'Hi there! How can I help you?'
            }
        ]
    }
    
def thankYouHandler():
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'ElicitIntent'
            }
        },
        'messages': [
            {
            'contentType': 'PlainText',
            'content': 'My pleasure!'
            }
        ]
    }
    
def diningSuggestionsHandler(intent_request):
    slots = intent_request['sessionState']['intent']['slots']
    slot_vals = {
        'location': slots['location']['value']['interpretedValue'] if slots['location'] and 'interpretedValue' in slots['location']['value'] else None,
        'cuisine': slots['cuisine']['value']['interpretedValue'] if slots['cuisine'] and 'interpretedValue' in slots['cuisine']['value'] else None,
        'date': slots['date']['value']['interpretedValue'] if slots['date'] and 'interpretedValue' in slots['date']['value'] else None,
        'time': slots['time']['value']['interpretedValue'] if slots['time'] and 'interpretedValue' in slots['time']['value'] else None,
        'people': slots['people']['value']['interpretedValue'] if slots['people'] and 'interpretedValue' in slots['people']['value'] else None,
        'email': slots['email']['value']['interpretedValue'] if slots['email'] and 'interpretedValue' in slots['email']['value'] else None
    }
        
    if intent_request['invocationSource'] == 'DialogCodeHook':
        ret = validateSlots(intent_request, slot_vals)
        if ret is None:
            return {
                'sessionState': {
                    'sessionAttributes': intent_request['sessionState']['sessionAttributes'],
                    'dialogAction': {
                        'type': 'Delegate'
                    },
                    'intent': intent_request['sessionState']['intent']
                }
            }
        return ret
        
    send_sqs(slot_vals)
    return close(intent_request)
    
def send_sqs(slot_vals):
    sqs = boto3.client('sqs')
    url = 'https://sqs.us-east-1.amazonaws.com/537502574872/dining-concierge-requests'
    attr = {
        'location': {
            'DataType': 'String',
            'StringValue': slot_vals["location"]
        },
        'cuisine': {
            'DataType': 'String',
            'StringValue': slot_vals["cuisine"]
        },
        'date': {
            'DataType': 'String',
            'StringValue': slot_vals["date"]
        },
        'time': {
            'DataType': 'String',
            'StringValue': slot_vals["time"]
        },
        'people': {
            'DataType': 'String',
            'StringValue': slot_vals["people"]
        },
        'email': {
            'DataType': 'String',
            'StringValue': slot_vals["email"]
        }
    }
    
    sqs.send_message(QueueUrl=url, MessageAttributes=attr, MessageBody=('Message from LF1'))
       
def createElicitSlotResponse(intent_request, invalidSlot, message):
    return {
        'sessionState': {
            'sessionAttributes': intent_request['sessionState']['sessionAttributes'],
            'dialogAction': {
                'type': 'ElicitSlot',
                'slotToElicit': invalidSlot
            },
            'intent': intent_request['sessionState']['intent'],
        },
        'messages': [
            {
            'contentType': 'PlainText',
            'content': message
            }
        ]
    }
        
def validateSlots(intent_request, slot_vals):
    # returns None if everything is valid, otherwise returns response
    location = slot_vals['location']
    cuisine = slot_vals['cuisine']
    date = slot_vals['date']
    time = slot_vals['time']
    people = slot_vals['people']
    email = slot_vals['email']
    
    if cuisine is None:
        return
    if cuisine.lower() not in ['chinese', 'italian', 'japanese', 'mexican', 'thai']:
        return createElicitSlotResponse(intent_request, 'cuisine', 'Cuisine not supported. Please select among chinese, italian, japanese, mexican, and thai.')
        
    if date is None:
        return
    if datetime.datetime.strptime(date, '%Y-%m-%d').date() < datetime.date.today() or (datetime.datetime.strptime(date, '%Y-%m-%d').date() - datetime.date.today()).days > 7:
        return createElicitSlotResponse(intent_request, 'date', 'Invalid date. Please select a day between today and a week from today.')
        
    if time is None:
        return
    if datetime.datetime.strptime(date, '%Y-%m-%d').date() == datetime.date.today() and datetime.datetime.strptime(time, '%H:%M').time() < datetime.datetime.now().time():
        return createElicitSlotResponse(intent_request, 'date', 'Invalid time. Please select a time later today.')
        
    if people is None:
        return
    if int(people) < 1 or int(people) > 10:
        return createElicitSlotResponse(intent_request, 'people', 'Please select a number of people between 1 and 10 inclusive.')
    
        
def close(intent_request):
    intent_request['sessionState']['intent']['state'] = 'Fulfilled'
    return {
        'sessionState': {
            'sessionAttributes': intent_request['sessionState']['sessionAttributes'],
            'dialogAction': {
                'type': 'Close'
            },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': [
            {
            'contentType': 'PlainText',
            'content': 'Thanks for using our service! I will send you an email with my recommendations within a minute.'
            }
        ]
    }
    
def dispatch(intent_request):
    intent_name = intent_request['sessionState']['intent']['name']
    if intent_name == 'ThankYouIntent':
        return thankYouHandler()
    elif intent_name == 'GreetingIntent':
        return greetingHandler()
    elif intent_name == 'DiningSuggestionsIntent':
        return diningSuggestionsHandler(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def lambda_handler(event, context):
    # TODO implement
    return dispatch(event)
