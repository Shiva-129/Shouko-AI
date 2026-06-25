import re


def normalize_supabase_url(raw: str) -> str:
    """
    Strip /rest/v1 or trailing slashes from SUPABASE_URL to get the base URL.

    Users sometimes copy the Supabase URL with ``/rest/v1`` appended from the
    project dashboard. This normalises it to the root project URL so that
    ``/auth/v1/``, ``/storage/v1/``, and other API path prefixes can be
    appended correctly.
    """
    url = raw.strip().rstrip("/")
    url = re.sub(r"/rest/v1$", "", url)
    return url
