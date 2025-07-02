import requests
from dotenv import load_dotenv
import os
from utils.config import EMAILGUARD

load_dotenv()

EMAILGUARD_TOKEN = EMAILGUARD["EMAILGUARD_TOKEN"]

def get_proxy_ip():
    resp = requests.get(
        "https://app.emailguard.io/api/v1/domain-masking-proxies/ip",
        headers={"Authorization": f"Bearer {EMAILGUARD_TOKEN}"}
    )
    resp.raise_for_status()
    return resp.json()["data"]["ip_address"]

def create_masking_proxy(masking_domain, primary_domain):
    url = "https://app.emailguard.io/api/v1/domain-masking-proxies"
    data = {
        "masking_domain": f"{masking_domain}",
        "primary_domain": f"{primary_domain}"
    }
    headers = {
        "Authorization": f"Bearer {EMAILGUARD_TOKEN}",
        "Content-Type": "application/json"
    }
    resp = requests.post(url, json=data, headers=headers)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        print("Response content:", resp.content.decode())
        raise
    data = resp.json().get("data", {})
    return data

def get_redirect_url(domain):
    url = "https://app.emailguard.io/api/v1/hosted-domain-redirects"
    headers = {
        "Authorization": f"Bearer {EMAILGUARD_TOKEN}",
        "Content-Type": "application/json"
    }
    resp = requests.get(url, headers=headers)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        print("Response content:", resp.content.decode())
        raise
    data = resp.json().get("data", {})
    return data

def delete_redirect(uuid):
    url = f"https://app.emailguard.io/api/v1/hosted-domain-redirects/{uuid}"
    headers = {
        "Authorization": f"Bearer {EMAILGUARD_TOKEN}",
        "Content-Type": "application/json"
    }
    resp = requests.delete(url, headers=headers)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        print("Response content:", resp.content.decode())
        raise
    return resp.json()

def create_redirect(domain, new_url):
    url = "https://app.emailguard.io/api/v1/hosted-domain-redirects"
    data = {
        "domain": f"{domain}",
        "redirect": f"{new_url}"
    }
    headers = {
        "Authorization": f"Bearer {EMAILGUARD_TOKEN}",
        "Content-Type": "application/json"
    }
    resp = requests.post(url, json=data, headers=headers)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        print("Response content:", resp.content.decode())
        raise
    data = resp.json().get("data", {})
    return data