from services.emailguard import get_proxy_ip, create_masking_proxy, delete_redirect, get_redirect_url
from services.cloudflare_functions import get_zone_id, create_a_record, a_record_exists, update_a_record, update_page_rule
from utils.config import DOMAINS, PRIMARY_DOMAIN, EMAILGUARD
import time

def adding_eg_a_record():
    """
    This is the workflow for using an A record from EmailGuard.
    """
    if EMAILGUARD['ADD_MASKING_PROXY'] == True:
        ip = get_proxy_ip()
        zone_ids = {}
        for i, domain in enumerate(DOMAINS, 1):
            try:
                zone_id = get_zone_id(domain)
                zone_ids[domain] = zone_id
                if a_record_exists(zone_id, domain, ip):
                    print(f"    ✅ A record already exists for {domain}")
                else:
                    create_a_record(zone_id, domain, ip)
                    print(f"    ✅ A record created for {domain}")
                    successful_records += 1
            except Exception as e:
                print(f"    ❌ Failed to process {domain}: {e}")
                continue
        proxies = []
        for i, domain in enumerate(DOMAINS, 1):
            try:
                data = create_masking_proxy(domain, PRIMARY_DOMAIN)
                if data.get("success") is False and "correct IP address" in data.get("message", ""):
                    print(f"    ⏳ Domain ready, proxy setup in progress...")
                    proxies.append((domain, "waiting"))
                    waiting_count += 1
                else:
                    status = data.get("status", "unknown")
                    print(f"    ✅ Proxy created with status: {status}")
                    proxies.append((domain, status))
            except Exception as e:
                print(f"    ❌ Failed to create proxy for {domain}: {e}")
                proxies.append((domain, "error"))

        if waiting_count > 0:
            print(f"\n⏰ Waiting 60 seconds for {waiting_count} proxies to become active...")
            print("    (This is normal - DNS propagation takes time)")
            time.sleep(60)

            retries = 0
            max_retries = 3
            
            while retries < max_retries:
                waiting_domains = [domain for domain, status in proxies if status == "waiting"]
                if not waiting_domains:
                    break
                    
                retries += 1
                print(f"\n🔄 Retry {retries}/{max_retries}: Checking {len(waiting_domains)} pending proxies...")
                print("-" * 30)
                
                if retries < max_retries:
                    time.sleep(30)

                updated_proxies = []
                for domain, status in proxies:
                    if status == "waiting":
                        print(f"    Checking {domain}...")
                        try:
                            data = create_masking_proxy(domain, PRIMARY_DOMAIN)
                            if data.get("success") is False and "correct IP address" in data.get("message", ""):
                                print(f"    ⏳ Still setting up...")
                                updated_proxies.append((domain, "waiting"))
                            else:
                                new_status = data.get("status", "connected")
                                print(f"    ✅ Proxy is now {new_status}!")
                                updated_proxies.append((domain, new_status))
                        except Exception as e:
                            print(f"    ❌ Error checking {domain}: {e}")
                            updated_proxies.append((domain, "error"))
                    else:
                        # Keep domains that are already successful
                        updated_proxies.append((domain, status))
                
                proxies = updated_proxies

        print(f"\n🎉 Domain Masking Setup Complete!")
        print("=" * 50)
        
        connected = [domain for domain, status in proxies if status in ["connected", "active"]]
        waiting = [domain for domain, status in proxies if status == "waiting"]
        errors = [domain for domain, status in proxies if status == "error"]
        
        if connected:
            print(f"✅ Successfully connected ({len(connected)}):")
            for domain in connected:
                print(f"    • {domain}")
        
        if waiting:
            print(f"\n⏳ Still setting up ({len(waiting)}):")
            for domain in waiting:
                print(f"    • {domain} (may need more time)")
        
        if errors:
            print(f"\n❌ Errors ({len(errors)}):")
            for domain in errors:
                print(f"    • {domain}")
        
        print(f"\n📈 Total Success Rate: {len(connected)}/{len(DOMAINS)} domains ({len(connected)/len(DOMAINS)*100:.0f}%)")
        
        if waiting:
            print(f"\n💡 Tip: Domains still setting up will typically complete within 5-10 minutes.")
            print("    You can check their status in the EmailGuard dashboard.")
                
def changing_eg_redirect():
    if EMAILGUARD['CHANGE_MASKING_PROXY'] == True:
        for domain in DOMAINS:
            zone_id = get_zone_id(domain)
            update_a_record(zone_id, domain)
            update_page_rule(zone_id, domain)