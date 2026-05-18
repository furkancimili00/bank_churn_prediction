import codecs

with codecs.open('ui/tabs/tab_single_analysis.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('def _render_campaign_detailsdef _render_campaign_detailsdef _render_campaign_details', 'def _render_campaign_details')
text = text.replace('??', '??')
text = text.replace('Ãœ', 'Ü')
text = text.replace('Ã¼', 'ü')
text = text.replace('Ã§', 'ç')
text = text.replace('Ã–', 'Ö')
text = text.replace('Ä±', 'i')
text = text.replace('ÅŸ', 's')

with codecs.open('ui/tabs/tab_single_analysis.py', 'w', encoding='utf-8') as f:
    f.write(text)
