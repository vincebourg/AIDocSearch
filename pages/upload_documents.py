import streamlit as st
import requests
import os

# Server URL configuration (defaults to localhost for local development)
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:5000")

st.title("📁 Import de Documents")

st.markdown("""
Importer des documents pour améliorer la base de connaissances.

**Types de fichiers supportés:**
- Fichiers texte (.txt)
- Fichiers HTML (.html)
- Fichiers CSV (.csv)
""")

# File uploader
uploaded_file = st.file_uploader(
    "Sélectionner un fichier à importer",
    type=["txt", "html", "csv"],
    help="Sélectionner un fichier texte, HTML ou CSV à ajouter à la base de connaissances"
)

# Upload button
if uploaded_file is not None:
    # Display file information
    st.info(f"**Fichier sélectionné:** {uploaded_file.name} ({uploaded_file.size} octets)")

    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button("🚀 Importer", type="primary"):
            with st.spinner("Importation du document..."):
                try:
                    # Prepare the file for upload
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

                    # Send to backend
                    response = requests.post(
                        f"{SERVER_URL}/upload",
                        files=files,
                        timeout=60
                    )

                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            st.success(f"✅ {result.get('message')}")
                            st.info(f"**Chunks indexed:** {result.get('chunks_indexed')}")
                            st.info(f"**Total documents in database:** {result.get('total_documents')}")
                        else:
                            st.error(f"❌ {result.get('message')}")
                    else:
                        error_data = response.json()
                        st.error(f"❌ Echec de l'import : {error_data.get('message', 'Unknown error')}")

                except requests.exceptions.ConnectionError:
                    st.error("❌ Impossible de se connecter. Veuillez vérifier l'état du serveur.")
                except requests.exceptions.Timeout:
                    st.error("❌ Le serveur n'a pas répondu dans le temps imparti.")
                except Exception as e:
                    st.error(f"❌ Erreur : {str(e)}")

    with col2:
        st.caption("Cliquer sur 'Importer' pour ajouter le document à la base de connaissances.")

# Backend status
st.divider()

st.subheader("Etat du serveur")

if st.button("Vérifier l'état du serveur"):
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            st.success("✅ Le server est opérationnel")
            st.json(health_data)
        else:
            st.error("❌ Le serveur a répondu avec une erreur")
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Impossible de se connecter au serveur {SERVER_URL}")
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
