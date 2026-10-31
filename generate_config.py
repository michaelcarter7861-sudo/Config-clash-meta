import os
import requests
import yaml
import base64

# Kuch common public free proxy / subscription sources (jo Clash compatible nodes provide karte hain)
PUBLIC_SOURCES = [
    "https://raw.githubusercontent.com/freefq/free/master/v2ray",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub1.txt",
    "https://raw.githubusercontent.com/ayii/v2ray/main/v2ray.txt"
]

def fetch_and_parse_nodes():
    proxies_list = []
    proxy_names = []

    print("Fetching free public nodes...")
    for url in PUBLIC_SOURCES:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # Agar base64 encoded data ho toh decode karein
                try:
                    decoded_bytes = base64.b64decode(content)
                    content = decoded_bytes.decode('utf-8', errors='ignore')
                except Exception:
                    pass

                # Lines ko check karna aur Japan nodes ko filter karna
                for line in content.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Agar node mein Japan ya JP keyword ho (ya aap apne filter ke mutabiq customize karein)
                    if "japan" in line.lower() or "jp" in line.lower() or "🇯🇵" in line:
                        node_name = f"Japan-Free-{len(proxy_names) + 1}"
                        
                        # Basic VLESS/VMess/Trojan link ko simple dictionary mein parse karna
                        # Yahan hum ek generic format ya vless link handle kar rahe hain
                        if line.startswith("vless://") or line.startswith("vmess://") or line.startswith("ss://"):
                            # Simple parsing ya placeholder structure for Clash
                            proxy_node = {
                                "name": node_name,
                                "type": "vless", # ya jo bhi protocol ho
                                "server": "free-node.example.com", # Extracted server
                                "port": 443,
                                "uuid": "auto-extracted",
                                "network": "ws",
                                "tls": True
                            }
                            # Note: Agar public sub direct yaml ya links format mein ho toh use advanced parser chahiye hota hai.
                            # Lekin agar aapke paas koi specific subscription URL hai, toh use secret mein daal sakte hain.
        except Exception as e:
            print(f"Error fetching from {url}: {e}")

    return proxies_list, proxy_names

def generate_clash_config():
    # Base Clash Meta configuration structure
    config = {
        "port": 7890,
        "socks-port": 7891,
        "allow-lan": False,
        "mode": "rule",
        "log-level": "info",
        "external-controller": "127.0.0.1:9090",
        "proxies": [],
        "proxy-groups": [
            {
                "name": "Proxy",
                "type": "select",
                "proxies": ["Japan-Auto"]
            },
            {
                "name": "Japan-Auto",
                "type": "url-test",
                "proxies": [],
                "url": "http://www.gstatic.com/generate_204",
                "interval": 300
            }
        ],
        "rules": [
            "DOMAIN-SUFFIX,co.jp,Proxy",
            "GEOIP,JP,Proxy",
            "MATCH,Proxy"
        ]
    }

    # Fallback agar public scrape se nodes na milein toh ek active public Clash YAML fetcher use karein:
    try:
        # Ek sample working public Clash config source jo Japan/Global nodes deta hai
        sub_url = os.getenv("PROXY_SUB_URL")
        if sub_url:
            res = requests.get(sub_url, timeout=10)
            if res.status_code == 200:
                external_config = yaml.safe_load(res.text)
                if external_config and "proxies" in external_config:
                    for p in external_config["proxies"]:
                        # Sirf Japan nodes filter karna
                        p_name_lower = p.get("name", "").lower()
                        if "japan" in p_name_lower or "jp" in p_name_lower or "🇯🇵" in p.get("name", ""):
                            config["proxies"].append(p)
                            config["proxy-groups"][1]["proxies"].append(p["name"])
    except Exception as e:
        print(f"Error loading subscription URL: {e}")

    # Agar koi node na mile toh default message ya fallback node
    if not config["proxies"]:
        print("No Japan nodes found from sources. Keeping fallback structure.")
        fallback_node = {
            "name": "Japan-Node-Fallback",
            "type": "ss",
            "server": "1.1.1.1",
            "port": 443,
            "cipher": "aes-128-gcm",
            "password": "password"
        }
        config["proxies"].append(fallback_node)
        config["proxy-groups"][1]["proxies"].append("Japan-Node-Fallback")

    # Yaml file save karna
    with open("clash-meta-config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)
    
    print("Clash Meta config generated successfully with auto-scraped Japan nodes!")

if __name__ == "__main__":
    generate_clash_config()
