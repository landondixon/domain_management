import os
from dotenv import load_dotenv

load_dotenv()

PORKBUN = {
    "PORKBUN_KEY": os.getenv("PORKBUN_KEY"),
    "PORKBUN_SECRET": os.getenv("PORKBUN_SECRET"),
    "ADD_FORWARDING": False,
    "CHANGE_FORWARDING": False,
    "DELETE_FORWARDING": False
}

CLOUDFLARE = {
    "CF_EMAIL": os.getenv("CF_EMAIL"),
    "CF_API_TOKEN": os.getenv("CF_API_TOKEN"),
    "CF_GLOBAL_KEY": os.getenv("CF_GLOBAL_KEY"),
    "USE_API_TOKEN": True,
    "IP": "192.0.2.1",
    "TARGET_URL": "https://sylforfun.com/",
    "NEW_TARGET_URL": "https://sylfeelingfunnow.com/", ## For updating the page rule
    "ADD_PAGERULE": False,
    "CHANGE_PAGERULE": False,
    "DELETE_PAGERULE": False,
    "ADD_A_RECORD": False,
    "CHANGE_A_RECORD": False,
    "DELETE_A_RECORD": False,
    "CHANGE_NAMESERVERS": False
}

EMAILGUARD = {
    "EMAILGUARD_TOKEN": os.getenv("EG_API_KEY"),
    "EG_IP_USAGE": False,
    "ADD_MASKING_PROXY": False,
    "CHANGE_MASKING_PROXY": False,
    "PRIMARY_DOMAIN": "sylnow.com"
}

EMAILBISON = {
    "BISON_API_KEY": os.getenv("BISON_KEY")
}

DOMAINS = ["sylnow.com"]