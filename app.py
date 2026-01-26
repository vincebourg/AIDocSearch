import streamlit as st
import requests
from datetime import datetime

st.title("Assistant Droit des affaires.")

# Initialize session state for message history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize error details storage
if "error_details" not in st.session_state:
    st.session_state.error_details = None


def display_error_in_console(error_message, user_message, error_type):
    print("=" * 60)
    print(f"Type d'erreur: {error_type}")
    print(f"Message utilisateur: {user_message}")
    print(f"Détails de l'erreur: {error_message}")
    print("=" * 60)


def send_error_notification(error_details):
    """Notification suite au clic utilisateur sur le bouton."""
    print("=" * 60)
    print("🔔 CONTACT ADMINISTRATEUR - ACTION UTILISATEUR")
    print("=" * 60)
    print(f"À: administrateur@example.com")
    print(f"Sujet: Demande d'Assistance - Assistant Droit des Affaires")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    print(f"Type d'erreur: {error_details['type']}")
    print(f"Message utilisateur: {error_details['user_message']}")
    print(f"Détails de l'erreur: {error_details['error']}")
    print(f"Horodatage erreur: {error_details['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL Backend: http://localhost:5000/chat")
    print("⚠️ L'UTILISATEUR A DEMANDÉ DE L'AIDE VIA LE BOUTON")
    print("=" * 60)


def handle_backend_error(user_message, error_details, error_type):
    """Gère les erreurs backend avec un message convivial."""
    # Message convivial pour l'utilisateur
    error_msg = (
        "Je suis désolé, mais le service est actuellement indisponible. "
        "Veuillez réessayer dans quelques instants. Si le problème persiste, "
        "vous pouvez contacter l'administrateur."
    )

    # Ajouter à l'historique
    st.session_state.messages.append({"role": "assistant", "content": error_msg})

    # Afficher dans l'interface
    with st.chat_message("assistant"):
        st.markdown(error_msg)

    # Stocker les détails pour le bouton de contact
    st.session_state.error_details = {
        "user_message": user_message,
        "error": error_details,
        "type": error_type,
        "timestamp": datetime.now()
    }

    # Log automatiquement dans la console
    send_error_notification(error_details, user_message, error_type)


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
        response = requests.post("http://localhost:5000/chat", json={"message": prompt}, timeout=10)
        if response.status_code == 200:
            bot_response = response.json().get("response", "No response")

            # Add bot response to history
            st.session_state.messages.append({"role": "assistant", "content": bot_response})

            # Display bot response
            with st.chat_message("assistant"):
                st.markdown(bot_response)

            # Clear error state on success
            st.session_state.error_details = None
        else:
            # Backend responded but with error
            error_msg = f"HTTP {response.status_code}"
            handle_backend_error(prompt, error_msg, "HTTP Error")

    except requests.exceptions.ConnectionError as e:
        # Backend unreachable
        handle_backend_error(prompt, str(e), "Connection Error")

    except requests.exceptions.Timeout as e:
        # Timeout
        handle_backend_error(prompt, str(e), "Timeout Error")

    except Exception as e:
        # Other errors
        handle_backend_error(prompt, str(e), "Unknown Error")

# Display contact button if error exists
if st.session_state.error_details:
    if st.button("📧 Contacter l'administrateur"):
        send_error_notification_with_user_action(st.session_state.error_details)
        st.success("✅ Notification envoyée à l'administrateur")
