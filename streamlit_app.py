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
st.markdown("### Haz preguntas sobre tus documentos financieros")

# Inputs del usuario
question = st.text_area("Escribe tu pregunta", placeholder="¿Cuánto IRPF me han retenido?", height=100)
uploaded_file = st.file_uploader("Sube tu nómina o archivo financiero", type=["pdf", "txt"])

if uploaded_file and question:
    try:
        if uploaded_file.name.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            file_contents = ""
            for page in pdf_reader.pages:
                file_contents += page.extract_text() + "\n"
        else:
            file_contents = uploaded_file.read().decode("utf-8")

        # Crear el prompt y llamar al modelo
        llm = init_chat_model(model=DEFAULT_CONFIG["model"])

        prompt_template = PromptTemplate(
            template="""You are an expert in economic and financial analysis.

{question}

You are given a file for extra information.

{file_contents}
""",
            input_variables=["question", "file_contents"]
        )

        prompt = prompt_template.format(question=question, file_contents=file_contents)

        with st.spinner("Procesando..."):
            answer = llm.invoke(prompt).content
            try:
                parsed_answer = answer.split("</think>")[1].strip()
            except IndexError:
                parsed_answer = answer

        st.subheader("Respuesta:")
        st.markdown(parsed_answer)

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
elif uploaded_file or question:
    st.info("Por favor, sube un archivo y escribe una pregunta para continuar.")
