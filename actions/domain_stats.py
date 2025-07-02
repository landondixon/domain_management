import requests
from services.bison_domains import get_bison_accounts, extract_domains, turn_into_df, get_domain_tags, add_account_count, workspace_details, grabbing_ESP, calculating_reply_rate
from services.porkbun_functions import get_dns_records, get_domains, get_nameservers, get_forwarding
from services.cloudflare_functions import get_zone_id, get_a_records
from utils.config import EMAILBISON, PORKBUN, CLOUDFLARE
import pandas as pd

def grab_all_domains(api_key):
    all_data = []
    
    data, next_page = get_bison_accounts(api_key)
    all_data.extend(data)
    
    page = 0
    while next_page:
        page += 1
        data, next_page = get_bison_accounts(api_key, page)
        all_data.extend(data)
        print(f"Page {page} processed")
    
    final_df = turn_into_df(all_data)
    df_domains, df_accounts = extract_domains(final_df)

    return df_accounts, df_domains

def calculate_bison_domain_stats(df_accounts, df_domains, api_key):
    df_domains = get_domain_tags(df_accounts, df_domains)
    df_domains = add_account_count(df_accounts, df_domains)
    workspace_info = workspace_details(api_key)
    try:
        workspaces = workspace_info.get('workspace', {})
        workspace_id = workspaces.get('id')
        workspace_name = workspaces.get('name')
    except Exception as e:
        print(f"Error getting workspace details: {e}")
        workspace_id = None
        workspace_name = None
    df_domains['workspace_id'] = workspace_id
    df_domains['workspace_name'] = workspace_name
    
    df_domains = grabbing_ESP(df_accounts, df_domains)
    df_domains = calculating_reply_rate(df_accounts, df_domains)
    return df_domains

def calculate_porkbun_domain_stats(df_domains):
    results = []
    domains = get_domains(PORKBUN['PORKBUN_KEY'], PORKBUN['PORKBUN_SECRET'])
    df_domains['in_porkbun'] = False

    for domain in domains:
        domain_name = domain.get('domain')
        status = domain.get('status')
        # Get tags
        if status == 'ACTIVE':
            porkbun_tags = domain.get('labels', [])
            tag_names = [tag.get('title') for tag in porkbun_tags if tag.get('title')]
        else:
            tag_names = []

        # Get nameservers
        nameservers = get_nameservers(domain_name, PORKBUN['PORKBUN_KEY'], PORKBUN['PORKBUN_SECRET'])

        # Get forwarding
        forwarding = get_forwarding(domain_name, PORKBUN['PORKBUN_KEY'], PORKBUN['PORKBUN_SECRET'])
        if isinstance(forwarding, list) and forwarding:
            forwarding = forwarding[0].get('location')
        else:
            forwarding = None

        # Get A record from Porkbun
        dns_records = get_dns_records(domain_name, PORKBUN['PORKBUN_KEY'], PORKBUN['PORKBUN_SECRET'])
        a_record = None
        if isinstance(dns_records, list):
            a_record = next((record.get('content') for record in dns_records if record.get('type') == 'A'), None)

        # If not found, try Cloudflare
        if not a_record and CLOUDFLARE.get("CF_API_TOKEN"):
            try:
                zone_id = get_zone_id(domain_name, CLOUDFLARE["CF_API_TOKEN"])
                a_records = get_a_records(zone_id, domain_name, CLOUDFLARE["CF_API_TOKEN"])
                if isinstance(a_records, list) and a_records:
                    a_record = a_records[0].get('content')
            except Exception as e:
                print(f"Error getting A record for {domain_name}: {e}")
                a_record = None

        # Check to see if domains are also in EmailBison
        if domain_name in df_domains['domain'].values:
            df_domains.loc[df_domains['domain'] == domain_name, 'in_porkbun'] = True
            in_bison = True
        else:
            in_bison = False
            print(f"Domain {domain_name} is not in EmailBison")

        # Collect all info for this domain
        results.append({
            'domain': domain_name,
            'status': status,
            'tag_names': tag_names,
            'nameservers': nameservers,
            'forwarding': forwarding,
            'a_record': a_record,
            'in_bison': in_bison
        })

    stats_df = pd.DataFrame(results)
    stats_df.to_csv('porkbun_domains.csv', index=False)
    return stats_df, df_domains

def find_registrar(df_domains):
    df_domains['registrar'] = None
    for domain in df_domains['domain']:
        if domain in PORKBUN['PORKBUN_DOMAINS']:
            df_domains.loc[df_domains['domain'] == domain, 'registrar'] = 'Porkbun'
        else:
            df_domains.loc[df_domains['domain'] == domain, 'registrar'] = 'EmailBison'

def main():
    df_accounts, df_domains = grab_all_domains(EMAILBISON["BISON_API_KEY"])
    print("Domains grabbed")
    df_domains = calculate_bison_domain_stats(df_accounts, df_domains, EMAILBISON["BISON_API_KEY"])
    print("Bison domains calculated")
    df_domains.to_csv('bison_domains.csv', index=False)
    print("Domains saved")

if __name__ == "__main__":
    main()