
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# 🗂️ Known blogs listing Indian homegrown brands by category
BLOG_SOURCES = {
    "skincare": [
        "https://www.thechannel46.com/style/beauty/20-homegrown-skincare-brands-to-support-in-2023/"
    ],
    "fashion": [
        "https://www.lifestyleasia.com/ind/style/fashion/indian-homegrown-fashion-brands-to-shop/"
    ],
    "food": [
        "https://www.femina.in/life/food/10-homegrown-indian-food-brands-to-try-right-now-228093.html"
    ]
}

# 🌐 Get links from blog
def extract_brand_links_from_blog(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    brand_links = []
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]
            if href.startswith("http") and len(text) > 3 and not any(x in href for x in ["facebook", "twitter", "instagram", "mailto"]):
                brand_links.append((text, href))
    except Exception as e:
        print(f"Error fetching blog: {e}")
    return brand_links

# 📧 Try to extract contact info and ₹ pricing
def extract_contact_and_price(url):
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        text = soup.get_text().lower()
        email_match = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        price_match = re.findall(r"₹[0-9,]+", text)
        return email_match[0] if email_match else "Not found", price_match[0] if price_match else "Not found"
    except:
        return "Not found", "Not found"

# 🚀 Streamlit App
st.set_page_config(page_title="Indian Homegrown Brands", layout="wide")
st.title("🇮🇳 Indian Homegrown Brand Explorer")
st.markdown("Get real Indian brands with website, email & pricing info.")

category = st.selectbox("Choose a category:", list(BLOG_SOURCES.keys()))

if st.button("Find Indian Brands"):
    with st.spinner("Fetching Indian brand websites from trusted sources..."):
        brand_data = []
        for blog_url in BLOG_SOURCES[category]:
            links = extract_brand_links_from_blog(blog_url)
            for name, link in links:
                email, price = extract_contact_and_price(link)
                brand_data.append({
                    "Brand Name": name,
                    "Website": link,
                    "Contact Email": email,
                    "Sample Price": price
                })

    if brand_data:
        df = pd.DataFrame(brand_data).drop_duplicates(subset="Website")
        st.success(f"Found {len(df)} Indian brands in {category.capitalize()}")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download as CSV", csv, "indian_brands_list.csv", "text/csv")
    else:
        st.warning("No brands found. Try another category.")
