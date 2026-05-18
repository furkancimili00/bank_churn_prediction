import codecs
import re

with codecs.open('ui/tabs/tab_single_analysis.py', 'r', encoding='utf-8') as f:
    text = f.read()

def replacer(match):
    return '''def _render_ai_campaign_messages(agent_result: dict[str, Any]) -> None:
    \"\"\"LLM kampanya mesajlarini veya kural tabanli mesaji gösterir.\"\"\"
    import urllib.parse
    gemini_msg = agent_result.get("gemini_campaign")
    groq_msg = agent_result.get("groq_campaign")
    openai_msg = agent_result.get("openai_campaign")

    def create_mailto_url(body_text):
        if not body_text:
            return ""
        safe_body = urllib.parse.quote(body_text)
        return f"mailto:?subject=Size%20Ozel%20Kampanya%20Firsati&body={safe_body}"

    if gemini_msg or groq_msg or openai_msg:
        st.markdown("### ?? Otonom Ajan Kampanya Üretimleri", help="Yapay zeka modellerinin ürettigi kampanya senaryolari")

        if gemini_msg:
            with st.container(border=True):
                st.markdown("#### ?? Google Gemini Senaryosu")
                st.success(gemini_msg)
                st.link_button("?? E-Posta Sablonunu Aç (Gemini)", create_mailto_url(gemini_msg))

        if groq_msg:
            with st.container(border=True):
                st.markdown("#### ?? Groq Llama3 Senaryosu")
                st.info(groq_msg)
                st.link_button("?? E-Posta Sablonunu Aç (Groq)", create_mailto_url(groq_msg))

        if openai_msg:
            with st.container(border=True):
                st.markdown("#### ?? OpenAI GPT Senaryosu")
                st.error(openai_msg)
                st.link_button("?? E-Posta Sablonunu Aç (OpenAI)", create_mailto_url(openai_msg))
        return

    # Fallback / Kural tabanli
    with st.container(border=True):
        st.markdown("#### ?? Sistem (Kural Tabanli) Kampanya Önerisi")
        campaign_msg = agent_result.get('campaign_message', '')
        if campaign_msg:
            st.warning(f"**Mesaj:** {campaign_msg}")
            st.link_button("?? E-Posta Sablonunu Aç", create_mailto_url(campaign_msg))
        else:
            st.warning("Henüz mesaj olusturulmadi.")


def _render_campaign_details'''

pattern = re.compile(r'def _render_ai_campaign_messages\(.*?(?=def _render_campaign_details)', re.DOTALL)
text, count = pattern.subn(replacer, text)

with codecs.open('ui/tabs/tab_single_analysis.py', 'w', encoding='utf-8') as f:
    f.write(text)

print(f"Replaced {count} blocks")
