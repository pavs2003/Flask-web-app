from flask import Flask, request, render_template, send_file
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import csv
import time
import os

app = Flask(__name__)

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=chrome_options)

def scrape_yelp_gyms(city):
    driver = init_driver()
    url = f"https://www.yelp.com/search?find_desc=Gyms&find_loc={city.replace(' ', '+')}"
    driver.get(url)
    time.sleep(5)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    gyms = []
    listings = soup.find_all("div", class_="container__09f24__21w3G")

    for listing in listings:
        name_tag = listing.find("a", class_="css-19v1rkv")
        rating_tag = listing.find("span", class_="display--inline__09f24__nqZ_W")
        address_tag = listing.find("span", class_="raw__09f24__T4Ezm")
        phone_tag = listing.find("p", class_="text__09f24__2NHRu")

        if name_tag:
            gyms.append({
                "name": name_tag.text.strip(),
                "rating": rating_tag.div['aria-label'] if rating_tag and rating_tag.div else None,
                "address": address_tag.text.strip() if address_tag else None,
                "phone": phone_tag.text.strip() if phone_tag else None
            })
    return gyms

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city = request.form['city']
        gyms = scrape_yelp_gyms(city)
        filename = "gyms.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["name", "rating", "address", "phone"])
            writer.writeheader()
            writer.writerows(gyms)
        return send_file(filename, as_attachment=True)
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
