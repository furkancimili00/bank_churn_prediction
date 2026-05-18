import sys
content = open("dashboard.py", "r", encoding="utf-8").read()

content = content.replace("st.sidebar.info(f\"{t(\\\"welcome\\\")} **{t(\\\"manager\\\")}**\")", "st.sidebar.info(f'{t(\"welcome\")} **{t(\"manager\")}**')")

open("dashboard.py", "w", encoding="utf-8").write(content)
print("Fixed syntax error")
