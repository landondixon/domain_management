import requests
import sys
import time
import os
from utils.config import CLOUDFLARE
from dotenv import load_dotenv

load_dotenv()

API_BASE = "https://api.cloudflare.com/client/v4"
CF_EMAIL = CLOUDFLARE["CF_EMAIL"]
CF_GLOBAL_KEY = CLOUDFLARE["CF_API_TOKEN"]
TARGET_URL = CLOUDFLARE["TARGET_URL"]

BASE = "https://api.cloudflare.com/client/v4"

def api(method: str, path: str, **kw):
    headers = get_headers(CLOUDFLARE['CF_API_TOKEN'])
    r = requests.request(method, f"{BASE}{path}", headers=headers, **kw)
    data = r.json() if r.headers.get("content-type","").startswith("application/json") else {}
    if not r.ok or not data.get("success", False):
        sys.exit(f"API error {r.status_code}: {r.text}")
    return data["result"]

def get_zone_id(domain, api_token):
    url = f"{API_BASE}/zones?name={domain}"
    resp = requests.get(url, headers=get_headers(api_token))
    resp.raise_for_status()
    result = resp.json()
    if result["success"] and result["result"]:
        return result["result"][0]["id"]
    else:
        raise Exception(f"Zone ID not found for {domain}")

def get_headers(api_token):
    """Return headers based on config preference."""
    if CLOUDFLARE["USE_API_TOKEN"]:
        token = CLOUDFLARE["CF_API_TOKEN"]
        if not token:
            raise ValueError("CF_API_TOKEN required when USE_API_TOKEN=true")
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    else:
        key = CLOUDFLARE["CF_GLOBAL_KEY"]
        email = CLOUDFLARE["CF_EMAIL"]
        if not key or not email:
            raise ValueError("CF_GLOBAL_KEY and CF_EMAIL required when USE_API_TOKEN=false")
        return {
            "X-Auth-Email": email,
            "X-Auth-Key": key,
            "Content-Type": "application/json"
        }

# ─── NameServers ───────────────────────────────────────────────────────── #
def first_account_id(api_token):
    """Return the first account the token has access to."""
    r = requests.get(f"{API_BASE}/accounts", headers=get_headers(api_token))
    r.raise_for_status()
    result = r.json().get("result", [])
    if not result or not isinstance(result, list):
        sys.exit("Could not retrieve account ID – check credentials: No accounts found in API response")
    try:
        return result[0]["id"]
    except (IndexError, KeyError, TypeError) as e:
        sys.exit(f"Could not retrieve account ID – check credentials: Could not retrieve account ID from API response: {e}")

def check_zone_exists(domain: str, api_token: str) -> tuple[bool, dict]:
    """
    Check if a zone exists in Cloudflare and return zone details if it does.
    
    Returns:
        tuple: (exists: bool, zone_data: dict or None)
    """
    r = requests.get(f"{API_BASE}/zones", headers=get_headers(api_token), params={"name": domain})
    r.raise_for_status()
    result_list = r.json().get("result", [])
    
    if result_list and isinstance(result_list, list):
        return True, result_list[0]
    return False, None

def create_new_zone(account_id: str, domain: str, api_token: str) -> dict:
    """
    Create a new zone in Cloudflare.
    
    Returns:
        dict: Zone data with nameservers
    """
    payload = {"name": domain, "account": {"id": account_id}, "type": "full"}
    r = requests.post(f"{API_BASE}/zones", headers=get_headers(api_token), json=payload)
    r.raise_for_status()
    
    result = r.json().get("result")
    if not result or "name_servers" not in result:
        raise RuntimeError(f"Zone creation for '{domain}' did not return nameservers")
    
    return result

