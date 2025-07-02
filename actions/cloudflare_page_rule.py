from utils.config import CLOUDFLARE, DOMAINS
from services.cloudflare_functions import create_page_rule, delete_page_rule, update_page_rule, get_zone_id

"""
For creating and deleting a page rule, make sure to add your target url in the config.py file.
For updating a page rule, make sure to add your new target url in the config.py file.
"""

def add_cloudflare_page_rule(domains):
    if CLOUDFLARE['ADD_PAGERULE'] == True and CLOUDFLARE['ADD_A_RECORD'] == False:
        for domain in domains:
            zone_id = get_zone_id(domain)
            create_page_rule(zone_id, domain)

def delete_cloudflare_page_rule(domains):
    if CLOUDFLARE['DELETE_PAGERULE'] == True and CLOUDFLARE['DELETE_A_RECORD'] == False:
        for domain in domains:
            zone_id = get_zone_id(domain)
            delete_page_rule(zone_id, domain)

def update_cloudflare_page_rule(domains):
    if CLOUDFLARE['CHANGE_PAGERULE'] == True and CLOUDFLARE['CHANGE_A_RECORD'] == False:
        for domain in domains:
            zone_id = get_zone_id(domain)
            update_page_rule(zone_id, domain, CLOUDFLARE["NEW_TARGET_URL"])

# add_cloudflare_page_rule(DOMAINS)
# delete_cloudflare_page_rule(DOMAINS)
# update_cloudflare_page_rule(DOMAINS)