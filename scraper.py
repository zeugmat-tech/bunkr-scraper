import os
import re
import json
import requests
import cloudscraper

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyk5mypVMTQyMTmGMhGm_MgKjSaHc6GlM6jironfXMqX3PNG1eQGjZ98gm_8Cf8bX7H/exec"

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
)

def run_scraper():
    print("Google Sheets'ten sayfa aralığı alınıyor...")
    
    # 1. Sheets'ten mevcut B1 ve C1 değerlerini çek
    baslangic_sayfa = 1
    bitis_sayfa = 5
    try:
        res = requests.get(WEB_APP_URL)
        if res.status_code == 200:
            config = res.json()
            baslangic_sayfa = config.get("baslangic", 1)
            bitis_sayfa = config.get("bitis", 5)
            print(f"Tarama Aralığı Alındı: Sayfa {baslangic_sayfa} -> {bitis_sayfa}")
    except Exception as e:
        print(f"Ayar çekilemedi, varsayılan (1-5) kullanılıyor: {e}")

    base_url = "https://balbums.st/albums"
    toplanan_linkler = []
    
    # 2. Belirtilen aralıktaki sayfaları Cloudflare aşarak tara
    for page in range(baslangic_sayfa, bitis_sayfa + 1):
        url = f"{base_url}?page={page}"
        try:
            response = scraper.get(url, timeout=15)
            if response.status_code == 200:
                html = response.text
                matches = re.findall(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE)
                sayfa_yeni = 0
                for rel_link in matches:
                    if rel_link.startswith("#") or rel_link.startswith("javascript:"):
                        continue
                    tam_link = rel_link if rel_link.startswith("http") else f"https://balbums.st{rel_link}"
                    
                    if any(x in tam_link for x in ["/a/", "/v/", "/i/", "/d/", "/f/", "/album/"]):
                        toplanan_linkler.append({"link": tam_link, "sayfa": page})
                        sayfa_yeni += 1
                print(f"Sayfa {page} çekildi. Bulunan link: {sayfa_yeni}")
            else:
                print(f"Sayfa {page} Hatası: HTTP {response.status_code}")
        except Exception as e:
            print(f"Sayfa {page} İstek Hatası: {str(e)}")

    # 3. Sonuçları Google Sheets Web App'e gönder
    payload = {
        "linkler": toplanan_linkler,
        "baslangic_sayfa": baslangic_sayfa,
        "bitis_sayfa": bitis_sayfa,
        "son_sayfa": bitis_sayfa
    }
    headers = {'Content-Type': 'application/json'}
    res = requests.post(WEB_APP_URL, data=json.dumps(payload), headers=headers)
    print(f"Google Sheets Kayıt Yanıtı: {res.text}")

if __name__ == "__main__":
    run_scraper()
