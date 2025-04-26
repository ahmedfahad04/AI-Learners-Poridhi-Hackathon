import requests
import re
import streamlit as st
import os

# Determine backend URL via environment variable, defaulting to localhost
BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

CONFIDENCE_LEVEL = 0.65

def highlight_text(text, query_terms):
    """Highlights query terms in the text with markdown formatting"""
    
    highlighted = text
    for term in query_terms:
        if term.strip():
            pattern = re.compile(re.escape(term.strip()), re.IGNORECASE)
            highlighted = pattern.sub(f"<span style='background-color: yellow; color: black;'>{term.strip()}</span>", highlighted)
    return highlighted

def search_products(query):
    response = requests.get(f"{BASE_URL}/search", params={"query": query})
    if response.status_code == 200:

        results = [product for product in response.json() if product['score'] > CONFIDENCE_LEVEL]
        if not results:
            st.write("No products found.")
            return None
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    else:
        st.error("Error fetching search results.")
        return None

def display_search_results(search_query, results):
    if results:
        st.write(f"Results for '{search_query}':")
        st.write(f"Total products found: {len(results)}")
        query_terms = search_query.split()
        for product in results:
            highlighted_name = highlight_text(product['name'], query_terms)
            highlighted_description = highlight_text(product['description'], query_terms)
            st.markdown(f"- **{highlighted_name}**: {highlighted_description} (${product['price']}) => Confidence: {product['score']}", unsafe_allow_html=True)
    else:
        st.write("No products found.")

def upload_csv_to_qdrant(uploaded_file):
    if uploaded_file is not None:
        with st.spinner("Uploading and processing file..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
            response = requests.post(f"{BASE_URL}/upload_csv", files=files)
            if response.status_code == 200:
                st.success(response.json().get("message", "Upload successful!"))
            else:
                st.error(f"Upload failed: {response.text}")

def main():
    global CONFIDENCE_LEVEL
    st.title("E-commerce Search")

    # total products
    resp = requests.get(f"{BASE_URL}/count")
    count = resp.json()
    st.write(f"Total products available: {count}")

    # Sidebar for CSV upload and confidence level
    st.sidebar.header("FastSearch BD")
    with st.sidebar:
        st.subheader("Upload Product CSV to Qdrant")
        uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
        upload_csv_to_qdrant(uploaded_file)
        st.subheader("Set Confidence Level")
        confidence_input = st.text_input("Confidence threshold (0-1)", value=str(CONFIDENCE_LEVEL))
        try:
            CONFIDENCE_LEVEL = float(confidence_input)
        except ValueError:
            st.warning("Please enter a valid number for confidence level.")

    search_query = st.text_input("Search for products:")
    if search_query:
        results = search_products(search_query)
        display_search_results(search_query, results)

if __name__ == "__main__":
    main()
