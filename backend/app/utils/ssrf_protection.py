import socket
import ipaddress
from urllib.parse import urlparse
from typing import Tuple

def is_safe_url(url: str) -> Tuple[bool, str]:
    """
    Validate URL to protect against Server-Side Request Forgery (SSRF).
    Blocks private networks, loopbacks, internal IPs, and cloud metadata services.
    """
    if not url:
        return False, "URL cannot be empty."

    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    if scheme not in ["http", "https"]:
        return False, f"Unsupported URL scheme '{scheme}'. Only HTTP and HTTPS are permitted."

    hostname = parsed.hostname
    if not hostname:
        return False, "Invalid URL: missing hostname."

    # Block localhost keywords
    if hostname.lower() in ["localhost", "127.0.0.1", "0.0.0.0", "::1"]:
        return False, "Access to localhost or loopback addresses is strictly forbidden."

    # Resolve IP address
    try:
        resolved_ip_str = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(resolved_ip_str)
    except Exception as e:
        return False, f"Could not resolve hostname '{hostname}': {str(e)}"

    # Check if IP is private, reserved, loopback, or link-local
    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
        return False, f"Access to private or internal network IP address '{ip}' is blocked."

    # Explicit check for AWS/GCP/Azure Cloud Metadata IP
    if str(ip) == "169.254.169.254":
        return False, "Access to cloud instance metadata endpoint is forbidden."

    return True, "URL is safe."

