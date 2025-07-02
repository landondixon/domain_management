import pandas as pd
from utils.config import PORKBUN, CLOUDFLARE
from services.porkbun_functions import get_all_domains_with_nameservers, update_domain_nameservers
from services.cloudflare_functions import add_domains_to_cloudflare

def update_cloudflare_nameservers():
    if CLOUDFLARE['CHANGE_NAMESERVERS'] == True:
        print("📋 Getting Porkbun domains and nameservers...")
        porkbun_data = get_all_domains_with_nameservers()
        domains_to_add = []
        for domain in CLOUDFLARE['DOMAINS']:
            if domain not in porkbun_data:
                print(f"❌ {domain} is not in Porkbun")
                continue
            else:
                print(f"✅ {domain} is in Porkbun")
        
        print("☁️  Adding domains to Cloudflare...")
        domains = list(porkbun_data.keys())
        cloudflare_data = add_domains_to_cloudflare(domains)
        
        print("🔍 Comparing nameservers...")
        domain_classification = {}
        for domain in domains:
            domain_classification[domain] = [
                domain, 
                'porkbun', 
                porkbun_data[domain], 
                cloudflare_data[domain]
            ]

        for domain in domains:
            if porkbun_data[domain] == cloudflare_data[domain]:
                print(f"✅ {domain} has matching nameservers")
                continue
            else:
                print(f"❌ {domain} has different nameservers")
                domains_to_add.append(domain)
        
        df = pd.DataFrame(domain_classification.values(), 
                        columns=['domain', 'service', 'other_ns', 'cloudflare_ns'])
        df['same_ns'] = df['other_ns'] == df['cloudflare_ns']
        
        update_nameservers_if_needed(df)
        
        return df

def update_nameservers_if_needed(df):
    """Update nameservers for domains that don't match Cloudflare."""
    domains_to_update = df[df['same_ns'] == False]
    
    if len(domains_to_update) == 0:
        print("✅ All domains already have matching nameservers!")
        return
    
    print(f"🔄 Updating nameservers for {len(domains_to_update)} domains...")
    
    for index, row in domains_to_update.iterrows():
        print(f"   → Updating {row['domain']}")
        update_domain_nameservers(row['domain'], row['cloudflare_ns'])

# update_cloudflare_nameservers()