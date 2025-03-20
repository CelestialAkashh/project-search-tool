import pandas as pd
import streamlit as st
import openai  # ChatGPT API
import requests
from bs4 import BeautifulSoup

# Load the file directly from GitHub
file_url = "https://github.com/CelestialAkashh/project-search-tool/raw/refs/heads/main/Copy%20of%20REAL%20Consolidated%20Project%20Portfolio.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(file_url, sheet_name="New Portfolio")  # Ensure sheet name matches

df = load_data()

st.title("🔍 AI-Powered Project Search & Email Generator")

# Search bar
search_query = st.text_input("Enter keywords (e.g., React Native, Fintech):")

# Filtering logic
filtered_df = df.copy()  # Create a copy to modify

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
    selected_projects = st.multiselect("Select up to 2 projects", filtered_df["Company Name"].tolist(), max_selections=2)

    if selected_projects:
        project_links = {}
        project_descriptions = {}

        for company in selected_projects:
            project_info = filtered_df[filtered_df["Company Name"] == company].iloc[0]
            link = project_info["Link"] if "Link" in project_info else "No website found"
            project_links[company] = link
            
            # **Web Scraping (Extract Company Info)**
            if link.startswith("http"):
                try:
                    response = requests.get(link, timeout=5)
                    soup = BeautifulSoup(response.text, "html.parser")
                    raw_text = " ".join([p.text for p in soup.find_all("p")])[:1000]  # Limit text size
                    project_descriptions[company] = raw_text if raw_text else "No details extracted."
                except Exception:
                    project_descriptions[company] = "Website not accessible."
            else:
                project_descriptions[company] = "No website available."

        # **Display Extracted Info**
        st.write("### Extracted Company Info:")
        for company, desc in project_descriptions.items():
            st.write(f"**{company}:** {desc}")
        
        # **Generate AI Email Button**
        if st.button("Generate AI-Powered Email"):
            with st.spinner("Generating email..."):
                email_draft = f"""
                Subject: Collaboration Opportunity with {selected_projects[0]} & {selected_projects[1]}
                
                Dear [Client Name],
                
                I came across your interest in fintech solutions and wanted to share two of our most successful projects:
                
                1. **{selected_projects[0]}** - {project_descriptions[selected_projects[0]]}
                2. **{selected_projects[1]}** - {project_descriptions[selected_projects[1]]}
                
                We have helped companies like yours build scalable and innovative fintech solutions. 
                Let’s discuss how we can support your goals.
                
                Best regards,  
                [Your Name]  
                [Your Company]
                """
                st.text_area("📧 AI-Generated Email", email_draft, height=300)

else:
    st.info("Enter a keyword to begin your search.")
