import sys

content = open("ui/tabs/tab_batch_analysis.py", "r", encoding="utf-8").read()

content = content.replace('st.error("â Toplu MÃ¼ÅŸteri Analizi ve Ã–nceliklendirme")', 'st.error(t("batch_file_limit"))')
# Also fix the main render logic
content = content.replace('def render_tab_batch_analysis(local_model: Any, local_scaler: Any, expected_features: list[str]) -> None:\n    """Toplu analiz sekmesini iÃ§erir."""\n    st.subheader("â Toplu MÃ¼ÅŸteri Analizi ve Ã–nceliklendirme")\n    st.write(\n        t("batch_desc")\n    )', 
                          'def render_tab_batch_analysis(local_model: Any, local_scaler: Any, expected_features: list[str]) -> None:\n    """Toplu analiz sekmesini iÃ§erir."""\n    st.subheader(t("batch_title"))\n    st.write(t("batch_desc"))')
# Fallback if that failed
content = content.replace('st.subheader("📂 Toplu Müşteri Analizi ve Önceliklendirme")', 'st.subheader(t("batch_title"))')
content = content.replace('st.error("Dosya boyutu çok büyük! Maksimum 5MB yüklenebilir.")', 'st.error(t("batch_file_limit"))')


open("ui/tabs/tab_batch_analysis.py", "w", encoding="utf-8").write(content)
print("Batch tab translations and headers injected")
