import os
import requests
import yaml

# Aap yahan koi bhi public free subscription URL ya proxy list source de sakte hain
SUBSCRIPTION_URL = os.getenv("PROXY_SUB_URL", "YOUR_DEFAULT_PUBLIC_URL_HERE")

def generate_clash_config():
    print("Fetching proxy nodes...")
    
    # Base Clash Meta configuration structure[span_2](start_span)[span_2](end_span)
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

    try:
        # Agar aapke paas koi subscription link hai toh yahan request jayegi
        # Yahan aap apne parsing logic ke mutabiq Japan nodes add kar sakte hain
        # Example ke liye ek placeholder node add kiya gaya hai:
        sample_japan_node = {
            "name": "Japan-Node-Free",
            "type": "vless",
            "server": "japan.example.com",
            "port": 443,
            "uuid": "your-uuid-here",
            "network": "ws",
            "tls": True
        }
        
        # Filtering logic: Sirf Japan nodes ko proxies aur proxy-groups mein dalna
        config["proxies"].append(sample_japan_node)
        config["proxy-groups"][1]["proxies"].append("Japan-Node-Free")

    except Exception as e:
        print(f"Error fetching or parsing nodes: {e}")

    # Yaml file save karna[span_3](start_span)[span_3](end_span)
    with open("clash-meta-config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)
    
    print("Clash Meta config generated successfully for Japan location!")

if __name__ == "__main__":
    generate_config_config = generate_clash_config()
