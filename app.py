# Contenedor del chat - SIN el div que causaba el cuadrado blanco
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
        
        # Botón de descarga para respuestas del asistente (excepto el mensaje de bienvenida)
        if i > 0 and len(message["content"]) > 100:
            recipe_name = f"Receta_IA_{i}"
            recipe_content = create_recipe_download(message["content"], recipe_name)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button(
                    label="📥 Descargar Receta",
                    data=recipe_content,
                    file_name=f"{recipe_name}.txt",
                    mime="text/plain",
                    key=f"download_{i}",
                    use_container_width=True
                )import streamlit as st
import requests
import json
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv
import base64
from io import BytesIO

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="CucinaIA - Tu Chef Personal",
    page_icon="🍝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para diseño móvil
st.markdown("""
<style>
    /* Importar fuentes modernas */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    /* Variables de colores bandera italiana */
    :root {
        --verde: #009246;
        --blanco: #FFFFFF;
        --rojo: #CE2B37;
        --verde-claro: #4CAF50;
        --gris-claro: #f8f9fa;
        --sombra: rgba(0, 0, 0, 0.1);
    }
    
    /* Reset y base */
    .stApp {
        background: linear-gradient(135deg, var(--verde) 0%, var(--verde-claro) 100%);
        font-family: 'Inter', sans-serif;
        min-height: 100vh;
    }
    
    /* Ocultar elementos innecesarios */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    .stSidebar {display: none;}
    
    /* Contenedor principal */
    .main .block-container {
        padding: 0.5rem;
        max-width: 100%;
        margin: 0;
        background: transparent;
    }
    
    /* Eliminar padding extra de streamlit */
    .element-container {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Header de la app */
    .header-container {
        background: var(--blanco);
        border-radius: 15px;
        padding: 1.5rem 1rem;
        text-align: center;
        box-shadow: 0 4px 20px var(--sombra);
        margin-bottom: 1rem;
        border-bottom: 3px solid var(--rojo);
    }
    
    .app-title {
        font-family: 'Poppins', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(45deg, var(--verde), var(--rojo));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .app-subtitle {
        color: #666;
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Chat container - SIN fondo blanco que causa el cuadrado */
    .chat-container {
        padding: 0;
        min-height: 60vh;
        margin-bottom: 1rem;
    }
    
    /* Mensajes del chat */
    .user-message {
        background: linear-gradient(135deg, var(--verde), var(--verde-claro));
        color: white;
        padding: 1rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.8rem 0 0.8rem 1rem;
        font-weight: 500;
        box-shadow: 0 2px 10px rgba(0, 146, 70, 0.3);
        max-width: 85%;
        margin-left: auto;
        margin-right: 0;
    }
    
    .assistant-message {
        background: var(--blanco);
        color: #333;
        padding: 1rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.8rem 1rem 0.8rem 0;
        border-left: 4px solid var(--rojo);
        box-shadow: 0 2px 10px var(--sombra);
        max-width: 85%;
    }
    
    /* Input del chat */
    .stTextInput > div > div > input {
        border-radius: 25px !important;
        border: 2px solid var(--verde) !important;
        padding: 1rem !important;
        font-size: 1.1rem !important;
        background: var(--blanco) !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--rojo) !important;
        box-shadow: 0 0 0 2px rgba(206, 43, 55, 0.2) !important;
    }
    
    /* Botones */
    .stButton > button {
        background: linear-gradient(135deg, var(--rojo), #ff4757) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(206, 43, 55, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(206, 43, 55, 0.4) !important;
    }
    
    /* Botón de descarga especial */
    .download-btn {
        background: linear-gradient(135deg, var(--verde), var(--verde-claro)) !important;
        margin-top: 1rem !important;
    }
    
    /* Cards de recetas */
    .recipe-card {
        background: var(--blanco);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px var(--sombra);
        border-left: 5px solid var(--verde);
    }
    
    .recipe-title {
        font-family: 'Poppins', sans-serif;
        font-size: 1.4rem;
        color: var(--verde);
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    /* Info bubble */
    .info-bubble {
        background: var(--blanco);
        border: 2px solid var(--verde);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 2px 10px var(--sombra);
    }
    
    /* Ocultar sidebar completamente */
    .css-1d391kg {display: none;}
    section[data-testid="stSidebar"] {display: none !important;}
    
    /* Responsive design */
    @media (max-width: 768px) {
        .app-title {
            font-size: 1.8rem;
        }
        
        .main .block-container {
            padding: 0.3rem;
        }
        
        .header-container {
            padding: 1rem 0.5rem;
        }
        
        .user-message, .assistant-message {
            margin-left: 0.5rem;
            margin-right: 0.5rem;
            max-width: 90%;
        }
    }
    
    /* Animaciones suaves */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stMarkdown {
        animation: fadeIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

def query_groq_api(messages, api_key):
    """Llama a la API de Groq con prompt especializado en cocina italiana"""
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Prompt especializado en cocina
        system_prompt = """Eres RecetasIA, un asistente especializado únicamente en recetas y cocina. 

REGLAS ESTRICTAS:
- SOLO responde sobre recetas, ingredientes, técnicas de cocina, platos de cualquier país
- NO respondas preguntas sobre otros temas (política, deportes, tecnología, etc.)
- Si preguntan algo no relacionado con cocina, responde: "¡Hola! Solo soy experto en recetas y cocina 🍳 ¿Qué receta te gustaría aprender hoy?"
- Siempre incluye emojis de comida 🍳🥘🍽️
- Incluye siempre ingredientes, tiempo de preparación y pasos claros
- Sugiere maridajes cuando sea apropiado

Ejemplo de respuesta perfecta:
"¡Excelente elección! 🍳 Te enseño mi receta de Paella Valenciana:

**Ingredientes (4 personas):**
- 400g arroz bomba
- 1 pollo troceado
- 200g judías verdes
- 100g garrofón

**Preparación (45 min):**
1. Sofríe el pollo en aceite de oliva
2. Añade las verduras...
3. Incorpora el arroz...

¡Buen provecho! 🥘"
"""
        
        # Insertar el prompt del sistema al inicio
        cooking_messages = [{"role": "system", "content": system_prompt}] + messages
        
        data = {
            "model": "llama3-8b-8192",
            "messages": cooking_messages,
            "temperature": 0.7,
            "max_tokens": 1000,
            "stream": False
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return "¡Hay un problema con la conexión! ¿Puedes intentarlo de nuevo? 🍳"
            
    except Exception as e:
        return "¡Ups! Hay un pequeño problema técnico. ¿Intentamos otra vez? 👨‍🍳"

def is_cooking_related(message):
    """Verifica si la pregunta está relacionada con cocina"""
    cooking_keywords = [
        'receta', 'cocinar', 'comida', 'pasta', 'pizza', 'ingrediente', 
        'plato', 'salsa', 'hornear', 'freír', 'hervir', 'sartén',
        'horno', 'ajo', 'tomate', 'queso', 'aceite', 'sal', 'pimienta',
        'risotto', 'gnocchi', 'carbonara', 'lasaña', 'tiramisu',
        'cómo hacer', 'preparar', 'cocción', 'paella', 'tortilla',
        'arroz', 'pollo', 'pescado', 'carne', 'verdura', 'postre'
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in cooking_keywords)

def create_recipe_download(recipe_text, recipe_name):
    """Crea un archivo descargable con la receta"""
    # Formatear la receta para descarga
    formatted_recipe = f"""
🍳 RECETAS IA - TU ASISTENTE CULINARIO 🍳
================================================

RECETA: {recipe_name}
Generada el: {datetime.now().strftime('%d/%m/%Y %H:%M')}

{recipe_text}

================================================
¡Buen Provecho! 🍽️
RecetasIA - Tu asistente de cocina personal
    """
    
    return formatted_recipe

# Header de la aplicación
st.markdown("""
<div class="header-container">
    <h1 class="app-title">🍳 RecetasIA</h1>
    <p class="app-subtitle">Tu Asistente Personal de Cocina • ¡Descubre recetas deliciosas! 🍽️</p>
</div>
""", unsafe_allow_html=True)

# Configuración de API en sidebar oculto
with st.sidebar:
    st.markdown("### 🔑 Configuración")
    groq_api_key = st.text_input(
        "Groq API Key", 
        value=os.getenv("GROQ_API_KEY", ""),
        type="password",
        help="Tu clave API de Groq para la IA"
    )

# Info bubble
st.markdown("""
<div class="info-bubble">
    <strong>🍳 ¡Bienvenido a RecetasIA!</strong><br>
    Pregúntame sobre cualquier receta del mundo: paella, sushi, tacos, pasta... 
    ¡Toda la cocina internacional a tu alcance! 👨‍🍳
</div>
""", unsafe_allow_html=True)

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome_msg = """¡Hola! Soy RecetasIA, tu asistente personal de cocina 🍳

¿Qué deliciosa receta te gustaría aprender hoy? 
Puedo enseñarte desde una paella española hasta sushi japonés, tacos mexicanos o cualquier plato que se te ocurra.

¡Pregúntame lo que quieras! 👨‍🍳🍽️"""
    
    st.session_state.messages.append({
        "role": "assistant", 
        "content": welcome_msg
    })

# Contenedor del chat
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Mostrar historial del chat
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
        
        # Botón de descarga para respuestas del asistente (excepto el mensaje de bienvenida)
        if i > 0 and len(message["content"]) > 100:
            recipe_name = f"Receta_CucinaIA_{i}"
            recipe_content = create_recipe_download(message["content"], recipe_name)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button(
                    label="📥 Descargar Receta",
                    data=recipe_content,
                    file_name=f"{recipe_name}.txt",
                    mime="text/plain",
                    key=f"download_{i}",
                    use_container_width=True
                )

st.markdown('</div>', unsafe_allow_html=True)

# Input del usuario
user_input = st.text_input(
    "",
    placeholder="¿Qué receta quieres aprender? Ej: 'Cómo hacer paella valenciana' 🍳",
    key="user_input"
)

# Botón de envío
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    send_button = st.button("🍳 ¡Cocinar!", use_container_width=True)

# Procesar input del usuario
if send_button and user_input:
    # Verificar si la pregunta es sobre cocina
    if not is_cooking_related(user_input):
        # Respuesta para temas no relacionados con cocina
        non_cooking_response = "¡Hola! 🍳 Solo soy experto en recetas y cocina de todo el mundo. ¿Qué receta te gustaría aprender hoy? ¡Puedo enseñarte paella, sushi, tacos, pasta y mucho más! 👨‍🍳🍽️"
        
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": non_cooking_response})
        st.rerun()
    else:
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Generar respuesta de IA
        with st.spinner("🍳 Preparando tu receta..."):
            if groq_api_key:
                # Usar solo los últimos 6 mensajes para mantener contexto
                recent_messages = st.session_state.messages[-6:]
                response = query_groq_api(recent_messages, groq_api_key)
            else:
                response = """¡Necesito que configures tu API key de Groq para poder darte recetas auténticas! 🍳

Mientras tanto, ¿te gustaría que te recomiende algunos platos populares? 
- Paella Valenciana 🥘
- Sushi Japonés 🍣  
- Tacos Mexicanos 🌮
- Pasta Italiana 🍝

¡Configura tu API y te enseño paso a paso! 👨‍🍳"""

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# Botones de control en la parte inferior
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("🗑️ Nueva Conversación", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

with col2:
    if st.button("📱 Compartir App", use_container_width=True):
        st.balloons()
        st.success("¡Gracias por usar RecetasIA! 🍳")

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem; color: white; font-size: 0.9rem;">
    🍳 <strong>RecetasIA</strong> - La cocina mundial al alcance de tus manos<br>
    <em>¡Buen provecho y hasta la próxima!</em> 🍽️
</div>
""", unsafe_allow_html=True)