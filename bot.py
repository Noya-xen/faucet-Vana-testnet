import requests
import json
from fake_useragent import UserAgent
import re
import time
import random
import urllib3

# Menonaktifkan peringatan SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL endpoint API
url = "https://faucet.vana.org/api/transactions"

# Inisialisasi user agent
ua = UserAgent()

headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,id;q=0.7",
    "content-type": "application/json",
    "origin": "https://faucet.vana.org",
    "referer": "https://faucet.vana.org/moksha",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": ua.chrome,
}

# Daftar proxy langsung dalam script
proxy_list = [
    "http://47.88.59.79:82",
    "http://95.217.196.186:21899",
    "http://198.89.123.216:6758"

    # Tambahkan proxy lain di sini
]

def solve_captcha(api_key, sitekey, domain):
    captcha_url = "https://2captcha.com/in.php"
    payload = {
        "key": api_key,
        "method": "hcaptcha",
        "sitekey": sitekey,
        "pageurl": domain,
        "json": 1,
    }

    response = requests.post(captcha_url, data=payload)
    result = response.json()
    
    if result.get("status") != 1:
        raise Exception(f"CAPTCHA request failed with status: {result.get('status')}, error: {result.get('request')}")
    
    request_id = result.get("request")
    
    fetch_url = f"https://2captcha.com/res.php?key={api_key}&action=get&id={request_id}&json=1"
    while True:
        result = requests.get(fetch_url).json()
        if result.get("status") == 1:
            print("Bypass CAPTCHA Sukses...")
            return result.get("request")
        elif result.get("request") != "CAPCHA_NOT_READY":
            raise Exception("Failed to solve CAPTCHA, error: " + result.get("request"))
        time.sleep(5)

def main():
    address = input("Masukkan address: ")
    captcha_api_key = input("Masukkan 2CAPTCHA API Key: ")

    network = "moksha"
    
    # Coba klaim faucet untuk setiap proxy
    for proxy in proxy_list:
        print(f"Menggunakan proxy: {proxy}")
        
        try:
            print("Proses Bypass CAPTCHA...")
            # Memecahkan CAPTCHA untuk setiap proxy yang digunakan
            captcha_token = solve_captcha(captcha_api_key, "b84448b5-ba29-4e90-9451-971f40fb6861", "https://faucet.vana.org")
        except Exception as e:
            print(f"Error solving CAPTCHA: {e}")
            continue  # Jika gagal memecahkan CAPTCHA, coba dengan proxy berikutnya
        
        payload = {
            "address": address,
            "captcha": captcha_token,
            "network": network,
        }

        proxies = {
            "http": proxy,
            "https": proxy,
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload), proxies=proxies, verify=False)

        if response.status_code == 200:
            response_data = response.json()
            print("Claim Success:", response_data.get("message"))
            break  # Klaim berhasil, keluar dari loop
        elif response.status_code == 400:
            print("Claim Error:", response.json().get("error"))
        else:
            print(f"Unexpected response with proxy {proxy}: {response.status_code}, {response.text}")
        
        # Tunggu sebentar sebelum mencoba proxy berikutnya
        time.sleep(5)

if __name__ == "__main__":
    main()
