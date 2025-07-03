from utils.config import CLOUDFLARE, DOMAINS
from services.cloudflare_functions import create_a_record, delete_a_record, update_a_record, get_zone_id, check_zone_exists, create_new_zone, first_account_id, a_record_exists
import requests

def add_cloudflare_A_records(domains):
    """
    This is the workflow for adding an A record to a domain in Cloudflare.
    """
    if CLOUDFLARE['ADD_A_RECORD'] == True and CLOUDFLARE['ADD_PAGERULE'] == False:
        for domain in domains:
            exists, zone_data = check_zone_exists(domain, CLOUDFLARE['CF_API_TOKEN'])
            if not exists:
                print(f"Creating new zone for {domain}")
                zone_data = create_new_zone(first_account_id(CLOUDFLARE['CF_API_TOKEN']), domain, CLOUDFLARE['CF_API_TOKEN'])
                print(f"New zone created for {domain}")
                print(zone_data)
            zone_id = zone_data['id']
            try:
                create_a_record(zone_id, domain, CLOUDFLARE['IP'])
            except requests.exceptions.HTTPError as e:
                print(f"Error creating A record: {e}")
                print(f"Response: {e.response.text}")
                raise

def delete_cloudflare_A_records(domains):
    """
    This is the workflow for deleting an A record from a domain in Cloudflare.
    """
    if CLOUDFLARE['DELETE_A_RECORD'] == True and CLOUDFLARE['DELETE_PAGERULE'] == False:
        for domain in domains:
            zone_id = get_zone_id(domain)
            exists = a_record_exists(zone_id, domain)
            if exists:
                delete_a_record(zone_id, domain)
                print(f"Deleted A record for {domain}")
            else:
                print(f"A record for {domain} does not exist")

def update_cloudflare_A_records(domains):
    """
    This is the workflow for updating an A record for a domain in Cloudflare.
    """
    if CLOUDFLARE['CHANGE_A_RECORD'] == True and CLOUDFLARE['CHANGE_PAGERULE'] == False:
        for domain in domains:
            zone_id = get_zone_id(domain)
            exists = a_record_exists(zone_id, domain)
            if not exists:
                print(f"A record for {domain} does not exist")
                continue
            print(f"Updating A record for {domain}")
            update_a_record(zone_id, domain, CLOUDFLARE['IP'])

# add_cloudflare_A_records(DOMAINS)
# delete_cloudflare_A_records(DOMAINS)
# update_cloudflare_A_records(DOMAINS)