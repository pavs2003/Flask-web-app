from flask import Flask, render_template, request, send_file
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import csv
import os
import time

app = Flask(__name__)

def init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service('chromedriver')  # chromedriver must be in root folder or PATH
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_yelp_gyms(city="Los Angeles"):
    driver = init_driver()
    search_url = f"https://www.yelp.com/search?find_desc=Gyms&find_loc={city.replace(' ', '+')}"
    driver.get(search_url)
    time.sleep(5)

    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(1.5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    gyms = []
    listings = soup.find_all("div", class_="container__09f24__21w3G")

    for listing in listings:
        name_tag = listing.find("a", class_="css-19v1rkv")
        rating_tag = listing.find("span", class_="display--inline__09f24__nqZ_W")
        address_tag = listing.find("span", class_="raw__09f24__T4Ezm")
        phone_tag = listing.find("p", class_="text__09f24__2NHRu text-color--normal__09f24__3xep9")

        if name_tag:
            gyms.append({
                "name": name_tag.text.strip(),
                "rating": rating_tag.div['aria-label'] if rating_tag and rating_tag.div else None,
                "address": address_tag.text.strip() if address_tag else None,
                "phone": phone_tag.text.strip() if phone_tag else None
            })
    return gyms

def save_to_csv(gyms, filename="gyms.csv"):
    if not gyms:
        return
    keys = gyms[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(gyms)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city = request.form['city']
        gyms = scrape_yelp_gyms(city)
        save_to_csv(gyms, "gyms.csv")
        return send_file("gyms.csv", as_attachment=True)
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
