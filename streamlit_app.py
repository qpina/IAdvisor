import streamlit as st
import PyPDF2
import io

from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate

# Configuración del modelo LLM
DEFAULT_CONFIG = {
    "model": "ollama:deepseek-r1:1.5b",
}

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

    # Llamar al modelo
    try:
        llm = init_chat_model(model=DEFAULT_CONFIG["model"])
        with st.spinner("Procesando..."):
            answer = llm.invoke(prompt_text).content
            try:
                parsed_answer = answer.split("</think>")[1].strip()
            except IndexError:
                parsed_answer = answer
        st.subheader("Respuesta:")
        st.markdown(parsed_answer)
    except Exception as e:
        st.error(f"Error al invocar el modelo de lenguaje: {e}")
else:
    st.info("Escribe una pregunta para comenzar.")
