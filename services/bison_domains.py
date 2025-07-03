import os
from dotenv import load_dotenv
import requests
from utils.config import EMAILBISON
import pandas as pd

load_dotenv()

BISON_API_KEY = os.getenv("BISON_KEY")

# ---------------------- API Calls--------------------------------------

def get_bison_accounts(api_key, page=1):
    """
    This is the API call for grabbing all accounts from a Bison workspace.
    """
    try:
        url = f"https://mail.scaleyourleads.com/api/sender-emails?page={page}"
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        return data['data'], data['links']['next']
    except Exception as e:
        print(f"Error with getting bison accounts: {e}")
        return [], None

def workspace_details(api_key):
    """
    This is the API call for getting the details of a Bison workspace.
    """
    try:
        url = f"https://mail.scaleyourleads.com/api/users"
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        return data.get('data', {})
    except Exception as e:
        print(f"Error with getting workspace details: {e}")
        return []

# ---------------------- Functions --------------------------------------

def turn_into_df(domains):
    """
    This is the function for turning data from API calls or a list of dictionaries into a pandas dataframe.
    """
    df = pd.DataFrame(domains)
    return df

def extract_domains(df):
    """
    This is the function for extracting the domains from the accounts dataframe.
    """
    try:
        df_copy = df.copy()
        new_df = pd.DataFrame()
        df_copy['domain'] = (
            df_copy['email']
            .str.split('@')
            .str[1]
            .str.lower()
        )
        new_df['domain'] = df_copy['domain']
        return new_df, df_copy
    except Exception as e:
        print(f"Error with extracting domains: {e}")
        return df

def extract_tag_names(tag_list):
    """
    This is the function for extracting the tag names from the tags dataframe.
    """
    if not isinstance(tag_list, list):
        return set()
    return set(tag['name'] for tag in tag_list if 'name' in tag)

def drop_duplicate_domains(df_domains):
    """
    This is the function for dropping duplicate domains from the domains dataframe.
    """
    try:
        df_domains = df_domains.drop_duplicates(subset=['domain']).copy()
        return df_domains
    except Exception as e:
        print(f"Error with dropping duplicate domains: {e}")
        return df_domains

def get_domain_tags(df_accounts, df_domains):
    """
    This is the function for getting the domains' tags from the accounts dataframe.
    """
    try:
        df_domains = drop_duplicate_domains(df_domains)
        
        df_accounts['tag_names'] = df_accounts['tags'].apply(extract_tag_names)
        
        common_tags = df_accounts.groupby('domain')['tag_names'].apply(
            lambda tag_sets: list(set.intersection(*tag_sets)) if tag_sets.any() else []
        )
    
        df_domains.loc[:, 'tags'] = df_domains['domain'].map(common_tags)
        
        return df_domains
    except Exception as e:
        print(f"Error with getting domain tags: {e}")
        return df_domains

def add_account_count(accounts_df, domains_df):
    """
    This is the function for counting all of the accounts associated with each domain from a dataframe.
    """
    try:
        account_counts = accounts_df.groupby('domain').size().reset_index(name='accounts')
        domains_df = domains_df.merge(account_counts, on='domain', how='left')
        
        return domains_df
    except Exception as e:
        print(f"Error with adding account count: {e}")
        return domains_df

def grabbing_ESP(df_accounts, df_domains):
    """
    This is the function for grabbing the ESP of each domain from the accounts dataframe.
    """
    try:
        df_accounts['type'] = df_accounts['type'].apply(
            lambda x: 'Outlook' if x == 'microsoft_oauth' 
            else 'Google' if x == 'google_oauth' 
            else 'Other'
        )
        
        # Group by domain and get unique types for each domain
        esp_by_domain = df_accounts.groupby('domain')['type'].unique().reset_index()
        esp_by_domain['ESP'] = esp_by_domain['type'].apply(lambda x: ', '.join(x))
        
        # Merge with domains_df
        df_domains = df_domains.merge(
            esp_by_domain[['domain', 'ESP']], 
            on='domain', 
                how='left'
            )

        return df_domains
    except Exception as e:
        print(f"Error with grabbing ESP: {e}")
        return df_domains

def calculating_reply_rate(df_accounts, df_domains):
    """
    This is the function for calculating the reply rate of each domain.
    """
    try:
        replied_sum = df_accounts.groupby('domain')['unique_replied_count'].sum()
        total_sum = df_accounts.groupby('domain')['total_leads_contacted_count'].sum()
        
        reply_rate = replied_sum / total_sum
        reply_rate = reply_rate.fillna(0)
        
        reply_rate_df = reply_rate.reset_index(name='reply_rate')
        df_domains = df_domains.merge(reply_rate_df, on='domain', how='left')
        
        return df_domains
    except Exception as e:
        print(f"Error with calculating reply rate: {e}")
        return df_domains