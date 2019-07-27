from twilio.rest import Client

API_KEY = 'AC2334761cef5af456c323ae0f524a4752'
API_TOKEN = 'e3dfc79afac09142e8e206482baa590a'
THEFT = 1
UNAUTHORIZED = 2
AUTHORIZED = 3


def _send_sms(vehicle_number, vehicle_type, date_time):
    client = Client(API_KEY, API_TOKEN)

    print("Sending SMS to user: {} about vehicle: {}".format('+917675818811', vehicle_number))
    if vehicle_type == THEFT:
        msg = "A theft vehicle number: {} was detected at: {} last signal point, please be alert".format(vehicle_number,
                                                                                                         date_time)
    if vehicle_type == UNAUTHORIZED:
        msg = "An unauthorized vehicle number: {} was detected at: {} at location: Ameerpet, please be alert".format(
            vehicle_number,
            date_time)
    message = client.messages.create(body=msg, from_='+19726969970', to='+917675818811')

    print(message.sid)
