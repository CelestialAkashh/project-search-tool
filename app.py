import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai  # ChatGPT API

# Load the file directly from GitHub
file_url = "https://github.com/CelestialAkashh/project-search-tool/raw/refs/heads/main/Copy%20of%20REAL%20Consolidated%20Project%20Portfolio.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(file_url, sheet_name="New Portfolio")  # Change sheet name if needed

df = load_data()

st.title("🔍 Project Search Tool")

# Show available columns
st.write("### Columns in file:", df.columns.tolist())

# Search bar
search_query = st.text_input("Enter keywords (e.g., React Native, Fintech):")

# Filtering logic
if search_query:
    query = search_query.strip().lower()

    if " and " in query:
        keywords = query.split(" and ")
        filtered_df = df[df.apply(lambda row: all(kw in str(row.values).lower() for kw in keywords), axis=1)]
    
    elif " or " in query:
        keywords = query.split(" or ")
        filtered_df = df[df.apply(lambda row: any(kw in str(row.values).lower() for kw in keywords), axis=1)]
    
    else:
        filtered_df = df[df.apply(lambda row: query in str(row.values).lower(), axis=1)]

    # Display results
    if not filtered_df.empty:
        st.write(f"### Found {len(filtered_df)} matching projects:")
        st.dataframe(filtered_df)

        # Allow user to select up to 2 projects
        selected_projects = st.multiselect("Select up to 2 projects:", filtered_df["Company Name"].tolist(), max_selections=2)

        if selected_projects:
            project_info = []
            
            for project in selected_projects:
                project_details = filtered_df[filtered_df["Company Name"] == project].iloc[0]
                website_url = project_details["Link"]

                # Scrape website for more details
                def scrape_website(url):
                    try:
                        response = requests.get(url, timeout=5)
                        soup = BeautifulSoup(response.text, "html.parser")
                        text = ' '.join([p.text for p in soup.find_all('p')])  # Extract full page text
                        return text[:2000]  # Limit to 2000 chars for processing
                    except Exception as e:
                        return "Failed to retrieve details."

                raw_text = scrape_website(website_url)

                # ChatGPT API call to summarize the text
                def summarize_text(text):
                    openai.api_key = "your_openai_api_key_here"  # Replace with your key
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "system", "content": "Summarize the following project details in 3-4 sentences, focusing on its key features and value proposition."},
                                  {"role": "user", "content": text}]
                    )
                    return response["choices"][0]["message"]["content"]

                summary = summarize_text(raw_text)

                project_info.append(f"**{project}**: {summary}")

            # Display summarized project details
            st.write("### Project Summaries:")
            for info in project_info:
                st.write(info)
            
    else:
        st.warning("No projects found matching your search.")
else:
    st.info("Enter a keyword to begin your search.")
