
import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd

# Simplified Bing scraper
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
                        "Title": link_tag.text.strip(),
                        "Link": link_tag['href'],
                        "Description": desc_tag.text.strip() if desc_tag else ""
                    })
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            st.error(f"Error while scraping: {e}")
            break
    return results

# Streamlit app UI
st.set_page_config(page_title="India Brand Search Debugger", layout="wide")
st.title("🔍 Web Search Debugger for Indian Brands")
st.markdown("Try something like: **indian skincare brands**, **indian clothing startups**, **homegrown tech brands india**")

query = st.text_input("Search keyword:", value="indian clothing brands")

if st.button("Search"):
    with st.spinner("Searching Bing..."):
        results = scrape_bing(query)

    if results:
        st.success(f"✅ Found {len(results)} results!")
        df = pd.DataFrame(results)
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "search_results.csv", "text/csv")
    else:
        st.warning("❌ No search results found. Try different wording.")
