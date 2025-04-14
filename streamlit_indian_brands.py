
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import time
import random
import pandas as pd

# Define a Brand class
class Brand:
    def __init__(self, name, website, price_info, contact_info):
        self.name = name
        self.website = website
        self.price_info = price_info
        self.contact_info = contact_info

# Function to scrape Google Search results
def scrape_google(query, num_results=30):
    headers = {"User-Agent": "Mozilla/5.0"}
    results = []
    for start in range(0, num_results, 10):
        url = f"https://www.google.com/search?q={query}&start={start}"
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            search_results = soup.find_all("div", class_="g")
            for result in search_results:
                link_tag = result.find("a")
                if link_tag and '/url?q=' in link_tag['href']:
                    link = link_tag['href'].split('/url?q=')[1].split('&')[0]
                    title = result.find("h3").text if result.find("h3") else "No title"
                    snippet = result.find("div", class_="VwiC3b").text if result.find("div", class_="VwiC3b") else "No description"
                    results.append({"title": title, "link": link, "snippet": snippet})
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print("Scraping failed:", e)
            break
    return results

# Try to extract pricing or contact info from website
def get_details_from_site(url):
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        text = soup.get_text().lower()
        # Find pricing info
        price_matches = re.findall(r'₹[0-9,]+', text)
        price_info = price_matches[0] if price_matches else "Not found"
        # Contact info
        email = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        contact_info = email[0] if email else "Not found"
        return price_info, contact_info
    except:
        return "Not found", "Not found"

# Convert results to Brand objects
def extract_brands(results):
    brands = []
    for result in results:
        link = result["link"]
        title = result["title"].split("|")[0].split("-")[0].strip()
        if ".in" in link:
            price, contact = get_details_from_site(link)
            brands.append(Brand(title, link, price, contact))
    return brands

# --- Streamlit UI ---
st.set_page_config(page_title="Indian Brand Finder", layout="wide")
st.title("🇮🇳 Indian Homegrown Brand Finder")
category = st.text_input("Enter a category (e.g., clothing, skincare, food):")

if st.button("Find Brands"):
    if category:
        with st.spinner("Searching the web..."):
            query = f"homegrown Indian brands in {category} site:.in"
            search_results = scrape_google(query)
            brands = extract_brands(search_results)

        if brands:
            st.success(f"Found {len(brands)} Indian brands in {category}")
            df = pd.DataFrame([vars(brand) for brand in brands])
            st.dataframe(df)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, "brands.csv", "text/csv")
        else:
            st.warning("No brands found. Try another category.")
    else:
        st.info("Please enter a category.")
