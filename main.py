import requests
from datetime import datetime
import smtplib
import time
import config


MY_LAT = 53.135963
MY_LONG = 23.122085

iss_live_map = config.iss_live_map
gmail_email = config.gmail_email
password = config.password


def positions_match():
    global MY_LAT, MY_LONG
    response_iss = requests.get(url="http://api.open-notify.org/iss-now.json")
    response_iss.raise_for_status()
    data_iss = response_iss.json()
    iss_latitude = float(data_iss["iss_position"]["latitude"])
    iss_longitude = float(data_iss["iss_position"]["longitude"])
    if (-5 <= (iss_latitude - MY_LAT) <= 5) and (-5 <= (iss_longitude - MY_LONG) <= 5):
        return True


def dark_match():
    parameters = {
        "lat": MY_LAT,
        "lng": MY_LONG,
        "formatted": 0,
    }
    response_sun = requests.get(
        "https://api.sunrise-sunset.org/json", params=parameters
    )
    response_sun.raise_for_status()
    data_sun = response_sun.json()
    sunrise = int(data_sun["results"]["sunrise"].split("T")[1].split(":")[0]) + 2
    sunset = int(data_sun["results"]["sunset"].split("T")[1].split(":")[0]) + 2
    hour_now = datetime.now().hour
    if (hour_now >= sunset) or (hour_now <= sunrise):
        return True


def send_email():
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(password=password, user=gmail_email)
        connection.sendmail(
            from_addr=gmail_email,
            to_addrs=config.email_recipient,
            msg=f"Subject: Stacja ISS jest nad miastem!\n\nZobacz pozycje\nLink{iss_live_map}",
        )


while True:
    if positions_match() and dark_match():
        send_email()
    time.sleep(60)
