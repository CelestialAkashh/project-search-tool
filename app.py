import pandas as pd
import streamlit as st

st.title("🔍 Project Search Tool")

# Upload Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="New Portfolio")  # Change sheet name if needed
    st.write("### Columns in file:", df.columns.tolist())

    # Rename columns (Modify if needed)
    df = df.rename(columns={
        "Company Name": "Project Name",
        "Technology Platform": "Technology",
        "Industry": "Domain",
        "Link": "Project Link"
    })

    # Search bar
    search_query = st.text_input("Enter keywords (e.g., React Native, Fintech):")

    if search_query:
        keywords = [kw.strip().lower() for kw in search_query.split(",")]
        filtered_df = df[df.apply(lambda row: any(kw in str(row.values).lower() for kw in keywords), axis=1)]

        if not filtered_df.empty:
            st.write(f"### Found {len(filtered_df)} matching projects:")
            st.dataframe(filtered_df)
        else:
            st.warning("No projects found matching your search.")
    else:
        st.info("Enter a keyword to begin your search.")