def create_zone(account_id: str, domain: str, api_token: str) -> tuple[str, str]:
    """
    Create the zone (type=full) or, if it already exists in this account,
    fetch its current nameservers.
    
    Returns:
        tuple: (nameserver1, nameserver2)
    """
    # First check if zone exists
    exists, zone_data = check_zone_exists(domain, api_token)
    
    if exists:
        result = zone_data
    else:
        # Try to create the zone
        try:
            result = create_new_zone(account_id, domain, api_token)
        except requests.exceptions.HTTPError as e:
            # Handle case where zone exists in another account
            if e.response.status_code in [409, 400]:
                exists, zone_data = check_zone_exists(domain, api_token)
                if exists:
                    result = zone_data
                else:
                    raise RuntimeError(f"Zone '{domain}' exists but could not retrieve its details")
            else:
                raise

    name_servers = result.get("name_servers")
    if not name_servers or not isinstance(name_servers, list) or len(name_servers) < 2:
        raise RuntimeError(f"Could not retrieve nameservers for '{domain}'")
    
    return name_servers[0], name_servers[1]

# ─── Page Rule (301 redirect) ────────────────────────────────────────────── #
def page_rule_payload(domain: str):
    return {
        "targets": [
            {
                "target": "url",
                "constraint": {
                    "operator": "matches",
                    "value": f"*{domain}/*"
                },
            }
        ],
        "actions": [
            {
                "id": "forwarding_url",
                "value": {
                    "url": TARGET_URL,
                    "status_code": 301,
                },
            }
        ],
        "status": "active",
        "priority": 1,
    }

def create_page_rule(zone_id, domain):
    payload = page_rule_payload(domain)
    rules = api("GET", f"/zones/{zone_id}/pagerules")
    if any(r["targets"][0]["constraint"]["value"] == payload["targets"][0]["constraint"]["value"]
           for r in rules):
        print(f"[{domain}] page rule already exists – skipping")
        return
    api("POST", f"/zones/{zone_id}/pagerules", json=payload)
    print(f"[{domain}] 301 page rule created")

# ─── Page Rule helpers: UPDATE & DELETE ─────────────────────────────────── #
def _find_redirect_rules(zone_id: str, domain: str):
    """
    Return a list of Page Rules whose URL-match pattern is '*{domain}/*'
    (the same pattern created by ensure_page_rule()).
    """
    target_value = f"*{domain}/*"
    rules = api("GET", f"/zones/{zone_id}/pagerules")
    return [r for r in rules
            if r["targets"][0]["constraint"]["value"] == target_value]

def update_page_rule(zone_id: str, domain: str, new_url: str, status_code: int = 301):
    """
    Change the forwarding destination (and/or status code) of every
    Page Rule that matches '*{domain}/*'.
    """
    rules = _find_redirect_rules(zone_id, domain)
    if not rules:
        print(f"[{domain}] No Page Rule to update – nothing changed")
        return
    
    print(f"Which rules do you want to update?")
    for r in rules:
        print(f"[{r['id']}] {r['targets'][0]['constraint']['value']} {r['actions'][0]['value']['url']}")
    
    print("Enter the ID of the rule you want to update:")
    rule_id = input().lower().strip()
    
    selected_rule = None
    for r in rules:
        if r["id"] == rule_id:
            selected_rule = r
            break
    
    if not selected_rule:
        print(f"[{domain}] Invalid rule ID – nothing changed")
        return
    
    payload = {
        "targets": selected_rule["targets"],          # keep same match pattern
        "actions": [{
            "id": "forwarding_url",
            "value": {
                "url": new_url,
                "status_code": status_code,
            },
        }],
        "status": selected_rule["status"],            # keep enabled/disabled
        "priority": selected_rule["priority"],        # keep original priority
    }
    
    try:
        api("PUT", f"/zones/{zone_id}/pagerules/{rule_id}", json=payload)
        print(f"[{domain}] Updated Page Rule {rule_id}")
    except Exception as e:
        print(f"[{domain}] Error updating Page Rule {rule_id}: {e}")

