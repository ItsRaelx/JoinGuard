import base64
import hashlib
import hmac
from datetime import datetime, timedelta
from os import getenv
from urllib.parse import urlencode, quote_plus

from dateutil import parser

SECRET_KEY = getenv("SIGN_SECRET")


def generate_signed_url(base_url: str, data: dict, expiry_days: int = 7):
    expiry_date = datetime.utcnow() + timedelta(days=expiry_days)
    data_to_sign = data.copy()
    data_to_sign['expiry'] = expiry_date.isoformat()
    query_string = urlencode(data_to_sign, quote_via=quote_plus)

    signature = hmac.new(SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).digest()
    signature_encoded = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()

    return f"{base_url}?{query_string}&signature={signature_encoded}"


def verify_signed_url(params: dict) -> bool:
    try:
        signature = params.pop('signature')
        expiry = params.get('expiry')

        if not expiry:
            return False

        expiry_date = parser.parse(expiry)
        if expiry_date < datetime.utcnow():
            return False

        query_string = urlencode(params, quote_via=quote_plus)
        expected_signature = hmac.new(SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).digest()
        expected_signature_encoded = base64.urlsafe_b64encode(expected_signature).rstrip(b'=').decode()

        return hmac.compare_digest(signature, expected_signature_encoded)
    except Exception:
        return False
