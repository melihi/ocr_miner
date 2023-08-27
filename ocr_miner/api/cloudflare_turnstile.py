from ocr_miner.config import CLOUDFLARE_TURNSTILE
import json
import logging
import requests


def check_turnstile(key: str) -> list:
    """Check request with CloudFlare turnstile.
    Request for the Private Access Token challenge.

    Args:
        key (str): Cloudflare client key

    Raises:
        HTTPException: _description_
    """
    # confirm CloudFlare turnstile
    cf_data = {"secret": CLOUDFLARE_TURNSTILE, "response": key}
    cf_validate = json.loads(
        requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data=cf_data,
        ).text
    )
    logging.warning(cf_validate)

    if cf_validate["success"] != True:
        return [False, cf_validate["error-codes"]]

    return [
        True,
    ]