def delete_page_rule(zone_id: str, domain: str):
    """
    Remove every Page Rule whose pattern is '*{domain}/*'.
    """
    rules = _find_redirect_rules(zone_id, domain)
    if not rules:
        print(f"[{domain}] Page Rule does not exist – OK")
        return
    print(f"Which rules do you want to delete?")
    for r in rules:
        print(f"[{r['id']}] {r['targets'][0]['constraint']['value']} {r['actions'][0]['value']['url']}")
    print("Enter the ID of the rule you want to delete:")
    rule_id = input().lower().strip()
    try:
        api("DELETE", f"/zones/{zone_id}/pagerules/{rule_id}")
        print(f"[{domain}] Deleted Page Rule {rule_id}")
    except Exception as e:
        print(f"[{domain}] Error deleting Page Rule {rule_id}: {e}")

# ─── A Records ────────────────────────────────────────────────────────────── #
def create_a_record(zone_id, domain, ip, proxied=True):
    url = f"{API_BASE}/zones/{zone_id}/dns_records"
    data = {
        "type": "A",
        "name": domain,
        "content": ip,
        "ttl": 600,
        "proxied": proxied
    }
    resp = requests.post(url, json=data, headers=get_headers(CLOUDFLARE['CF_API_TOKEN']))
    resp.raise_for_status()
    return resp.json()

# ─── DNS helpers: UPDATE & DELETE  ───────────────────────────────────────── #
def get_a_records(zone_id: str, zone_name: str, api_token: str):
    """
    Return the list of A-record objects for the root of the zone.
    Cloudflare stores the "@" record internally under the full zone name,
    so we search with name == zone_name.
    """
    params = {"type": "A", "name": zone_name}
    return api("GET", f"/zones/{zone_id}/dns_records", params=params)

def update_a_record(zone_id: str, zone_name: str, new_ip: str,
                    proxied: bool = True):
    """
    Replace the content (IP) -- and optionally TTL / proxy flag --
    of every root-level A record that already exists for this zone.
    """
    records = get_a_records(zone_id, zone_name, CLOUDFLARE['CF_API_TOKEN'])
    if not records:
        print(f"[{zone_name}] No A record to update (nothing changed)")
        return

    for r in records:
        payload = {
            "type": "A",
            "name": r["name"],          # root (@) record
            "content": new_ip,
            "ttl": 600,
            "proxied": proxied,
        }
        api("PUT", f"/zones/{zone_id}/dns_records/{r['id']}", json=payload)
        print(f"[{zone_name}] A record {r['id']} ➔ {new_ip} (proxied={proxied})")

def delete_a_record(zone_id: str, zone_name: str):
    """
    Delete every root-level A record for this zone (if any).
    """
    records = get_a_records(zone_id, zone_name, CLOUDFLARE['CF_API_TOKEN'])
    if not records:
        print(f"[{zone_name}] A record does not exist – OK")
        return

    for r in records:
        api("DELETE", f"/zones/{zone_id}/dns_records/{r['id']}")
        print(f"[{zone_name}] Deleted A record {r['id']}")

def a_record_exists(zone_id, domain):
    url = f"{API_BASE}/zones/{zone_id}/dns_records?type=A&name={domain}"
    headers = get_headers(CLOUDFLARE['CF_API_TOKEN'])
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    records = resp.json().get("result", [])
    for record in records:
        if record["type"] == "A" and record["name"] == domain:
            return True
    return False

def add_domains_to_cloudflare(domains):
    """Add multiple domains to Cloudflare and return their nameservers."""
    if not CLOUDFLARE['CF_API_TOKEN'] or len(CLOUDFLARE['CF_API_TOKEN']) < 10:
        raise ValueError("❌  Set your Cloudflare API Token first!\n"
                        "   1. Get your token from: https://dash.cloudflare.com/profile/api-tokens")
    
    cloudflare_domains_nameservers = {}
    summary = add_to_cloudflare(domains, CLOUDFLARE['CF_API_TOKEN'])
    for d in summary:
        cloudflare_domains_nameservers[d[0]] = [d[1], d[2]]
    return cloudflare_domains_nameservers 

def get_cloudflare_domains_nameservers():
    pass