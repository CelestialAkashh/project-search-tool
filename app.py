import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai  # OpenAI API for email generation
import re

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

        # 🔹 App Store Patterns: This is now declared outside the function
        app_store_patterns = [r"play.google.com", r"apps.apple.com"]

        # 🔹 Extract Website Data using BeautifulSoup
        def extract_project_info(url):
            # Debugging: Print the URL being processed
            st.write(f"Processing URL: {url}")

            # Skip app store URLs as they won't have useful content
            if any(re.search(pattern, url) for pattern in app_store_patterns):
                return None  # Skip app store links entirely

            if not url.startswith("http"):
                return "No website available."
            
            try:
                # Fetch and parse the page
                response = requests.get(url, timeout=5)
                
                # Check if the response is valid
                if response.status_code != 200:
                    return f"Error: Unable to reach the website (Status Code: {response.status_code})"

                soup = BeautifulSoup(response.text, "html.parser")
                raw_text = " ".join([p.text for p in soup.find_all("p")])[:2000]  # Limit to 2000 chars
                
                # If no text was extracted, handle accordingly
                if not raw_text.strip():
                    return "No significant text found on the page."

                # Return the first 1000 characters of the extracted text
                return raw_text[:1000]
            except Exception as e:
                return f"Error extracting data: {str(e)}"

        # 🔹 Process each selected project and extract info from valid website links
        for company in selected_projects:
            website_data = None

            # Iterate over available links and extract from the first valid website link
            for link in project_links[company]:
                # Process only if it's a valid non-app store link
                if not any(re.search(pattern, link) for pattern in app_store_patterns):
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
                # OpenAI API key setup
                openai.api_key = "your-openai-api-key-here"  # Set your API key here

                email_prompt = f"""
                Generate a professional business email for a client. The email should introduce our company, highlight these two selected projects, and explain how we can help them with similar solutions.
                
                Selected Projects:
                1. {selected_projects[0]} - {project_descriptions[selected_projects[0]]}
                2. {selected_projects[1]} - {project_descriptions[selected_projects[1]]}
                
                Format it professionally.
                """

                # Make API call to OpenAI to generate email
                response = openai.Completion.create(
                    engine="text-davinci-003",  # You can use the GPT-3 or GPT-4 model depending on your subscription
                    prompt=email_prompt,
                    max_tokens=500,
                    temperature=0.7
                )

                # Display the generated email
                email_content = response.choices[0].text.strip()

                st.text_area("📧 AI-Generated Email", email_content, height=350)
