from email.message import Message
from smtplib import SMTP

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.auchandrive.lu/drive/{}/"
NO_TIME_SLOT_TEXT = "retrait possible dès aucun slot disponible"

shops = {
    'Cloche-Or': BASE_URL.format('magasin'),
    # 'Munsbach': BASE_URL.format('Munsbach-102'),
    # 'Bertrange': BASE_URL.format('Bertrange-104'),
    # 'Foetz': BASE_URL.format('Foetz-103'),
}

FROM_MAIL = ""
TO_MAILS = []
SMTP_SERVER = 'localhost'


def check_shop(shop_url):
    page = requests.get(shop_url)
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, "html.parser")
        if time_slot_element := soup.findAll("p", {"class": "header-infos-retrait"}).pop():
            time_slot = " ".join(time_slot_element.text.split()).lower()
            if time_slot != NO_TIME_SLOT_TEXT:
                return time_slot
    return False


def send_mail(body):
    with SMTP(SMTP_SERVER) as smtp:
        message = Message()
        message["Subject"] = "Auchan Drive Slot Checker"
        message.set_payload(body.encode('utf-8'))
        smtp.send_message(message, FROM_MAIL, TO_MAILS)


if __name__ == "__main__":
    if not all([FROM_MAIL, TO_MAILS]):
        exit("FROM_MAIL and TO_MAILS have to be configured first")
    status = ""
    for shop, url in shops.items():
        if shop_status := check_shop(url):
            status += "{} - {}\n".format(shop, shop_status)
    if status:
        send_mail(status)
