# -*- coding: utf-8 -*-
import re, codecs

with codecs.open('ui/tabs/tab_single_analysis.py', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = re.compile(r'    st\.markdown\(\s*f"> \*\*Kural Tabanli Kampanya Mesaji:\*\* "\s*f"\{agent_result\.get\(\'campaign_message\', \'\'\)\}"\s*\)', re.DOTALL)

new_block = '''    with st.container(border=True):
        st.markdown("#### Sistem (Kural Tabanli) Kampanya Onerisi")
        campaign_msg = agent_result.get('campaign_message', '')
        st.warning(f"**Mesaj:** {campaign_msg}")
        
        if campaign_msg:
            import urllib.parse
            encoded = urllib.parse.quote(campaign_msg)
            st.link_button("E-Posta Sablonuna Aktar", f"mailto:?subject=Size%20Ozel%20Kampanya%20Firsati&body={encoded}")'''

text, count = pattern.subn(new_block, text)

with codecs.open('ui/tabs/tab_single_analysis.py', 'w', encoding='utf-8') as f:
    f.write(text)

print(f"Replaced {count} instances.")
