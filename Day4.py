from google import genai
import streamlit as st
import PyPDF2
from PIL import Image

# --- Initialize Robix client ---
robix = genai.Client(api_key="AIzaSyDPlZu16-MRLt7CyCEzJCsXhMyAAOvTi98")

st.title("My Own RobixGPT 🤖")
st.header("RobixGPT 🤖")

# --- User input ---
question = st.text_input("Ask Anything")

uploaded_files = st.file_uploader(
    "Upload multiple files:",
    accept_multiple_files=True,
    type=["txt", "csv", "pdf", "png", "jpg", "jpeg"]
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} file(s) uploaded successfully!")
    for f in uploaded_files:
        st.write(f"📄 {f.name}")
else:
    st.info("No files uploaded yet.")

# --- ONE unified Send button ---
if st.button("Send", key="robix_send"):
    if not question:
        st.warning("Please type a question first!")
    elif not uploaded_files:
        st.warning("Please upload at least one file!")
    else:
        # Initialize response variable to be available outside try/except
        response = None 
        
        with st.spinner("RobixGPT is cooking... 🧠"):
            all_text = ""
            image_files = []

            # --- Extract text and detect images ---
            for file in uploaded_files:
                filename = file.name.lower()

                if filename.endswith((".txt", ".csv")):
                    content = file.read().decode("utf-8", errors="ignore")
                    all_text += f"\n\n--- File: {file.name} ---\n{content}"

                elif filename.endswith(".pdf"):
                    reader = PyPDF2.PdfReader(file)
                    pdf_text = ""
                    for page in reader.pages:
                        pdf_text += page.extract_text() or ""
                    all_text += f"\n\n--- File: {file.name} ---\n{pdf_text}"

                elif filename.endswith((".jpg", ".jpeg", ".png")):
                    image = Image.open(file)
                    image_files.append(image)
                    st.image(image, caption=f"🖼️ {file.name}", use_column_width=True)

            # --- Build the prompt ---
            prompt = f"""
            You are RobixGPT, an intelligent multimodal assistant.
            The user uploaded the following content and asked a question.

            Text contents:
            {all_text}

            Question: {question}
            Please give a clear, helpful, and insightful answer.
            """

            # --- Send both text + images to Gemini ---
            try:
                # Correct structure for contents: list of parts (prompt string + image objects)
                contents_parts = [prompt] + image_files 
    
                response = robix.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents_parts
                )
            except Exception as e:
                st.error(f"Error: {e}")
                # Note: The code will stop here if an error occurs

        # Display output only if a response was successfully generated
        if response is not None:
            st.success("✅ Response generated successfully cooked!")
            st.write(response.text)
