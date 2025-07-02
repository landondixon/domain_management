import os
from dotenv import load_dotenv
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from utils.config import PORKBUN, DOMAINS, CLOUDFLARE

load_dotenv()

PORKBUN_API_KEY = PORKBUN["PORKBUN_KEY"]
PORKBUN_SECRET_API_KEY = PORKBUN["PORKBUN_SECRET"]

def get_domains(api_key, secret_api_key, start=0):
    try:
        url = "https://api.porkbun.com/api/json/v3/domain/listAll"
        payload = {
            "secretapikey": secret_api_key,
            "apikey": api_key,
            "start": str(start),
            "includeLabels": "yes"
        }
        response = requests.post(url, json=payload)
        data = response.json()
        return data['domains']
    except Exception as e:
        print(f"Error with getting porkbun domains: {e}")
        return []

def get_nameservers(domain, api_key, secret_api_key):
    try:
        url = f"https://api.porkbun.com/api/json/v3/domain/getNs/{domain}"
        payload = {
            "secretapikey": secret_api_key,
            "apikey": api_key
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"HTTP {response.status_code} error getting nameservers for {domain}")
            return 'error'
        
        data = response.json()
        
        if data['status'] == "SUCCESS":
            return data['ns']
        else:
            error_msg = data.get('message', 'Unknown API error')
            print(f"API Error for {domain}: {error_msg}")
            return 'api_error'
    except Exception as e:
        print(f"Unexpected error for {domain}: {str(e)}")
        return 'unexpected_error'

def update_nameservers(domain, nameservers, api_key, secret_api_key):
    try:
        url = f"https://api.porkbun.com/api/json/v3/domain/updateNs/{domain}"
        payload = {
            "secretapikey": secret_api_key,
            "apikey": api_key,
            "ns": nameservers
            }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"HTTP {response.status_code} error updating nameservers for {domain}")
            return 'error'
        return response.json().get('status')
    except Exception as e:
        print(f"Unexpected error for {domain}: {str(e)}")
        return 'unexpected_error'

def add_forwarding(domain, new_url, api_key, secret_api_key):
    try:
        url = f"https://api.porkbun.com/api/json/v3/domain/addUrlForward/{domain}"
        payload = {
            "secretapikey": secret_api_key,
            "apikey": api_key,
            "subdomain": "",
            "location": new_url,
            "type": "temporary",
            "includePath": "no",
            "wildcard": "yes"
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"HTTP {response.status_code} error adding forwarding for {domain}")
            return 'error'
        return response.json().get('status')
    except Exception as e:
        print(f"Unexpected error for {domain}: {str(e)}")
        return 'unexpected_error'

def get_forwarding(domain, api_key, secret_api_key):
    try:
        url = f"https://api.porkbun.com/api/json/v3/domain/getUrlForwarding/{domain}"
        payload = {
            "secretapikey": secret_api_key,
            "apikey": api_key
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"HTTP {response.status_code} error getting forwarding for {domain}")
            return 'error'
        return response.json().get('forwards')
    except Exception as e:
        print(f"Unexpected error for {domain}: {str(e)}")
        return 'unexpected_error'

def delete_forwarding(domain, record_id, api_key, secret_api_key):
    try:
        url = f"https://api.porkbun.com/api/json/v3/domain/deleteUrlForward/{domain}/{record_id}"
        payload = {
            "secretapikey": secret_api_key,
            "apikey": api_key
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"HTTP {response.status_code} error deleting forwarding for {domain}")
            return 'error'
        return response.json().get('status')
    except Exception as e:
        print(f"Unexpected error for {domain}: {str(e)}")
        return 'unexpected_error'

def get_porkbun_nameservers(domain):
    time.sleep(1.2)
    nameservers = get_nameservers(domain)
    if nameservers == 'error' or nameservers == 'api_error' or nameservers == 'unexpected_error':
        ns_list = []
    else:
        ns_list = nameservers if isinstance(nameservers, list) else []
    print(f"Processed {domain}")
    return domain, ns_list

def get_all_domains_with_nameservers():
    """Get all Porkbun domains with their current nameservers."""
    porkbun_domains_nameservers = {}
    for domain in DOMAINS:
        domain, nameservers = get_porkbun_nameservers(domain)
        porkbun_domains_nameservers[domain] = nameservers
    return porkbun_domains_nameservers

def update_domain_nameservers(domain, nameservers):
    """Update nameservers for a specific domain."""
    return update_nameservers(domain, nameservers, PORKBUN['PORKBUN_KEY'], PORKBUN['PORKBUN_SECRET'])

def get_dns_records(domain, api_key, secret_api_key):
    """Get DNS records for a specific domain."""
    try:
        url = f"https://api.porkbun.com/api/json/v3/dns/retrieve/{domain}"
        payload = {
            "secretapikey": secret_api_key,
            "apikey": api_key
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"HTTP {response.status_code} error getting DNS records for {domain}")
            return 'error'
        results = response.json()
        dns = results.get('records')
        return dns
    except Exception as e:
        print(f"Unexpected error for dns records for {domain}: {str(e)}")
        return 'unexpected_error'