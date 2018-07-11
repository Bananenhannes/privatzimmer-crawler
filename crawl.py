#!/usr/bin/python
# coding=utf-8
import requests
from lxml import html
from twython import Twython
import Config
from time import sleep
import json
import os.path
import smtplib

Filename = "crawlerdata"
refresh_time = 300


# Fetches the website and extracts the offers from the table.
# If an old offer list is passed as the argument, only offers which are not contained in the list yet will be returned.
def get_new_offers(old_offers):
    # Get the website and extract the tables
    page = requests.get("http://www.studentenwerk-muenchen.de/wohnen/privatzimmervermittlung/angebote/")
    tree = html.fromstring(page.content)
    table_muenchen, table_freising, table_rosenheim = tree.xpath("//table/tbody")

    new_offers = []
    # Iterate through table columns
    for tr_element in table_muenchen.xpath(".//tr"):
        row = tr_element.xpath('./td[position()=1]/a/text() | ./td[position()>1]/text()')

        offer = {"nr": row[0].split()[0]}
        # If the offer is not yet in the list, we found a new one.
        if old_offers==[] or offer["nr"] not in [x["nr"] for x in old_offers]:
            offer["district"] = " ".join(row[1].split())
            offer["street"] = " ".join(row[2].split())
            offer["rent_type"] = "".join(row[3].split())
            offer["rent_cost"] = float(row[4].split()[0].replace(".", "").replace(",", "."))
            offer["rooms"] = float(row[5].split()[0].replace(",", "."))
            offer["size"] = float(row[6].split()[0].replace(",", "."))
            offer["link"] = "http://www.studentenwerk-muenchen.de/wohnen/privatzimmervermittlung/angebote/" \
                            "?tx_stwmprivatzimmervermittlung_angebotabfrage[angebot]=" \
                            + offer["nr"] + "&tx_stwmprivatzimmervermittlung_angebotabfrage[action]=show"
            new_offers.append(offer)

    return new_offers


# write the offer list to the specified path
def write_to_disk(path, offer_list):
    f = open(path, "w")
    f.write(json.dumps(offer_list))
    f.close()


# reads an existing offer list from the given path
def read_from_disk(path):
    if os.path.exists(path):
        f = open(path, "r")
        data = f.read()
        offer_list = json.loads(data)
        f.close()
    else:
        offer_list = []
    return offer_list


# Uses the twitter API to post new offers
def twitter_post(offer_list):
    for offer in offer_list:
        tweet = "Neues Zimmer in {}! {}, {}€, {}qm. Link: {}".format(offer["district"], offer["rent_type"],
                                                                    offer["rent_cost"], offer["size"], offer["link"])
        api = Twython(Config.apiKey, Config.apiSecret, Config.accessToken, Config.accessTokenSecret)
        api.update_status(status=tweet)
        sleep(5)


# Sends new offers via mail
def send_mail(offer_list):
    server = smtplib.SMTP(Config.smtpserver, 587)
    server.starttls()
    server.login(Config.mail_address, Config.mail_password)

    message = "Subject: {} neue Privatzimmer Angebote\n\n".format(len(offer_list))
    for offer in offer_list:
        message += "Neues Zimmer in {}! {}, {}€, {}qm.\nLink: {} \n\n".format(offer["district"], offer["rent_type"],
                                                                             offer["rent_cost"], offer["size"], offer["link"])
    server.sendmail(Config.mail_address, Config.mail_address, message)
    server.quit()


# Try to load existing offers from file
current_offers = read_from_disk(Filename)

# If there were no existing offers found, initialise the offer list
if current_offers ==[]:
    current_offers = get_new_offers(current_offers)

# Main loop
while True:
    # fetch new offers
    new_offers = get_new_offers(current_offers)
    print("Found {} new offers".format(len(new_offers)))
    # store them
    write_to_disk(Filename, new_offers+current_offers)
    # distribute to twitter and mail
    if len(new_offers) > 0:
        twitter_post(new_offers)
        send_mail(new_offers)
    # update offer list
    current_offers = new_offers + current_offers

    sleep(refresh_time)
