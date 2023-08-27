import pytesseract
import re
from ocr_miner.ocr_engine.opencv import process_image
from email_validator import validate_email, EmailNotValidError
from urllib.parse import urlparse, urlsplit
import pyvat
import math
import requests
import logging
from ocr_miner.ocr_engine.helper import IANA_CONTENT


PHONE_PATTERNS = [
    r"[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}",
]
# id : TC, Usa social security number,Europe VAT,
ID_PATTERNS = [
    r"[1-9]{1}[0-9]{9}[02468]{1}",
    r"\b(?!000|.+0{4})(?:\d{9}|\d{3}-\d{2}-\d{4})\b",
    r"([A-Z]{2}\d{9,12})",
]
CC_PATTERNS = [r"(?:\d{4}[ -]?){3}\d{4}"]
# turkey, usa , germany,french,russia,china
PLATE_PATTERNS = [
    r"\b\d{2}\s?[A-HJ-NPR-TV-Z]{1,3}\s?\d{2,4}\b|\b\d{2}-?[A-HJ-NPR-TV-Z]{1,3}-?\d{2,4}\b",
    r"\b[A-HJ-NPR-Z0-9]{1,7}\b",
    r"\b[A-Z]{1,2}\s?[A-Z0-9]{1,4}\s?[A-Z0-9]{1,4}\b",
    r"\b[A-Z0-9]{2}-?[A-Z0-9]{2}-?[A-Z0-9]{2}\b",
    r"\b[A-Z0-9]{1}\d{3}[A-Z0-9]{2}\b",
    r"\b[A-Z]{1}[A-HJ-NP-Z]{1}[A-HJ-NP-Z0-9]{4,5}\b",
]
DATE_PATTERNS = [
    r"([1-9]|[12][0-9]|3[01])(|\/|\.|\-|\s)?(0[1-9]|1[12])\2(19[0-9]{2}|200[0-9]|201[0-8])"
]
EMAIL_PATTERNS = [r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"]
DOMAIN_PATTERNS = [
    r"(?:[_a-z0-9](?:[_a-z0-9-]{0,61}[a-z0-9])?\.)+(?:[a-z](?:[a-z0-9-]{0,61}[a-z0-9])?)"
]
URL_PATTERNS = [
    r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
]
# md5-md4 , sha256 , ntlm , sha1
HASH_PATTERNS = [
    r"[a-f0-9]{32}",
    r"[a-f0-9]{64}",
    r"(\\$NT\\$)?[a-f0-9]{32}",
    r"[a-f0-9]{40}",
    r"[a-f0-9]{128}",
]
COMBOLIST_PATTERNS = [r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9.-]+:[a-zA-Z0-9._-]+"]

PATTERN_LIST = [
    PHONE_PATTERNS,
    ID_PATTERNS,
    CC_PATTERNS,
    PLATE_PATTERNS,
    DATE_PATTERNS,
    EMAIL_PATTERNS,
    DOMAIN_PATTERNS,
    URL_PATTERNS,
    HASH_PATTERNS,
    COMBOLIST_PATTERNS,
]
# TODO
# key point detection
# mypy
# test
# ip  extract


async def start_ocr(image_location: str):
    """Start tesseract ocr.

    Args:
        image_location (str): path of image.
    """

    try:
        img = process_image(image_location)
        custom_config = r"--oem 3 --psm 6 -l eng+tr"  # +tr+deu+fra+ita+spa+por
        ocr_data = pytesseract.image_to_string(img, config=custom_config)
        ocr_data = clear_data(ocr_data)
        print(ocr_data)
        result = await find_regex(ocr_data)
        print(result)
        status = ""
        # if ocr data emtp set status to unsuccess
        if ocr_data == None or ocr_data == "":
            status = "Unsuccessful"
        else:
            status = "Successful"

        response = {
            "content": str(ocr_data),
            "status": status,
            "findings": result,
        }
        print(response)
        return response
    except Exception as e:
        logging.warning(e)


async def find_regex(ocr_data: str) -> dict:
    """Extract data from content with regex patterns.

    Args:
        ocr_data (str): ocr text.
    """
    # global result
    result = {}
    global PATTERN_LIST

    for i, regex_list in enumerate(PATTERN_LIST):
        found_data = []
        for regex in regex_list:
            regex_result = re.findall(regex, str(ocr_data), re.MULTILINE)
            for match in regex_result:
                if match != None or match != "":
                    found_data.append(match)

        found_data = list(set(found_data))
        if len(found_data) > 0:
            print(found_data)
            match i:
                case 0:
                    tmp = []
                    try:
                        for phone in found_data:
                            # if phone[-1:].isdigit():

                            tmp.append({"value": phone, "TYPE": "PHONE"})
                    except IndexError as e:
                        logging.warn(e)
                    if tmp:
                        result["PHONE_NUMBERS"] = tmp
                case 1:
                    tmp = []
                    try:
                        for ID in found_data:
                            verify_result = verify_identity(ID)

                            if verify_result != None:
                                tmp.append({"value": ID, "TYPE": verify_result})
                            else:
                                tmp.append({"value": ID, "TYPE": "UNKNOWN"})
                    except IndexError as e:
                        logging.warn(e)
                    if tmp:
                        result["ID_NUMBER"] = tmp
                case 2:
                    tmp = []

                    for cc in found_data:
                        tmp.append({"value": cc, "TYPE": "CREDIT_CARD"})
                    if tmp:
                        result["CREDIT_CARD_NUMBERS"] = tmp
                case 3:
                    tmp = []

                    for plate in found_data:
                        if len(plate) > 5 and verify_plate(plate):
                            tmp.append({"value": plate, "type": "PLATE"})
                    if tmp:
                        result["PLATES"] = tmp
                case 4:
                    tmp = []
                    # iterate every grepped date string. Replace " " - . chars
                    # Sample data:
                    # [('13', '.', '08', '1987'), ('13', '', '08', '1987'), ('13', '/', '08', '1987'), ('13', '-', '08', '1987'), ('13', ' ', '08', '1987')]
                    try:
                        for date in found_data:
                            extract_date = ""
                            for string in date:
                                for word in string:
                                    if word.isdigit():
                                        extract_date += word
                                if extract_date[-1] != "/":
                                    extract_date += "/"
                            # delete last / in date string  Example: 11/11/1987/
                            extract_date = extract_date[:-1]

                            tmp.append({"value": extract_date, "type": "DATE"})
                    except IndexError as e:
                        logging.warn(e)
                    if tmp:
                        result["DATES"] = tmp
                case 5:
                    tmp = []

                    for email in found_data:
                        try:
                            mail = validate_email(email, check_deliverability=False)
                            tmp.append({"value": mail.normalized, "type": "EMAIL"})

                        except EmailNotValidError as e:
                            logging.warn(e)
                    if tmp:
                        result["EMAILS"] = tmp
                case 6:
                    # tmp = []
                    dat = verify_domain(found_data)
                    if dat:
                        result["DOMAINS"] = dat
                        # tmp.append({"value": domain, "type": "DOMAIN"})

                    # result["DOMAINS"] = tmp
                case 7:
                    # url[0] because avoid to add sub groups
                    tmp = []
                    for url in found_data:
                        try:
                            parsed_url = urlparse(url[0])
                            if parsed_url.scheme and parsed_url.netloc:
                                tmp.append({"value": url[0], "type": "URL"})

                        except EmailNotValidError as e:
                            logging.warn(e)
                    if tmp:
                        result["URLS"] = tmp
                case 8:
                    tmp = []
                    for hash in found_data:
                        if len(hash) > 30:
                            if verify_hash(hash):
                                tmp.append({"value": hash, "type": "HASH"})
                    if tmp:
                        result["HASHS"] = tmp
                case 9:
                    tmp = []
                    for combo in found_data:
                        if combo.count(":") <= 1 and "http" in combo:
                            continue
                        tmp.append({"value": combo, "type": "COMBO"})
                    if tmp:
                        result["COMBOLISTS"] = tmp
                case _:
                    print("not matchedd")
    return result


def clear_data(ocr_data: str):
    """Clear and normalzize ocr text.

    Args:
        ocr_data (str): ocr text string.


    """
    replace_dot = [" .", ". ", " . "]
    replace_url = ["http: //", "https: //"]
    for dot in replace_dot:
        ocr_data = ocr_data.replace(dot, ".")
    for url in replace_url:
        ocr_data = ocr_data.replace(url, url.replace(" ", ""))

    return ocr_data


def verify_identity(identity_data: str) -> str:
    """Validate various types of ID's.
    Turkish citizen no, Usa social security number ,

    Args:
        identity_data (str): id for validation.

    Returns:
        bool: Validated or not validated result.
    """
    try:
        check_vat = pyvat.is_vat_number_format_valid(identity_data, country_code=None)

        if check_vat:
            return "VAT_NUMBER"

    except Exception as e:
        logging.warning(e)
    try:
        # Usa social security number
        if (
            len(identity_data) == 11
            and identity_data[0:3].isdigit()
            and identity_data[3] == "-"
            and identity_data[4:6].isdigit()
            and identity_data[6] == "-"
            and identity_data[7:].isdigit()
        ):
            return "USA_SOCIAL_SECURITY_NUMBER"
    except Exception as e:
        logging.warning(e)
    try:
        # turkish citizen number
        list_tc = list(map(int, str(identity_data)))
        tc10 = (sum(list_tc[0:10:2]) * 7 - sum(list_tc[1:9:2])) % 10
        tc11 = (sum(list_tc[0:9]) + tc10) % 10
        if list_tc[9] == tc10 and list_tc[10] == tc11:
            return "TURKISH_CITIZEN_NUMBER"
    except Exception as e:
        logging.warning(e)


def verify_credit_card(card_number: str) -> bool:
    """Verify credit card with luhn algorithm.

    Args:
        card_number (str): credit card string.

    Returns:
        bool:
    """
    card_number = card_number.replace(" ", "").replace("-", "")
    card_number = [int(num) for num in card_number]

    checkDigit = card_number.pop(-1)

    card_number.reverse()

    card_number = [
        num * 2 if idx % 2 == 0 else num for idx, num in enumerate(card_number)
    ]

    card_number = [
        num - 9 if idx % 2 == 0 and num > 9 else num
        for idx, num in enumerate(card_number)
    ]

    card_number.append(checkDigit)

    checkSum = sum(card_number)
    return checkSum % 10 == 0


def verify_hash(hash: str) -> bool:
    """Shanon entropy calculation.

    Args:
        hash (str): hash string.
    """
    hash2 = bytes(hash, "utf-8")
    possible = dict(((chr(x), 0) for x in range(0, 256)))
    for byte in hash2:
        possible[chr(byte)] += 1
    data_len = len(hash2)
    entropy = 0.0

    for i in possible:
        if possible[i] == 0:
            continue
        p = float(possible[i] / data_len)
        entropy -= p * math.log(p, 2)
    if entropy > 2.5:
        return True
    return False


def verify_plate(plate: str):
    pattern = re.match(r"^(?=.*[a-zA-Z])(?=.*\d).+$", plate)
    if plate.isalnum() and pattern:
        return True


def verify_domain(domains: list) -> bool:
    """Check TLD from IANA tld list. This list Updating automatically by IANA.

    Args:
        domain (str): domain name.
    """

    tmp = []
    try:
        for domain in domains:
            if domain.split(".")[-1].upper() in IANA_CONTENT:
                tmp.append({"value": domain, "type": "DOMAIN"})
    except requests.exceptions.ConnectionError as e:
        logging.warning(e)
    return tmp
