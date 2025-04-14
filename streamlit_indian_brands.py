
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

# Function to scrape Bing Search results
def scrape_bing(query, num_results=30):
    headers = {'User-Agent': 'Mozilla/5.0'}
    results = []
    for start in range(0, num_results, 10):
        url = f"https://www.bing.com/search?q={query}&first={start}"
        try:
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            search_results = soup.find_all('li', class_='b_algo')
            for item in search_results:
                title_tag = item.find('h2')
                link_tag = title_tag.find('a') if title_tag else None
                desc_tag = item.find('p')
                if link_tag:
                    results.append({
                        "title": link_tag.text.strip(),
                        "link": link_tag['href'],
                        "snippet": desc_tag.text.strip() if desc_tag else ''
                    })
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            st.warning(f"Error during scraping: {e}")
            break
    return results

# --- Streamlit UI ---
st.set_page_config(page_title="Indian Brand Finder", layout="wide")
st.title("🇮🇳 Indian Homegrown Brand Finder")
st.markdown("Search for Indian brands in any category like clothing, skincare, food, etc.")

category = st.text_input("Enter a category (e.g., clothing, skincare, food):")

if st.button("Find Brands"):
    if category:
        with st.spinner("Searching the web..."):
            query = f"homegrown Indian brands in {category}"
            search_results = scrape_bing(query)

        if search_results:
            st.success(f"Found {len(search_results)} results. Showing preview:")
            st.write(search_results[:5])  # Debug: show first 5 results

            brands = []
            for res in search_results:
                link = res["link"]
                title = res["title"].split("|")[0].split("-")[0].strip()
                if link.startswith("http"):
                    # TEMP: Skip price/contact scraping
                    brands.append(Brand(title, link, "Not scraped", "Not scraped"))

            if brands:
                df = pd.DataFrame([vars(brand) for brand in brands])
                st.dataframe(df)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("Download CSV", csv, "brands.csv", "text/csv")
            else:
                st.warning("No valid links found.")
        else:
            st.warning("No search results. Try a different keyword.")
    else:
        st.info("Please enter a category.")
