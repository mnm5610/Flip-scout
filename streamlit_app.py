import requests
from bs4 import BeautifulSoup
import openai
import streamlit as st
import os

# Load OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

def scrape_craigslist(search_term="comic books", location="sfbay"):
    base_url = f"https://{location}.craigslist.org/search/sss?query={search_term.replace(' ', '+')}"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    listings = []
    for post in soup.find_all('li', class_='result-row')[:10]:  # Limit to first 10 results
        title = post.find('a', class_='result-title').text
        price = post.find('span', class_='result-price')
        price = price.text if price else "N/A"
        url = post.find('a', class_='result-title')['href']
        listings.append({"title": title, "price": price, "url": url})
    return listings

def analyze_listing(title, price):
    prompt = f"""This item is listed as: "{title}" for {price}.
    Based on resale trends, recent eBay sales, and collector demand, is this a good flip?
    Give a 2-sentence summary with a rough profit estimate."""
    
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

# --- Streamlit UI ---
st.title("Smart Flip Scout")

search_term = st.text_input("Search term", "comic books")
location = st.text_input("Craigslist location (e.g., sfbay, newyork, chicago)", "sfbay")

if st.button("Scout Listings"):
    with st.spinner("Searching Craigslist and analyzing..."):
        listings = scrape_craigslist(search_term, location)
        for listing in listings:
            listing['analysis'] = analyze_listing(listing['title'], listing['price'])

        for listing in listings:
            st.subheader(listing['title'])
            st.write(f"**Price:** {listing['price']}")
            st.write(f"**URL:** [View Listing]({listing['url']})")
            st.write(f"**GPT Flip Analysis:** {listing['analysis']}")
