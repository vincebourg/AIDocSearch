import streamlit as st
import requests

st.title("Assistant Droit des affaires.")

# Initialize session state for message history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display all previous messages in chronological order (oldest first)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input at the bottom
if prompt := st.chat_input("Que puis-je pour vous ?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get bot response
    try:
        response = requests.post("http://localhost:5000/chat", json={"message": prompt})
        if response.status_code == 200:
            bot_response = response.json().get("response", "No response")

            # Add bot response to history
            st.session_state.messages.append({"role": "assistant", "content": bot_response})

            # Display bot response
            with st.chat_message("assistant"):
                st.markdown(bot_response)
        else:
            st.error("Error communicating with chatbot.")
    except Exception as e:
        st.error(f"Error: {str(e)}")
