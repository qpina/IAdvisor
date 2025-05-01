import streamlit as st
import PyPDF2
import io
import os
from dotenv import load_dotenv

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

# Cargar API key desde .env o secrets
load_dotenv()
together_api_key = os.getenv("TOGETHER_API_KEY")

if not together_api_key:
    st.error("No se encontró la API key de Together AI. Asegúrate de definir TOGETHER_API_KEY en un archivo .env o en los secretos de Streamlit.")
    st.stop()

# Título y logo
st.set_page_config(page_title="IAdvisor", layout="centered")
st.image("logo.png", width=100)
st.title("IAdvisor")
st.markdown("### Haz preguntas sobre tus documentos financieros o simplemente consulta tus dudas")

# Inputs del usuario
question = st.text_area("Escribe tu pregunta", placeholder="¿Cuánto IRPF me han retenido?", height=100)
uploaded_file = st.file_uploader("Sube tu nómina o archivo financiero (opcional)", type=["pdf", "txt"])

if question:
    file_contents = ""
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".pdf"):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                for page in pdf_reader.pages:
                    file_contents += page.extract_text() + "\n"
            else:
                file_contents = uploaded_file.read().decode("utf-8")
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            st.stop()

    # Crear el prompt dependiendo de si hay archivo o no
    if file_contents:
        prompt_text = f"""You are an expert in economic and financial analysis.

{question}

You are given a file for extra information.

{file_contents}
"""
    else:
        prompt_text = f"""You are an expert in economic and financial analysis.

{question}
"""

    # Llamar a Together.ai como si fuera OpenAI
    try:
        llm = ChatOpenAI(
            openai_api_key=together_api_key,
            base_url="https://api.together.xyz/v1",
            model="mistralai/Mistral-7B-Instruct-v0.2",
            temperature=0.4,
            max_tokens=1024
        )
        with st.spinner("Procesando..."):
            answer = llm.invoke(prompt_text).content
        st.subheader("Respuesta:")
        st.markdown(answer)
    except Exception as e:
        st.error(f"Error al invocar el modelo de Together AI: {e}")
else:
    st.info("Escribe una pregunta para comenzar.")
