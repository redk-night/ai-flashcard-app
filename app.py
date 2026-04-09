import streamlit as st
from groq import Groq
import json

# --- 1. CONFIGURATION (Using Streamlit Secrets) ---
# Ab ye line aapke Streamlit Cloud ke Secrets se key uthayegi
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("API Key nahi mili! Streamlit Settings > Secrets mein 'GROQ_API_KEY' set karein.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# --- 2. WEB INTERFACE ---
st.set_page_config(page_title="AI Flashcard Maker", page_icon="🦙")
st.title("🦙 Llama 3.3 Flashcard Generator")
st.markdown("---")

# User Input
user_notes = st.text_area("Apne Study Notes yahan paste karein:", height=200, placeholder="Example: Photosynthesis is the process by which plants make food...")
card_count = st.slider("Kitne flashcards chahiye?", 2, 10, 5)

# --- 3. THE MAGIC LOGIC ---
if st.button("🚀 Generate Flashcards", type="primary"):
    if not user_notes:
        st.warning("Pehle kuch text toh likhiye!")
    else:
        with st.spinner("Llama 3.3 is thinking..."):
            try:
                # API Call to Llama 3.3
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a professional teacher. Create flashcards in JSON format only. Return a JSON array where each object has 'front' and 'back' keys."
                        },
                        {
                            "role": "user", 
                            "content": f"Generate {card_count} flashcards from this text: {user_notes}"
                        }
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.5,
                    response_format={"type": "json_object"}
                )

                # Response parsing
                raw_response = chat_completion.choices[0].message.content
                data = json.loads(raw_response)

                # Logic to handle different JSON structures
                if isinstance(data, dict):
                    # Check if list is inside a key
                    for key in data:
                        if isinstance(data[key], list):
                            st.session_state.deck = data[key]
                            break
                    else:
                        st.session_state.deck = [data]
                else:
                    st.session_state.deck = data

                st.success(f"Success! {len(st.session_state.deck)} Cards Generated.")

            except Exception as e:
                st.error(f"Error: {e}")

# --- 4. DISPLAYING THE CARDS ---
if 'deck' in st.session_state:
    st.write("### Your Flashcards:")
    for i, card in enumerate(st.session_state.deck):
        with st.container(border=True):
            st.write(f"**Question {i+1}**")
            # Using .get() to prevent errors if keys are missing
            st.markdown(f"#### {card.get('front', card.get('question', 'No Question'))}")
            
            with st.expander("🔍 Click to reveal Answer"):
                st.success(f"**Answer:** {card.get('back', card.get('answer', 'No Answer'))}")