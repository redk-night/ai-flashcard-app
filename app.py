import streamlit as st
from groq import Groq
import json
import re

# --- 1. CONFIGURATION ---
GROQ_API_KEY = "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" 

client = Groq(api_key=GROQ_API_KEY)

# --- 2. WEB INTERFACE ---
st.set_page_config(page_title="Llama 3.3 Flashcard Maker", page_icon="🦙")
st.title("🦙 Llama 3.3 Flashcard Generator")
st.markdown("---")

user_notes = st.text_area("Apne Study Notes yahan paste karein:", height=200)
card_count = st.slider("Kitne flashcards chahiye?", 2, 10, 5)

# --- 3. THE MAGIC LOGIC ---
if st.button("🚀 Generate Flashcards", type="primary"):
    if not user_notes:
        st.warning("Pehle kuch text toh likhiye!")
    else:
        with st.spinner("Llama 3.3 is thinking..."):
            try:
                # Updated Model: llama-3.3-70b-versatile
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

                raw_response = chat_completion.choices[0].message.content
                data = json.loads(raw_response)

                # Logic to find the list in JSON
                if isinstance(data, dict):
                    if "flashcards" in data:
                        st.session_state.deck = data["flashcards"]
                    elif "cards" in data:
                        st.session_state.deck = data["cards"]
                    else:
                        for key in data:
                            if isinstance(data[key], list):
                                st.session_state.deck = data[key]
                                break
                else:
                    st.session_state.deck = data

                st.success("Done!")

            except Exception as e:
                st.error(f"Error: {e}")

# --- 4. DISPLAY ---
if 'deck' in st.session_state:
    st.write("### Your Flashcards:")
    for i, card in enumerate(st.session_state.deck):
        with st.container(border=True):
            st.write(f"**Question {i+1}**")
            st.markdown(f"#### {card.get('front', 'No Question')}")
            with st.expander("🔍 Click to reveal Answer"):
                st.success(f"**Answer:** {card.get('back', 'No Answer')}")