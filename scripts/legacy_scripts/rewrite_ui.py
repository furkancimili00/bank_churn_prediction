import re, codecs

with codecs.open('ui/tabs/tab_single_analysis.py', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = re.compile(r'def _render_ai_campaign_messages(.*?)def _render_retention_campaign', re.DOTALL)

new_block = '''def _render_ai_campaign_messages(agent_result: dict[str, Any]) -> None:
    \"\"\"LLM kampanya mesajlarini veya kural tabanli mesaji gösterir.

    Args:
        agent_result: Ajan akisindan dönen kampanya sonucu.
    \"\"\"
    import urllib.parse
    gemini_msg = agent_result.get("gemini_campaign")
    groq_msg = agent_result.get("groq_campaign")
    openai_msg = agent_result.get("openai_campaign")

    if gemini_msg or groq_msg or openai_msg:
        st.markdown("### ?? Otonom Ajan Kampanya Üretimleri", help="Farkli AI Ajanlarinin Senaryolari")

        if gemini_msg:
            with st.container(border=True):
                st.markdown("#### ?? Google Gemini Senaryosu")
                st.success(gemini_msg)
                encoded = urllib.parse.quote(gemini_msg)
                st.link_button("?? E-Posta Sablonuna Aktar", f"mailto:?subject=Size%20Ozel%20Kampanya%20Firsati&body={encoded}")

        if groq_msg:
            with st.container(border=True):
                st.markdown("#### ?? Groq Llama3 Senaryosu")
                st.info(groq_msg)
                encoded = urllib.parse.quote(groq_msg)
                st.link_button("?? E-Posta Sablonuna Aktar", f"mailto:?subject=Size%20Ozel%20Kampanya%20Firsati&body={encoded}")

        if openai_msg:
            with st.container(border=True):
                st.markdown("#### ?? OpenAI GPT Senaryosu")
                st.error(openai_msg)
                encoded = urllib.parse.quote(openai_msg)
                st.link_button("?? E-Posta Sablonuna Aktar", f"mailto:?subject=Size%20Ozel%20Kampanya%20Firsati&body={encoded}")
        return

    st.markdown(
        f"> ?? **Kural Tabanli Kampanya Mesaji:** "
        f"{agent_result.get('campaign_message', '')}"
    )


def _render_campaign_details(agent_result: dict[str, Any]) -> None:
    \"\"\"Ajan kampanya sonucunun detaylarini render eder.

    Args:
        agent_result: Ajan akisindan dönen kampanya sonucu.
    \"\"\"
    with st.expander("?? 360° AI Karar Mekanizmasi ve Aksiyon Özeti", expanded=True):
        ag_c1, ag_c2, ag_c3 = st.columns(3)
        contact_channel = agent_result.get("contact_channel", "—")
        contact_parts = contact_channel.split()

        ag_c1.metric("?? Hedef", agent_result.get("campaign_type", "—"))
        ag_c2.metric("?? Bütçe", f"€{agent_result.get('estimated_budget', 0):,.0f}")
        ag_c3.metric("?? Kanal", contact_parts[1] if len(contact_parts) > 1 else contact_channel)

        st.markdown("---")
        st.info(f"**?? Tavsiye Edilen Aksiyon:** {agent_result.get('recommended_action')}")
        st.caption(f"Aciliyet: {agent_result.get('urgency', '—').upper()}")

        st.markdown("---")
        _render_ai_campaign_messages(agent_result)


def _render_retention_campaign'''

text = pattern.sub(new_block, text)

with codecs.open('ui/tabs/tab_single_analysis.py', 'w', encoding='utf-8') as f:
    f.write(text)
