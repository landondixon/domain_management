import os
from dotenv import load_dotenv

load_dotenv()

PORKBUN = {
    "PORKBUN_KEY": os.getenv("PORKBUN_KEY"), # The API key for Porkbun
    "PORKBUN_SECRET": os.getenv("PORKBUN_SECRET"), # The API secret for Porkbun
    "ADD_FORWARDING": False, # For adding forwarding in Porkbun
    "CHANGE_FORWARDING": False, # For changing forwarding in Porkbun
    "DELETE_FORWARDING": False # For deleting forwarding in Porkbun
}

CLOUDFLARE = {
    "CF_EMAIL": os.getenv("CF_EMAIL"), # Your CF email
    "CF_API_TOKEN": os.getenv("CF_API_TOKEN"), # The API token value for CF
    "CF_GLOBAL_KEY": os.getenv("CF_GLOBAL_KEY"), # The global key value for CF
    "USE_API_TOKEN": True, # For using API token in CF instead of global key
    "IP": "192.0.2.1", # Manually set IP Address for A Record
    "TARGET_URL": "https://sylforfun.com/", # For adding or deleting page rule/forwarding
    "NEW_TARGET_URL": "https://sylfeelingfunnow.com/", # For updating the page rule
    "ADD_PAGERULE": False, # For adding a page rule
    "CHANGE_PAGERULE": False, # For changing a page rule
    "DELETE_PAGERULE": False, # For deleting a page rule
    "ADD_A_RECORD": False, # For adding an A Record
    "CHANGE_A_RECORD": False, # For changing an A Record
    "DELETE_A_RECORD": False, # For deleting an A Record
    "CHANGE_NAMESERVERS": False # For changing nameservers
}

EMAILGUARD = {
    "EMAILGUARD_TOKEN": os.getenv("EG_API_KEY"), # The API key for EG
    "EG_IP_USAGE": False, # For using IP in EmailGuard
    "ADD_MASKING_PROXY": False, # For adding a masking proxy in EG
    "CHANGE_MASKING_PROXY": False, # For changing a masking proxy in EG
    "PRIMARY_DOMAIN": "sylnow.com" # The primary domain for EG
}

EMAILBISON = {
    "BISON_API_KEY": os.getenv("BISON_KEY") # The API key for a workspace in EmailBison
}

DOMAINS = ["sylnow.com"] # The domains to be used in the script (representation of the domains they choose to use)