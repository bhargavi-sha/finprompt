import streamlit as st
import pandas as pd
from openai import OpenAI

# This function generates the AI description for a single row of data
def generate_description(row, client):
    """
    Creates a prompt from invoice data and calls the OpenAI API to get a summary.
    """
    try:
        # 1. Create a clear prompt for the AI model
        prompt = f"Create a short, human-readable transaction summary for an accounting entry with the following details: Vendor='{row['Vendor']}', Amount='{row['Amount']}', Date='{row['Date']}'."

        # 2. Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # As specified in the PRD [cite: 19]
            messages=[{"role": "user", "content": prompt}],
            max_tokens=25  # Keep the description concise
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Return an error message if the API call fails
        return f"Error generating description: {e}"

# This function converts a DataFrame to a CSV file for downloading
@st.cache_data
def convert_df_to_csv(dataframe):
    """
    Converts a pandas DataFrame to a UTF-8 encoded CSV file.
    """
    return dataframe.to_csv(index=False).encode('utf-8')

# --- Main Application UI ---

# STEP 1: Set up the title and the file uploader widget
st.title("FinPrompt - AI Invoice Description Writer")
st.write("Upload your invoice file (CSV or XLSX) to automatically generate transaction summaries.")

uploaded_file = st.file_uploader("Choose an invoice file", type=['csv', 'xlsx'])

# This block runs only after a file has been uploaded
if uploaded_file is not None:
    try:
        # STEP 2: Read the uploaded file using pandas
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("File uploaded and read successfully!")
        st.write("### Original Data")
        st.dataframe(df)

        # Create a button to start the AI generation process
        if st.button("Generate AI Descriptions"):
            # STEP 3: Connect to the AI and generate descriptions for each row
            
            # IMPORTANT: Replace "YOUR_OPENAI_API_KEY" with your actual key.
            # For better security, use Streamlit's secrets management for real projects.
            client = OpenAI(api_key="OPENAI_API_KEY")

            with st.spinner("Generating descriptions... Please wait."):
                # Create a new column by applying the generation function to each row
                df['AI_Summary'] = df.apply(lambda row: generate_description(row, client), axis=1)

            st.write("### Data with AI-Generated Summaries")
            st.dataframe(df)

            # STEP 4: Create the download button for the final results
            csv_data = convert_df_to_csv(df)

            st.download_button(
                label="Download Data as CSV",
                data=csv_data,
                file_name='invoice_with_ai_summaries.csv',
                mime='text/csv',
            )

    except Exception as e:
        # Handle potential errors during file processing or AI generation
        st.error(f"An error occurred: {e}")