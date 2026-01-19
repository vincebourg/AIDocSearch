import streamlit as st
import requests

st.title("Chatbot Interface")

message = st.text_input("Enter your message:")

if st.button("Send"):
    if message:
        try:
            response = requests.post("http://localhost:5000/chat", json={"message": message})
            if response.status_code == 200:
                bot_response = response.json().get("response", "No response")
                st.write(f"**Bot:** {bot_response}")
            else:
                st.error("Error communicating with chatbot.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a message.")