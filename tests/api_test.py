from ocr_miner.api.cloudflare_turnstile import check_turnstile

import unittest
from unittest.mock import patch
import json
from fastapi.testclient import TestClient

from ocr_miner.api.ocr_miner_api import APP

client = TestClient(APP)


expected_data = json.loads(
    {
        "success": True,
        "error-codes": [],
        "challenge_ts": "2023-08-26T12:55:43.873Z",
        "hostname": "127.0.0.1",
        "action": "",
        "cdata": "",
        "metadata": {"interactive": False},
    }
)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.templates.TemplateResponse("index.html", {"request": ""})
