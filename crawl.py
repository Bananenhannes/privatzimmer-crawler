import requests
from lxml import html
from twython import Twython
import TwitterKeys
from time import sleep
import json
import os.path

Filename = "crawlerdata"
refresh_time = 300

# Get the HTML Doc and parse it


def get_new_offers(old_offers):
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


def write_to_disk(path, offer_list):
    f = open(path, "w")
    f.write(json.dumps(offer_list))
    f.close()


def read_from_disk(path):
    if os.path.exists(path):
        f = open(path, "r")
        data = f.read()
        offer_list = json.loads(data)
        f.close()
    else:
        offer_list = []
    return offer_list


def twitter_post(offer_list):
    for offer in offer_list:
        tweet = "Neues Zimmer in {}! {}, {}€, {}qm. Link: {}".format(offer["district"], offer["rent_type"],
                                                                    offer["rent_cost"], offer["size"], offer["link"])
        api = Twython(TwitterKeys.apiKey, TwitterKeys.apiSecret, TwitterKeys.accessToken, TwitterKeys.accessTokenSecret)
        api.update_status(status=tweet)
        sleep(5)


# Try to load existing offers from file
current_offers = read_from_disk(Filename)

# If there were no existing offers found, initialise the offer list
if current_offers ==[]:
    current_offers = get_new_offers(current_offers)

# Main loop
while True:
    new_offers = get_new_offers(current_offers)
    write_to_disk(Filename, new_offers+current_offers)
    twitter_post(new_offers)
    current_offers = new_offers + current_offers

    sleep(refresh_time)
