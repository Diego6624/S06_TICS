import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Chatbot Gastronomía Peruana", page_icon="🍲")
st.title("🍲 Chatbot Experto en Comida Peruana")

# 1. Configurar tu API Key de Gemini
API_KEY = "AIzaSyDti0yNNLCVdg0NR0iN5w7eSNSBLfyAeDs"  # Pega tu clave aquí
genai.configure(api_key=API_KEY)

# 2. Configurar el modelo Gemini 3.6 Flash con System Prompt
model = genai.GenerativeModel(
    model_name="gemini-3.6-flash",
    system_instruction="Eres un experto culinario especializado única y exclusivamente en comida peruana. Responde de forma amable y concisa a cualquier pregunta sobre ingredientes, recetas o historia de la gastronomía del Perú."
)

# Inicializar sesión de chat para mantener el contexto
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Mostrar el historial de mensajes
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# --- PARTE MULTIMODAL: Procesamiento de Audio ---
st.sidebar.header("🎤 Consultas por Audio")

# Opción 1: Subir archivo
audio_file = st.sidebar.file_uploader("Sube tu nota de voz", type=['mp3', 'wav', 'm4a', 'mpeg', 'mpga', 'ogg', 'webm'])

# Opción 2: Grabar audio directamente desde el micrófono
audio_recorded = st.sidebar.audio_input("O graba tu mensaje de voz aquí")

# Determinar qué audio usar (si graba uno nuevo, se prioriza)
audio_to_process = audio_recorded if audio_recorded else audio_file

if audio_to_process is not None:
    if st.sidebar.button("Procesar Audio"):
        with st.spinner("Procesando y escuchando el audio con Gemini..."):
            # Obtener el nombre del archivo (st.audio_input usa "audio.wav" por defecto)
            file_name = getattr(audio_to_process, "name", "temp_recording.wav")
            temp_filename = f"temp_{file_name}"
            
            # Guardar el archivo localmente para enviarlo a Gemini
            with open(temp_filename, "wb") as f:
                f.write(audio_to_process.getbuffer())
            
            # Subir el audio a los servidores de Gemini
            uploaded_file = genai.upload_file(temp_filename)
            
            # Pedir a Gemini que entienda y responda al audio
            response = model.generate_content([
                uploaded_file, 
                "Escucha este audio y responde a la pregunta sobre comida peruana que realiza el usuario."
            ])
            
            # Eliminar archivo temporal local
            os.remove(temp_filename)
            
            # Mostrar resultado en el chat
            with st.chat_message("user"):
                st.audio(audio_to_process)
            with st.chat_message("assistant"):
                st.markdown(response.text)

# --- PARTE CHATBOT: Texto ---
if prompt := st.chat_input("Escribe tu pregunta sobre comida peruana..."):
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Enviar a Gemini manteniendo la conversación previa
    response = st.session_state.chat_session.send_message(prompt)
    
    # Mostrar respuesta
    with st.chat_message("assistant"):
        st.markdown(response.text)