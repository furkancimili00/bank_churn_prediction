import streamlit as st
import pandas as pd
from services.eda_service import (
    create_categorical_analysis,
    create_churn_boxplots,
    create_churn_rate_by_category,
    create_correlation_heatmap,
    create_distribution_histograms,
    get_summary_statistics,
    load_default_dataset,
)

def render_tab_eda(local_model=None, local_scaler=None, expected_features=None):
        st.subheader("📈 Keşifsel Veri Analizi (EDA)")
        st.write(
            "Veri setini interaktif grafiklerle keşfedin. Varsayılan olarak eğitim verisi kullanılır, "
            "veya kendi CSV dosyanızı yükleyebilirsiniz."
        )
    
        eda_source = st.radio(
            "Veri Kaynağı Seçin:",
            ["Varsayılan Veri Seti (Churn_Modelling.csv)", "Kendi CSV Dosyamı Yükle"],
            horizontal=True,
            key="eda_source",
        )
    
        eda_df = None
        if eda_source == "Varsayılan Veri Seti (Churn_Modelling.csv)":
            eda_df = load_default_dataset()
        else:
            eda_file = st.file_uploader("CSV Dosyası Yükle", type=["csv"], key="eda_upload")
            if eda_file is not None:
                eda_df = pd.read_csv(eda_file)
    
        if eda_df is not None:
            # Özet İstatistikler
            stats = get_summary_statistics(eda_df)
            st.markdown("### 📊 Genel Bakış")
            eda_m1, eda_m2, eda_m3, eda_m4 = st.columns(4)
            eda_m1.metric("Toplam Müşteri", f"{stats['toplam_musteri']:,}")
            eda_m2.metric("Ortalama Yaş", f"{stats['ortalama_yas']}" if stats['ortalama_yas'] else "—")
            eda_m3.metric("Ort. Bakiye (€)", f"€{stats['ortalama_bakiye']:,.0f}" if stats['ortalama_bakiye'] else "—")
            eda_m4.metric("Churn Oranı", f"%{stats['churn_orani']}" if stats['churn_orani'] is not None else "—")
    
            st.write("---")
    
            # Korelasyon Haritası
            st.markdown("### 🔗 Korelasyon Matrisi")
            fig_corr = create_correlation_heatmap(eda_df)
            st.plotly_chart(fig_corr, use_container_width=True)
    
            # Dağılım Histogramları
            st.markdown("### 📊 Özellik Dağılımları")
            fig_dist = create_distribution_histograms(eda_df)
            st.plotly_chart(fig_dist, use_container_width=True)
    
            # Box Plot'lar
            fig_box = create_churn_boxplots(eda_df)
            if fig_box is not None:
                st.markdown("### 📦 Churn Karşılaştırmalı Box Plot")
                st.plotly_chart(fig_box, use_container_width=True)
    
            # Kategorik Churn Oranları
            fig_cat_rate = create_churn_rate_by_category(eda_df)
            if fig_cat_rate is not None:
                st.markdown("### 📋 Kategorik Değişkenlere Göre Churn Oranı")
                st.plotly_chart(fig_cat_rate, use_container_width=True)
    
            # Çapraz Analiz (Sunburst)
            fig_sun = create_categorical_analysis(eda_df)
            if fig_sun is not None:
                st.markdown("### 🌐 Coğrafya → Cinsiyet → Churn (Sunburst)")
                st.plotly_chart(fig_sun, use_container_width=True)
        else:
            st.info("Lütfen bir veri kaynağı seçin veya CSV dosyası yükleyin.")
    
    # --- SEKME 6: MODEL PERFORMANSI ---
