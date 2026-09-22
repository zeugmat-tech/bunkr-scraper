import os
import re
import json
import requests
import cloudscraper

# Google Apps Script Web App URL
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyk5mypVMTQyMTmGMhGm_MgKjSaHc6GlM6jironfXMqX3PNG1eQGjZ98gm_8Cf8bX7H/exec"

# Cloudflare bypass edici scraper
scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
)

def run_scraper():
    # 1. Mevcut ayarları ve sayfa aralığını Sheets'ten almak yerine baştan / kaldığı yerden tetikliyoruz
    # Başlangıçta kaçıncı sayfadan başlanacağını manuel veya dinamik verebiliriz.
    # Örnek: Her seferinde Sheets'teki B1/C1 hücrelerini takip edecek yapıyı çalıştırıyoruz.

    print("Scraper başlatılıyor...")
    
    # Hedef URL ve sayfa aralığı (Örnek: 1-5 arası, Apps Script sonrasını güncelleyecek)
    # Varsayılan başlangıç adresimiz:
    base_url = "https://balbums.st/albums"
    
    # Apps Script'e göndereceğimiz veriler
    toplanan_linkler = []
    
    # 5 sayfalık paketler halinde tarayalım
    # İlerlemeyi duruma göre dinamikleştiriyoruz
    print("Cloudflare koruması geçiliyor...")
    
    for page in range(1, 6):
        url = f"{base_url}?page={page}"
        try:
            response = scraper.get(url, timeout=15)
            if response.status_code == 200:
                html = response.text
                # Albüm linklerini yakala (/a/, /v/, /i/, /d/, /f/, /album/)
                matches = re.findall(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE)
                sayfa_yeni = 0
                for rel_link in matches:
                    if rel_link.startswith("#") or rel_link.startswith("javascript:"):
                        continue
                    tam_link = rel_link if rel_link.startswith("http") else f"https://balbums.st{rel_link}"
                    
                    if any(x in tam_link for x in ["/a/", "/v/", "/i/", "/d/", "/f/", "/album/"]):
                        toplanan_linkler.append({"link": tam_link, "sayfa": page})
                        sayfa_yeni += 1
                print(f"Sayfa {page} başarıyla çekildi. Bulunan link: {sayfa_yeni}")
            else:
                print(f"Sayfa {page} Hatası: HTTP {response.status_code}")
        except Exception as e:
            print(f"Sayfa {page} İstek Hatası: {str(e)}")

    # 2. Bulunan Linkleri Google Sheets Web App'e Gönder
    if toplanan_linkler:
        payload = {
            "linkler": toplanan_linkler,
            "son_sayfa": 5
        }
        headers = {'Content-Type': 'application/json'}
        res = requests.post(WEB_APP_URL, data=json.dumps(payload), headers=headers)
        print(f"Google Sheets Yanıtı: {res.text}")
    else:
        print("Yeni link bulunamadı.")

if __name__ == "__main__":
    run_scraper()
