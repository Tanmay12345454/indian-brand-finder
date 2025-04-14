
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import time
import pandas as pd

# Utility: Extract all links from a blog article page
def extract_brand_links_from_article(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    brand_links = []
    try:
        res = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            if href.startswith("http") and len(text) > 2:
                brand_links.append((text, href))
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
    return brand_links

# Utility: Try to get contact info + price from a brand site
def extract_contact_and_price(url):
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        text = soup.get_text().lower()
        email_match = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        contact = email_match[0] if email_match else "Not found"
        price_match = re.findall(r'₹[0-9,]+', text)
        price = price_match[0] if price_match else "Not found"
        return contact, price
    except:
        return "Not found", "Not found"

# Step 1: Search Bing for blog articles listing Indian brands
def search_bing_for_articles(category, num_results=10):
    headers = {'User-Agent': 'Mozilla/5.0'}
    query = f"top indian homegrown {category} brands site:.in OR site:.com"
    results = []
    for start in range(0, num_results, 10):
        url = f"https://www.bing.com/search?q={query}&first={start}"
        try:
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            for item in soup.find_all("li", class_="b_algo"):
                h2 = item.find("h2")
                a = h2.find("a") if h2 else None
                if a and a["href"].startswith("http"):
                    results.append(a["href"])
        except Exception as e:
            st.warning(f"Bing scraping failed: {e}")
    return results

# Streamlit App
st.set_page_config(page_title="Indian Brand Extractor", layout="wide")
st.title("🇮🇳 Indian Brand Finder")
st.markdown("Searches blogs/articles listing Indian brands and pulls brand names, links, contact info & pricing.")

category = st.text_input("Enter product category (e.g., skincare, fashion, food):")

if st.button("Find Brands"):
    if category:
        with st.spinner("🔍 Searching for blogs and extracting brand data..."):
            blog_links = search_bing_for_articles(category)
            st.info(f"Found {len(blog_links)} potential blog articles.")

            all_brands = []
            for blog_url in blog_links[:3]:  # Limit for speed
                brand_links = extract_brand_links_from_article(blog_url)
                for name, link in brand_links:
                    if link.startswith("http"):
                        email, price = extract_contact_and_price(link)
                        all_brands.append({
                            "Brand Name": name,
                            "Website": link,
                            "Contact Info": email,
                            "Sample Price": price
                        })

            if all_brands:
                df = pd.DataFrame(all_brands).drop_duplicates(subset="Website")
                st.success(f"✅ Found {len(df)} potential brand sites!")
                st.dataframe(df)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("Download CSV", csv, "indian_brands_extracted.csv", "text/csv")
            else:
                st.warning("No brand links extracted. Try another category or wording.")
    else:
        st.info("Please enter a category above.")
