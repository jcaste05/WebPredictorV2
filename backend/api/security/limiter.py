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
    ip = ""
    if request.headers.get("x-forwarded-for"):
        print("DEBUG: x-forwarded-for header found")
        xff = request.headers.get("x-forwarded-for")
        ip = xff.split(",")[0].strip()
    elif request.headers.get("x-real-ip"):
        print("DEBUG: x-real-ip header found")
        xrip = request.headers.get("x-real-ip")
        ip = xrip.strip()

    if len(ip) > 100:
        ip == ""
    if ip.count(":") == 1 and ip.split(":")[1].isdigit():
        ip = ip.split(":")[0]

    if ip == "":
        ip = "0.0.0.0"
    print(f"DEBUG: Using hashed IP address {hash_ip(ip)} for rate limiting")
    return hash_ip(ip)