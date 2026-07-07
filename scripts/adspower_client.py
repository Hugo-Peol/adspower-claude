"""AdsPower Local API Client.

Connects to the AdsPower Local API to manage browser profiles.
Requires AdsPower to be running with the Local API enabled.
"""

import os
import time
import requests

BASE_URL = os.environ.get("ADSPOWER_API_URL", "http://127.0.0.1:50325")
API_KEY = os.environ.get("ADSPOWER_API_KEY", "")


def _get(endpoint, params=None):
    if params is None:
        params = {}
    if API_KEY:
        params["apikey"] = API_KEY
    resp = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"AdsPower API error: {data.get('msg', 'Unknown error')}")
    return data.get("data", {})


def _post(endpoint, payload=None):
    if payload is None:
        payload = {}
    params = {}
    if API_KEY:
        params["apikey"] = API_KEY
    resp = requests.post(f"{BASE_URL}{endpoint}", json=payload, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"AdsPower API error: {data.get('msg', 'Unknown error')}")
    return data.get("data", {})


def check_connection():
    """Check if AdsPower Local API is reachable."""
    try:
        data = _get("/api/v1/status")
        print(f"Connected to AdsPower at {BASE_URL}")
        return True
    except Exception as e:
        print(f"Failed to connect to AdsPower at {BASE_URL}: {e}")
        return False


def list_profiles(page=1, page_size=10, group_id=None):
    """List browser profiles."""
    params = {"page": page, "page_size": page_size}
    if group_id:
        params["group_id"] = group_id
    data = _get("/api/v1/user/list", params)
    profiles = data.get("list", [])
    print(f"Found {len(profiles)} profiles (page {page}):")
    for p in profiles:
        print(f"  - {p.get('serial_number', '?')}: {p.get('name', 'Unnamed')} (ID: {p.get('user_id', '?')})")
    return profiles


def open_profile(user_id, headless=False):
    """Open a browser profile and return connection details."""
    params = {"user_id": user_id}
    if headless:
        params["headless"] = 1
    data = _get("/api/v1/browser/start", params)
    ws_url = data.get("ws", {}).get("puppeteer", "")
    selenium_url = data.get("ws", {}).get("selenium", "")
    print(f"Profile {user_id} opened.")
    if ws_url:
        print(f"  Puppeteer WS: {ws_url}")
    if selenium_url:
        print(f"  Selenium URL: {selenium_url}")
    return data


def close_profile(user_id):
    """Close a running browser profile."""
    data = _get("/api/v1/browser/stop", {"user_id": user_id})
    print(f"Profile {user_id} closed.")
    return data


def check_profile_status(user_id):
    """Check if a profile's browser is running."""
    data = _get("/api/v1/browser/active", {"user_id": user_id})
    status = data.get("status", "unknown")
    print(f"Profile {user_id} status: {status}")
    return data


def create_profile(name, group_id="0", domain_name=None, fingerprint_config=None):
    """Create a new browser profile."""
    payload = {
        "name": name,
        "group_id": group_id,
    }
    if domain_name:
        payload["domain_name"] = domain_name
    if fingerprint_config:
        payload["fingerprint_config"] = fingerprint_config
    data = _post("/api/v1/user/create", payload)
    user_id = data.get("id", "")
    print(f"Profile created: {name} (ID: {user_id})")
    return data


def delete_profile(user_ids):
    """Delete one or more browser profiles."""
    if isinstance(user_ids, str):
        user_ids = [user_ids]
    data = _post("/api/v1/user/delete", {"user_ids": user_ids})
    print(f"Deleted {len(user_ids)} profile(s).")
    return data


def list_groups(page=1, page_size=100):
    """List profile groups."""
    data = _get("/api/v1/group/list", {"page": page, "page_size": page_size})
    groups = data.get("list", [])
    print(f"Found {len(groups)} groups:")
    for g in groups:
        print(f"  - {g.get('group_name', 'Unnamed')} (ID: {g.get('group_id', '?')})")
    return groups


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AdsPower CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Check API connection")
    sub.add_parser("groups", help="List groups")

    lp = sub.add_parser("list", help="List profiles")
    lp.add_argument("--page", type=int, default=1)
    lp.add_argument("--size", type=int, default=10)

    op = sub.add_parser("open", help="Open a profile")
    op.add_argument("user_id")
    op.add_argument("--headless", action="store_true")

    cp = sub.add_parser("close", help="Close a profile")
    cp.add_argument("user_id")

    sp = sub.add_parser("check", help="Check profile status")
    sp.add_argument("user_id")

    cr = sub.add_parser("create", help="Create a profile")
    cr.add_argument("name")
    cr.add_argument("--group-id", default="0")

    dl = sub.add_parser("delete", help="Delete profile(s)")
    dl.add_argument("user_ids", nargs="+")

    args = parser.parse_args()

    if args.command == "status":
        check_connection()
    elif args.command == "groups":
        list_groups()
    elif args.command == "list":
        list_profiles(page=args.page, page_size=args.size)
    elif args.command == "open":
        open_profile(args.user_id, headless=args.headless)
    elif args.command == "close":
        close_profile(args.user_id)
    elif args.command == "check":
        check_profile_status(args.user_id)
    elif args.command == "create":
        create_profile(args.name, group_id=args.group_id)
    elif args.command == "delete":
        delete_profile(args.user_ids)
    else:
        parser.print_help()
