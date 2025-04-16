import requests
import re
import streamlit as st

st.title("E-commerce Search")

# total products
resp = requests.get("http://127.0.0.1:8000/count")
count = resp.json()['total']
st.write(f"Total products available: {count}")

search_query = st.text_input("Search for products:")

def highlight_text(text, query_terms):
    """Highlights query terms in the text with markdown formatting"""
    highlighted = text
    for term in query_terms:
        if term.strip():
            pattern = re.compile(re.escape(term.strip()), re.IGNORECASE)
            highlighted = pattern.sub(f"<span style='background-color: yellow; color: black;'>{term.strip()}</span>", highlighted)
    return highlighted

if search_query:
    query_terms = search_query.split()
    
    response = requests.get("http://127.0.0.1:8000/search", params={"query": search_query})
    if response.status_code == 200:
        results = response.json()
        if results:
            st.write(f"Results for '{search_query}':")
            st.write(f"Total products found: {len(results)}")

            for product in results:

                highlighted_name = highlight_text(product['product_name'], query_terms)
                highlighted_description = highlight_text(product['description'], query_terms)
                
                st.markdown(f"- **{highlighted_name}**: {highlighted_description} (${product['price']})", unsafe_allow_html=True)
        else:
            st.write("No products found.")
    else:
        st.write("Error fetching search results.")
