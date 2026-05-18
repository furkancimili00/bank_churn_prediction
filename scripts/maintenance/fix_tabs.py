import sys

content = open("ui/tabs/tab_single_analysis.py", "r", encoding="utf-8").read()

content = content.replace('st.radio("Kredi Kartı Var mı?", ["Evet", "Hayır"]) == "Evet"', 'st.radio(t("single_credit_card"), [t("single_yes"), t("single_no")]) == t("single_yes")')
content = content.replace('st.radio("Aktif Müşteri mi?", ["Evet", "Hayır"]) == "Evet"', 'st.radio(t("single_active"), [t("single_yes"), t("single_no")]) == t("single_yes")')
content = content.replace('st.radio(t("single_credit_card"), ["Evet", "Hayır"]) == "Evet"', 'st.radio(t("single_credit_card"), [t("single_yes"), t("single_no")]) == t("single_yes")')
content = content.replace('st.radio(t("single_active"), ["Evet", "Hayır"]) == "Evet"', 'st.radio(t("single_active"), [t("single_yes"), t("single_no")]) == t("single_yes")')

open("ui/tabs/tab_single_analysis.py", "w", encoding="utf-8").write(content)
print("Radio buttons fixed")
