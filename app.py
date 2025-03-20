import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup

# 🔹 Load Excel File from GitHub
file_url = "https://github.com/CelestialAkashh/project-search-tool/raw/refs/heads/main/Copy%20of%20REAL%20Consolidated%20Project%20Portfolio.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(file_url, sheet_name="New Portfolio")

df = load_data()

st.title("🚀 AI-Powered Project Search & Email Generator")

# 🔹 Search bar
search_query = st.text_input("Enter keywords (e.g., React Native, Fintech):")

# 🔹 Filtering logic
filtered_df = pd.DataFrame()

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

# 🔹 Display Search Results
if not filtered_df.empty:
    st.write(f"### Found {len(filtered_df)} matching projects:")
    st.dataframe(filtered_df)

    # 🔹 Project Selection
    selected_projects = st.multiselect("Select up to 2 projects", filtered_df["Company Name"].tolist(), max_selections=2)

    if selected_projects:
        project_links = {}
        project_descriptions = {}

        for company in selected_projects:
            project_info = filtered_df[filtered_df["Company Name"] == company].iloc[0]
            links = project_info.get("Link", "").split(",")  # Split multiple links by commas
            project_links[company] = [link.strip() for link in links if 'http' in link]  # Only consider valid links

        # 🔹 Filter out app store links and process valid website links only
        app_store_patterns = [r"play.google.com", r"apps.apple.com"]

        # 🔹 Extract Website Data using BeautifulSoup
        def extract_project_info(url):
            if any(pattern in url for pattern in app_store_patterns):
                return None  # Skip app store links entirely

            if not url.startswith("http"):
                return "Invalid URL"

            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    raw_text = " ".join([p.text for p in soup.find_all("p")])[:2000]  # Limit to 2000 chars
                    if not raw_text.strip():
                        return "No significant text found on the page."
                    return raw_text[:1000]
                else:
                    return f"Error: Unable to reach the website (Status Code: {response.status_code})"
            except Exception as e:
                return f"Error extracting data: {str(e)}"

        # 🔹 Process each selected project and extract info from valid website links
        for company in selected_projects:
            website_data = None

            # Iterate over available links and extract from the first valid website link
            for link in project_links[company]:
                if not any(pattern in link for pattern in app_store_patterns):
                    website_data = extract_project_info(link)
                    if website_data:
                        break  # Stop after the first valid website is processed

            # If no valid website was found, set the description to 'No valid website available.'
            project_descriptions[company] = website_data or "No valid website available."

        # 🔹 Display Extracted Info
        st.write("### Extracted Project Info:")
        for company, desc in project_descriptions.items():
            st.write(f"**{company}:** {desc}")

        # 🔹 Generate AI Email
        if st.button("Generate AI-Powered Email"):
            with st.spinner("Generating email..."):
                email_prompt = f"""
                Generate a professional business email for a client. The email should introduce our company, highlight these two selected projects, and explain how we can help them with similar solutions.
                
                Selected Projects:
                1. {selected_projects[0]} - {project_descriptions[selected_projects[0]]}
                2. {selected_projects[1]} - {project_descriptions[selected_projects[1]]}
                
                Format it professionally.
                """

                # Display the generated email (in this case, just return the prompt)
                st.text_area("📧 AI-Generated Email", email_prompt, height=350)
