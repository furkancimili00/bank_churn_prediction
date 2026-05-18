import os
import streamlit as st
from typing import List, Dict

def get_project_context() -> str:
    """Proje dokümanlarını okuyarak bağlam (context) string'i oluşturur."""
    context = ""
    docs_to_read = ["README.md", "QA_REPORT.md"]
    
    for doc in docs_to_read:
        try:
            # Proje kök dizinini bul
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, doc)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    context += f"\n--- {doc} ---\n{content}\n"
        except Exception as e:
            pass
            
    if not context:
        context = "Banka Churn Tahmin (Müşteri Kayıp Analizi) Projesi."
        
    return context

def init_chat_history() -> None:
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Merhaba! Ben bu projenin gömülü yapay zeka asistanıyım. Algoritmalar, mimari veya müşteri verileri hakkında bana soru sorabilirsiniz."}
        ]

def get_llm_response(messages: List[Dict[str, str]]) -> str:
    groq_key = st.secrets.get("llm", {}).get("groq_api_key", "")
    if not groq_key:
        return "⚠️ Hata: Groq API anahtarı bulunamadı."
        
    try:
        from openai import OpenAI
        client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
        
        system_prompt = f"""Sen bu banka churn tahmin (müşteri kayıp analizi) projesinin içine gömülü (embedded) uzman yapay zeka asistanısın.
Kullanıcıya (veri bilimci, analist veya şube müdürü olabilir) proje ile ilgili sorularında yardımcı olacaksın.
Aşağıda projenin dökümantasyon dosyalarından çekilmiş bilgiler yer almaktadır. Yanıtlarını bu bilgilere dayandır.
Eğer cevabı dökümantasyonda bulamazsan, genel veri bilimi ve XGBoost/Streamlit uzmanlığına dayanarak profesyonelce cevap ver.
Cevapların Markdown formatında, şık ve anlaşılır olsun. Emojiler kullanabilirsin.

PROJE BAĞLAMI:
{get_project_context()}
"""
        
        api_messages = [{"role": "system", "content": system_prompt}]
        # Sadece son 5 mesajı gönder (token tasarrufu)
        api_messages.extend(messages[-5:])
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=api_messages,
            max_tokens=800,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Groq API Hatası: {str(e)}"

def render_floating_assistant() -> None:
    """Ekranın sağ altına sabitlenmiş yüzen (floating) chat arayüzünü çizer."""
    import streamlit.components.v1 as components
    
    init_chat_history()
    
    # "Chat Asistanı" görünümünü simüle eden Expander
    with st.expander("💬 AI Asistan", expanded=False):
        
        chat_container = st.container(height=350)
        
        with chat_container:
            for msg in st.session_state.chat_messages:
                if msg["role"] == "user":
                    st.markdown(f"👤 **Siz:** {msg['content']}")
                else:
                    st.markdown(f"🤖 **AI:** {msg['content']}")
                    
        def submit_chat():
            prompt = st.session_state.get("ai_chat_prompt", "").strip()
            if prompt:
                st.session_state.chat_messages.append({"role": "user", "content": prompt})
                with st.spinner("AI Yanıtlıyor..."):
                    response = get_llm_response(st.session_state.chat_messages)
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                st.session_state.ai_chat_prompt = "" # Input kutusunu temizle
                
        st.text_input("Bana bir şey sorun...", key="ai_chat_prompt", on_change=submit_chat, placeholder="Örn: Uygulamanın amacı nedir?")

    # JavaScript ile bu expander'ı ekranın sağ altına sabitle (Floating Widget Hack)
    components.html(
        """
        <script>
        // Streamlit yüklendiğinde çalışması için küçük bir gecikme
        setTimeout(function() {
            const expanders = window.parent.document.querySelectorAll('[data-testid="stExpander"]');
            expanders.forEach(exp => {
                const summaryText = exp.querySelector('summary').innerText;
                if(summaryText.includes("AI Asistan")) {
                    exp.style.position = 'fixed';
                    exp.style.bottom = '20px';
                    exp.style.right = '20px';
                    exp.style.width = '350px';
                    exp.style.zIndex = '9999';
                    exp.style.backgroundColor = '#1e1e1e';
                    exp.style.borderRadius = '10px';
                    exp.style.boxShadow = '0px 8px 16px rgba(0,0,0,0.6)';
                    exp.style.border = '1px solid #e67e22';
                }
            });
        }, 500);
        </script>
        """,
        height=0, width=0
    )
