import base64
import hashlib
import hmac

from fastapi import Request

from backend.api.config import IP_KEY_SALT


def hash_ip(ip: str) -> str:
    """
    Return a hashed representation of the given IP address.
    """
    key_bytes = IP_KEY_SALT.encode("utf-8")
    ip_bytes = ip.encode("utf-8")
    digest = hmac.new(key_bytes, ip_bytes, hashlib.sha256).digest()
    b64hash = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return b64hash


async def real_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        ip_hashed = hash_ip(xff.split(",")[0].strip())
        return ip_hashed
    xrip = request.headers.get("x-real-ip")
    if xrip:
        ip_hashed = hash_ip(xrip.strip())
        return ip_hashed

    return hash_ip(request.client.host)
