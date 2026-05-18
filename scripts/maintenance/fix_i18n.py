import codecs
import ast

with open('ui/i18n.py', 'rb') as f:
    raw = f.read()

if raw.startswith(codecs.BOM_UTF8):
    raw = raw[len(codecs.BOM_UTF8):]

text = raw.decode('utf-8')

# Search for the injected garbage and remove it. The garbage might have "\n" or "\\n" depending on what happened.
idx1 = text.find(',\\n        "audit_no_logs":')
idx2 = text.find(',\n        "audit_no_logs":')

if idx1 != -1:
    text = text[:idx1]
elif idx2 != -1:
    text = text[:idx2]

# Let's also verify that we aren't truncating the file incorrectly.
# The garbage was injected at `st.markdown(css, unsafe_allow_html=True)`
# It should end gracefully with that line and a newline.

with open('ui/i18n.py', 'w', encoding='utf-8') as f:
    f.write(text)

try:
    ast.parse(text)
    print("Cleaned up garbage from ui/i18n.py and Syntax OK!")
except Exception as e:
    print("Syntax Error:", e)
    
