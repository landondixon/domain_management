from services.porkbun_functions import add_forwarding, delete_forwarding, get_forwarding
from utils.config import PORKBUN, DOMAINS

def add_forwarding_logic(domains, new_url):
    """
    This is the workflow for adding a forwarding to a domain in Porkbun.
    """
    if PORKBUN['ADD_FORWARDING'] == True:
        for domain in domains:
            add_forwarding(domain, new_url, PORKBUN["PORKBUN_KEY"], PORKBUN["PORKBUN_SECRET"])

def delete_forwarding_logic(domains):
    """
    This is the workflow for deleting a forwarding from a domain in Porkbun.
    """
    if PORKBUN['DELETE_FORWARDING'] == True:
        for domain in domains:
            domain_data = get_forwarding(domain, PORKBUN["PORKBUN_KEY"], PORKBUN["PORKBUN_SECRET"])
            record_id = domain_data[0].get("id")
            delete_forwarding(domain, record_id, PORKBUN["PORKBUN_KEY"], PORKBUN["PORKBUN_SECRET"])

def update_forwarding_logic(domains, new_url):
    """
    This is the workflow for updating a forwarding for a domain in Porkbun.
    """
    if PORKBUN['UPDATE_FORWARDING'] == True:
        for domain in domains:
            domain_data = get_forwarding(domain, PORKBUN["PORKBUN_KEY"], PORKBUN["PORKBUN_SECRET"])
            record_id = domain_data[0].get("id")
            delete_forwarding(domain, record_id, PORKBUN["PORKBUN_KEY"], PORKBUN["PORKBUN_SECRET"])
            add_forwarding(domain, new_url, PORKBUN["PORKBUN_KEY"], PORKBUN["PORKBUN_SECRET"])

# add_forwarding_logic(DOMAINS, "https://sylnow.com/")
# delete_forwarding_logic(DOMAINS)
# update_forwarding_logic(DOMAINS, "https://sylnow.com/")