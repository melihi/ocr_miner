import requests
import logging

IANA_CONTENT = []
IANA_URL = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"


def download_iana():
    try:
        global IANA_CONTENT
        tlds = requests.get(IANA_URL)
        if tlds.status_code == 200:
            IANA_CONTENT = tlds.text.split("\n")

    except Exception as e:
        logging.warn("An error occurred while download iana list:", e)


download_iana()
