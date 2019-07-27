import smtplib
import ssl

USER_EMAIL = 'arvind.adari@aricent.com'
TO_EMAIL = 'sathikomurelli@gmail.com'
PASSWORD = ''
THEFT = 1
UNAUTHORIZED = 2
AUTHORIZED = 3

context = ssl.create_default_context()


def _send_mail(vehicle_number, vehicle_type, date_time):

    print("Sending Mail to user: {} about vehicle: {}".format('sathikomurelli@gmail.com', vehicle_number))

    server = smtplib.SMTP("10.203.112.4:25")

    msg = "{} found".format(vehicle_number)
    if vehicle_type == THEFT:
        msg = "A theft vehicle number: {} was detected at: {} last signal point, please be alert".format(vehicle_number,
                                                                                                         date_time)
    if vehicle_type == UNAUTHORIZED:
        msg = "An unauthorized vehicle number: {} was detected at: {} at location: Ameerpet, please be alert".format(
            vehicle_number,
            date_time)

    server.sendmail(
        'arvind.adari@aricent.com',
        TO_EMAIL,
        msg)

    server.quit()


if __name__ == '__main__':
    _send_mail('sathikomurelli@gmail.com')
