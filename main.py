import requests
import os
import json
import time

EMAIL = ""
PASSWORD = ""

def lambda_handler(event, context):

    if event['session']['application']['applicationId'] != "amzn1.ask.skill.c8fd59e4-a9df-4bf4-9c5d-b0971baebfbf":
        print ("Invalid Application ID")
        raise
    else:
        #Not using session currently
        sessionAttributes = {}

        headers = getAccessToken()
        vehicle_id = getVehicleId(headers)

        if event['session']['new']:
            onSessionStarted(event['request']['requestId'], event['session'])
        if event['request']['type'] == "LaunchRequest":
            speechlet = onLaunch(event['request'], event['session'])
            response = buildResponse(sessionAttributes, speechlet)
        elif event['request']['type'] == "IntentRequest":
            speechlet = onIntent(event['request'], event['session'], headers, str(vehicle_id))
            response = buildResponse(sessionAttributes, speechlet)
        elif event['request']['type'] == "SessionEndedRequest":
            speechlet = onSessionEnded(event['request'], event['session'])
            response = buildResponse(sessionAttributes, speechlet)
    return (response)

def getAccessToken():
    print('Entering getAccessToken')
    params = { "grant_type" : "password", "client_id" : "81527cff06843c8634fdc09e8ac0abefb46ac849f38fe1e431c2ef2106796384", "client_secret" : "c7257eb71a564034f9419ee651c7d0e5f7aa6bfbd18bafb5c5c033b093bb2fa3", "email" : EMAIL, "password" : PASSWORD }
    response  = requests.post("https://owner-api.teslamotors.com/oauth/token/", params = params).json()

    headers = {"Authorization" : "Bearer " + response["access_token"]}
    print(headers)
    return(headers)


def getVehicleId(headers):
    print("Entering getVehicleId")
    print(headers)
    vehicles = requests.get("https://owner-api.teslamotors.com/api/1/vehicles", headers= headers).json()
    vehicle_id = vehicles["response"][0]["id"]
    print(vehicle_id)
    return vehicle_id


def onSessionStarted(requestId, session):
    print("onSessionStarted requestId=" + requestId + ", sessionId=" + session['sessionId'])


def onLaunch(launchRequest, session):
    # Dispatch to your skill's launch.
    getWelcomeResponse()

def getWelcomeResponse():
    cardTitle = "Welcome to myTesla"
    speechOutput = """By using this skill it is possible to control many functions of your Tesla Vehicle."""

    # If the user either does not reply to the welcome message or says something that is not
    # understood, they will be prompted again with this text.
    repromptText = 'Ask me commands that relate to the vehicle'
    shouldEndSession = True

    return (buildSpeechletResponse(cardTitle, speechOutput, repromptText, shouldEndSession))

def onIntent(intentRequest, session,headers,vehicle_id):
    intent = intentRequest['intent']
    intentName = intentRequest['intent']['name']

    if intentName == "GetCharging":
        return chargingResponse(headers, vehicle_id)
    elif intentName == "HonkHorn":
        return honkingResponse(headers, vehicle_id)

def chargingResponse(headers,vehicle_id):
    print(headers)
    print(vehicle_id)
    res = requests.get("https://owner-api.teslamotors.com/api/1/vehicles/" + vehicle_id + "/data_request/charge_state", headers = headers)
    if(res.status_code == 200):
        res = res.json()
        if res["response"]["charging_state"] == "Complete":
            speechOutput = "Your car has completed charging. With a range of " + str(res["response"]["battery_range"]) + "."
            cardTitle = "Your car has completed charging. With a range of " + str(res["response"]["battery_range"]) + "."
        else:
            speechOutput = "Your car is " + str(res["response"]["battery_level"]) + " charged. With a range of " + str(res["response"]["battery_range"]) + "."
            cardTitle = "Your car is " + str(res["response"]["battery_level"]) + " charged. With a range of " + str(res["response"]["battery_range"]) + "."
    else:
        speechOutput = "Error connecting to Tesla Servers. Please try again"
        cardTitle = "Error connecting to Tesla Servers. Please try again"

    repromptText = "I didn't understand that. Please try again"
    shouldEndSession = True

    return(buildSpeechletResponse(cardTitle,speechOutput,repromptText,shouldEndSession))

def honkingResponse(headers,vehicle_id):
    res = requests.post("https://owner-api.teslamotors.com/api/1/vehicles/" + str(vehicle_id) + "/command/honk_horn", headers = headers)
    if(res.status_code == 200):
        res = res.json()
        speechOutput = "Car Horn Honked."
        cardTitle = "Car Horn Honked."
    else:
        speechOutput = "Error connecting to Tesla Servers. Please try again"
        cardTitle = "Error connecting to Tesla Servers. Please try again"
    repromptText = "I didnt understand that. Please try again"
    shouldEndSession = True

    return(buildSpeechletResponse(cardTitle,speechOutput,repromptText,shouldEndSession))

# --------------- Helpers that build all of the responses -----------------------
def buildSpeechletResponse(title, output, repromptText, shouldEndSession):
    print("Entering buildSpeechletResponse")
    return ({
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": "myTesla - " + title,
            "content": "myTesla - " + output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": repromptText
            }
        },
        "shouldEndSession": shouldEndSession
    })

def buildResponse(sessionAttributes, speechletResponse):
    return ({
        "version": "1.0",
        "sessionAttributes": sessionAttributes,
        "response": speechletResponse
    })