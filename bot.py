import requests
import json
import os
import random
from fake_useragent import UserAgent
import re
import time
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://faucet.vana.org/api/transactions"

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
        raise Exception("CAPTCHA request failed")
    
    request_id = result.get("request")
    
    fetch_url = f"https://2captcha.com/res.php?key={api_key}&action=get&id={request_id}&json=1"
    while True:
        result = requests.get(fetch_url).json()
        if result.get("status") == 1:
            print("Bypass CAPTCHA Sukses...")
            return result.get("request")
        elif result.get("request") != "CAPCHA_NOT_READY":
            raise Exception("Failed to solve CAPTCHA")
        time.sleep(5)

def read_proxies_from_folder(proxy_folder):
    proxies = []
    for filename in os.listdir(proxy_folder):
        with open(os.path.join(proxy_folder, filename), 'r') as file:
            for line in file:
                proxies.append(line.strip())
    return proxies

def claim_faucet(address, captcha_token, proxy, network="moksha"):
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
    return response

def main():
    address = input("Masukkan address: ")
    captcha_api_key = input("Masukkan 2CAPTCHA API Key: ")
    proxy_folder = input("Masukkan folder yang berisi daftar proxy: ")

    proxies = read_proxies_from_folder(proxy_folder)

    try:
        print("Proses Bypass CAPTCHA...")
        captcha_token = solve_captcha(captcha_api_key, "b84448b5-ba29-4e90-9451-971f40fb6861", "https://faucet.vana.org")
    except Exception as e:
        print(f"Error solving CAPTCHA: {e}")
        exit()

    proxy_index = 0
    claim_success = False

    while not claim_success:
        proxy = proxies[proxy_index]
        print(f"Menggunakan proxy: {proxy}")

        # Klaim faucet pertama
        response = claim_faucet(address, captcha_token, proxy)
        if response.status_code == 200:
            response_data = response.json()
            print("Claim Success:", response_data.get("message"))
            claim_success = True
        elif response.status_code == 400:
            print("Claim Error:", response.json().get("error"))
            print(f"Gagal klaim dengan proxy {proxy}, mencoba proxy lain...")
        else:
            print(f"Unexpected response with status code {response.status_code}, mencoba proxy lain...")

        # Ganti proxy setelah setiap percakapan
        proxy_index = (proxy_index + 1) % len(proxies)
        time.sleep(2)  # Tunggu sejenak sebelum mencoba proxy berikutnya

if __name__ == "__main__":
    main()
