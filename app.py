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

# 🔹 Show available columns
st.write("### Available Columns:", df.columns.tolist())

# 🔹 Search bar
search_query = st.text_input("Enter keywords (e.g., React Native, Fintech):")

# 🔹 Filtering logic
filtered_df = pd.DataFrame()  # Empty DataFrame initially

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
            link = project_info.get("Link", "No website found")
            project_links[company] = link
            
            # 🔹 Extract Website Data
            def extract_project_info(url):
                if not url.startswith("http"):
                    return "No website available."
                try:
                    response = requests.get(url, timeout=5)
                    soup = BeautifulSoup(response.text, "html.parser")
                    raw_text = " ".join([p.text for p in soup.find_all("p")])[:2000]  # Limit to 2000 chars
                    return raw_text if raw_text else "No detailed content available."
                except Exception:
                    return "Website not accessible."

            # 🔹 Process each selected project
            for company in selected_projects:
                project_descriptions[company] = extract_project_info(project_links[company])

        # 🔹 Display Extracted Info
        st.write("### Extracted Project Info:")
        for company, desc in project_descriptions.items():
            st.write(f"**{company}:** {desc}")

        # 🔹 Generate AI Email (Using Free GPT-4o)
        if "messages" not in st.session_state:
            st.session_state["messages"] = []

        if st.button("Generate AI-Powered Email"):
            with st.chat_message("assistant"):
                st.markdown("Generating email...")

            # 🧠 AI Prompt for Email Generation
            prompt = f"""
            Write a professional business email introducing our company to a client. 
            Highlight how we helped these two projects and explain how we can assist them similarly.
            1. {selected_projects[0]} - {project_descriptions[selected_projects[0]]}
            2. {selected_projects[1]} - {project_descriptions[selected_projects[1]]}
            
            The email should be engaging, formal, and have a clear call-to-action.
            """

            # 🔹 Get AI Response Using Streamlit’s Free GPT-4o
            st.session_state["messages"].append({"role": "user", "content": prompt})
            st.chat_input("Type here to chat with AI...")  # Enable GPT-4o free chat

else:
    st.info("Enter a keyword to begin your search.")
