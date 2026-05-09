from typing import TypedDict, Optional

import pandas as pd
from langgraph.graph import StateGraph, END
from langchain_core.prompts import PromptTemplate
from core.logging_config import get_logger

logger = get_logger(__name__)


# Genişletilmiş durum tanımı (Multi-Step State)
class CustomerState(TypedDict):
    customer_id: Optional[str]
    churn_probability: float
    risk_level: str
    recommended_action: Optional[str]
    contact_channel: Optional[str]
    campaign_type: Optional[str]
    campaign_message: Optional[str]
    estimated_budget: Optional[float]
    urgency: Optional[str]


# ============================================
# ÇOK ADIMLI AJAN DÜĞÜMLERİ (Multi-Step Nodes)
# ============================================

def assess_risk(state: CustomerState) -> CustomerState:
    """
    Düğüm 1: Risk değerlendirmesi ve aciliyet seviyesi belirleme.

    Args:
        state (CustomerState): Müşteri durumu.

    Returns:
        CustomerState: Aciliyet ve risk seviyesi eklenmiş durum.
    """
    prob = state.get("churn_probability", 0.0)

    if prob >= 0.70:
        state["risk_level"] = "Çok Yüksek Riskli - Acil İletişime Geçilmeli"
        state["urgency"] = "acil"
    elif prob >= 0.40:
        state["risk_level"] = "Orta Riskli - Kampanya Önerilebilir"
        state["urgency"] = "normal"
    else:
        state["risk_level"] = "Düşük Riskli - Sadık Müşteri"
        state["urgency"] = "düşük"

    logger.info(f"Risk değerlendirmesi: {state['urgency']} (prob={prob:.2f})")
    return state


def select_channel(state: CustomerState) -> CustomerState:
    """
    Düğüm 2: Müşteriye ulaşım kanalını belirler (aciliyete göre).

    Args:
        state (CustomerState): Müşteri durumu.

    Returns:
        CustomerState: İletişim kanalı eklenmiş durum.
    """
    urgency = state.get("urgency", "düşük")

    channel_map = {
        "acil": "📞 Telefon + 📧 E-posta (Müşteri Temsilcisi Ataması)",
        "normal": "📧 E-posta + 📱 Uygulama Bildirimi",
        "düşük": "📱 Uygulama İçi Bildirim",
    }
    state["contact_channel"] = channel_map.get(urgency, "📱 Uygulama İçi Bildirim")
    logger.debug(f"İletişim kanalı seçildi: {state['contact_channel']}")
    return state


def generate_campaign(state: CustomerState) -> CustomerState:
    """
    Düğüm 3: Kişiselleştirilmiş kampanya türü ve mesajı üretir.

    Args:
        state (CustomerState): Müşteri durumu.

    Returns:
        CustomerState: Kampanya detayları eklenmiş durum.
    """
    urgency = state.get("urgency", "düşük")
    prob = state.get("churn_probability", 0.0)
    customer_id = state.get("customer_id", "Bilinmiyor")

    if urgency == "acil":
        state["campaign_type"] = "Acil Elde Tutma Paketi"
        state["recommended_action"] = "Acil İletişim & %20 İndirim + VIP Statüsü"
        state["campaign_message"] = (
            f"Sayın Müşterimiz (#{customer_id}), size özel %20 indirimli VIP paketimizi "
            f"sunmak istiyoruz. Ayrıca kişisel bankacılık danışmanınız atanmıştır."
        )
    elif urgency == "normal":
        state["campaign_type"] = "Sadakat Kampanyası"
        state["recommended_action"] = "Kredi Kartı Kampanyası + Bonus Puan"
        state["campaign_message"] = (
            f"Sayın Müşterimiz (#{customer_id}), yeni kredi kartı kampanyamızla "
            f"3 ay boyunca 2 kat bonus puan kazanabilirsiniz!"
        )
    else:
        state["campaign_type"] = "Rutin İletişim"
        state["recommended_action"] = "İşlem Yok (Sadık Müşteri)"
        state["campaign_message"] = (
            f"Sayın Müşterimiz (#{customer_id}), sadakatiniz için teşekkür ederiz. "
            f"Özel avantajlarınızı keşfetmek için uygulamamızı ziyaret edin."
        )

    logger.debug(f"Kampanya üretildi: {state['campaign_type']}")
    return state


def calculate_budget(state: CustomerState) -> CustomerState:
    """
    Düğüm 4: Kampanya bütçesini tahmin eder.

    Args:
        state (CustomerState): Müşteri durumu.

    Returns:
        CustomerState: Tahmini bütçe eklenmiş durum.
    """
    urgency = state.get("urgency", "düşük")

    budget_map = {
        "acil": 500.0,    # VIP paket + indirim maliyeti
        "normal": 150.0,  # Kampanya ve bonus maliyeti
        "düşük": 25.0,    # Bildirim maliyeti
    }
    state["estimated_budget"] = budget_map.get(urgency, 25.0)
    logger.debug(f"Bütçe hesaplandı: €{state['estimated_budget']}")
    return state


# Koşullu dallanma fonksiyonu
def route_by_urgency(state: CustomerState) -> str:
    """
    Aciliyete göre akışı dallandırır.
    Düşük riskli müşteriler için kampanya adımı atlanır.

    Args:
        state (CustomerState): Müşteri durumu.

    Returns:
        str: Sonraki düğüm adı.
    """
    if state.get("urgency") == "düşük":
        return "generate_campaign_node"
    return "select_channel_node"


# ============================================
# ÇOK ADIMLI AJAN AKIŞI (Multi-Step Graph)
# ============================================
workflow = StateGraph(CustomerState)

# Düğümleri ekleme
workflow.add_node("assess_risk_node", assess_risk)
workflow.add_node("select_channel_node", select_channel)
workflow.add_node("generate_campaign_node", generate_campaign)
workflow.add_node("calculate_budget_node", calculate_budget)

# Akış bağlantıları
workflow.set_entry_point("assess_risk_node")
workflow.add_conditional_edges(
    "assess_risk_node",
    route_by_urgency,
    {
        "select_channel_node": "select_channel_node",
        "generate_campaign_node": "generate_campaign_node",
    },
)
workflow.add_edge("select_channel_node", "generate_campaign_node")
workflow.add_edge("generate_campaign_node", "calculate_budget_node")
workflow.add_edge("calculate_budget_node", END)

# Çalıştırılabilir uygulamayı (Agent) derleme
agent_app = workflow.compile()


def run_agent(
    customer_id: str, churn_probability: float, risk_level: str
) -> CustomerState:
    """
    Çok adımlı ajan akışını başlatan ana fonksiyon.
    Akış: assess_risk → select_channel → generate_campaign → calculate_budget

    Args:
        customer_id (str): Müşteri kimlik numarası.
        churn_probability (float): Modelin hesapladığı churn olasılığı (0.0-1.0).
        risk_level (str): Risk seviyesi metni.

    Returns:
        CustomerState: Tüm adımların sonuçlarını içeren durum.
    """
    initial_state: CustomerState = {
        "customer_id": customer_id,
        "churn_probability": churn_probability,
        "risk_level": risk_level,
        "recommended_action": None,
        "contact_channel": None,
        "campaign_type": None,
        "campaign_message": None,
        "estimated_budget": None,
        "urgency": None,
    }

    result = agent_app.invoke(initial_state)
    logger.info(
        f"Ajan akışı tamamlandı: {result.get('campaign_type')} "
        f"(bütçe: €{result.get('estimated_budget', 0):.0f})"
    )
    return result



def _build_report_context(df_summary: pd.DataFrame) -> dict:
    """
    Rapor oluşturmak için veri özetini hazırlar.

    Args:
        df_summary (pd.DataFrame): Toplu analiz sonucu.

    Returns:
        dict: Rapor için gerekli istatistiksel bağlam.
    """
    total_customers = len(df_summary)
    high_risk_customers = len(df_summary[df_summary["Risk Seviyesi"] == "Yüksek"])
    medium_risk_customers = len(df_summary[df_summary["Risk Seviyesi"] == "Orta"])
    low_risk_customers = len(df_summary[df_summary["Risk Seviyesi"] == "Düşük"])
    total_expected_loss = df_summary["Beklenen Kayıp (€)"].sum()
    avg_risk = df_summary["Risk (%)"].mean() if "Risk (%)" in df_summary.columns else 0
    high_risk_percentage = (high_risk_customers / total_customers) * 100 if total_customers > 0 else 0

    # En yüksek riskli 5 müşteri
    top5 = df_summary.head(5)
    top5_text = ""
    for _, row in top5.iterrows():
        top5_text += f"  - Müşteri {row.get('Müşteri ID', '?')}: Risk %{row.get('Risk (%)', 0)}, Beklenen Kayıp €{row.get('Beklenen Kayıp (€)', 0):,.2f}\n"

    return {
        "total_customers": total_customers,
        "high_risk_customers": high_risk_customers,
        "medium_risk_customers": medium_risk_customers,
        "low_risk_customers": low_risk_customers,
        "total_expected_loss": total_expected_loss,
        "avg_risk": avg_risk,
        "high_risk_percentage": high_risk_percentage,
        "top5_text": top5_text,
    }


def _generate_llm_report(context: dict) -> str:
    """
    Gerçek bir LLM API'si (Gemini veya OpenAI) kullanarak yönetim raporu üretir.
    API anahtarı bulunamazsa veya hata oluşursa None döner.

    Args:
        context (dict): Rapor bağlam verileri.

    Returns:
        str veya None: LLM tarafından üretilen rapor metni.
    """
    try:
        import streamlit as st

        # Gemini API denemesi
        gemini_key = st.secrets.get("llm", {}).get("gemini_api_key", "")
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-2.0-flash")

                prompt = f"""Sen bir banka şube müdürüne rapor sunan kıdemli veri analistisin.
Aşağıdaki müşteri churn analiz verilerini kullanarak Türkçe, profesyonel bir yönetim özeti raporu yaz.

VERİLER:
- Toplam müşteri: {context['total_customers']}
- Yüksek riskli: {context['high_risk_customers']} (%{context['high_risk_percentage']:.1f})
- Orta riskli: {context['medium_risk_customers']}
- Düşük riskli: {context['low_risk_customers']}
- Toplam beklenen finansal kayıp: €{context['total_expected_loss']:,.2f}
- Ortalama risk skoru: %{context['avg_risk']:.1f}
- En riskli 5 müşteri:
{context['top5_text']}

RAPOR FORMATI:
1. Markdown formatında yaz
2. Başlıklar ve alt başlıklar kullan
3. Mevcut durum analizi, stratejik aksiyon planı ve önceliklendirme bölümleri olsun
4. Somut ve uygulanabilir öneriler ver
5. Emoji kullanarak görsel zenginlik kat"""

                response = model.generate_content(prompt)
                logger.info("LLM raporu başarıyla oluşturuldu (Gemini)")
                return response.text
            except Exception as e:
                logger.warning(f"Gemini API hatası, fallback'e geçiliyor: {e}")
                return None

        # OpenAI API denemesi
        openai_key = st.secrets.get("llm", {}).get("openai_api_key", "")
        if openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)

                prompt = f"""Sen bir banka şube müdürüne rapor sunan kıdemli veri analistisin.
Aşağıdaki müşteri churn analiz verilerini kullanarak Türkçe, profesyonel bir yönetim özeti raporu yaz.

VERİLER:
- Toplam müşteri: {context['total_customers']}
- Yüksek riskli: {context['high_risk_customers']} (%{context['high_risk_percentage']:.1f})
- Orta riskli: {context['medium_risk_customers']}
- Düşük riskli: {context['low_risk_customers']}
- Toplam beklenen finansal kayıp: €{context['total_expected_loss']:,.2f}
- Ortalama risk skoru: %{context['avg_risk']:.1f}

Markdown formatında, başlıklı, somut öneriler içeren bir rapor oluştur."""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1500,
                )
                logger.info("LLM raporu başarıyla oluşturuldu (OpenAI)")
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"OpenAI API hatası, fallback'e geçiliyor: {e}")
                return None

        logger.info("LLM API anahtarı bulunamadı, kural tabanlı rapora geçiliyor")
        return None

    except Exception as e:
        logger.warning(f"LLM entegrasyonu başarısız: {e}")
        return None


def _generate_rule_based_report(context: dict) -> str:
    """
    Kural tabanlı (fallback) yönetim raporu oluşturur.
    LLM API erişilemediğinde otomatik olarak kullanılır.

    Args:
        context (dict): Rapor bağlam verileri.

    Returns:
        str: Markdown formatında kural tabanlı rapor.
    """
    # Dinamik aksiyon planı kararı
    hrp = context["high_risk_percentage"]
    if hrp > 20:
        action_plan = (
            "- 🚨 **Kritik Durum:** Yüksek riskli müşteri oranı %20'yi aşıyor. "
            "Acil bir elde tutma (retention) kampanyası başlatılmalı.\n"
            "- VIP müşterilere özel müşteri temsilcisi atanmalıdır.\n"
            "- Yüksek bakiyeli müşterilere faiz avantajı sunulmalıdır."
        )
    elif hrp > 10:
        action_plan = (
            "- ⚠️ **Uyarı:** Riskli müşteri sayısı dikkat çekici. "
            "Mevcut kredi kartı ve faiz oranları rakiplerle karşılaştırılarak revize edilmelidir.\n"
            "- Orta riskli müşterilere sadakat programı başlatılmalıdır."
        )
    else:
        action_plan = (
            "- ✅ **Stabil Durum:** Churn riski genel olarak kontrol altında. "
            "Sadakat programları (loyalty programs) ile mevcut durum korunmalıdır."
        )

    # Risk dağılımı tablosu
    risk_table = f"""| Risk Seviyesi | Müşteri Sayısı | Oran |
|:---|:---:|:---:|
| 🔴 Yüksek | {context['high_risk_customers']} | %{context['high_risk_percentage']:.1f} |
| 🟡 Orta | {context['medium_risk_customers']} | %{(context['medium_risk_customers']/context['total_customers']*100) if context['total_customers'] > 0 else 0:.1f} |
| 🟢 Düşük | {context['low_risk_customers']} | %{(context['low_risk_customers']/context['total_customers']*100) if context['total_customers'] > 0 else 0:.1f} |"""

    report = f"""# 📊 Şube Yönetim Özeti Raporu

## 🎯 Mevcut Durum Analizi
Toplam **{context['total_customers']}** müşteri analiz edilmiştir. Bu müşteriler arasından **{context['high_risk_customers']}** tanesi (%{context['high_risk_percentage']:.1f}) yüksek ayrılma (churn) riski taşımaktadır.
Eğer önlem alınmazsa, bankamızın karşılaşacağı toplam beklenen finansal kayıp **€{context['total_expected_loss']:,.2f}** seviyesindedir.

## 📈 Risk Dağılımı
{risk_table}

## 🔝 En Yüksek Riskli Müşteriler
{context['top5_text']}

## 🛠️ Önerilen Stratejik Aksiyon Planı
{action_plan}

## 📌 Önceliklendirme
Lütfen sisteme yüklediğiniz dosyadaki **Yüksek Riskli** müşterilerle CLTV (Müşteri Yaşam Boyu Değeri) sırasına göre acilen iletişime geçin.

---
*Bu rapor otomatik olarak oluşturulmuştur. LLM API anahtarı tanımlandığında yapay zeka destekli detaylı raporlar üretilecektir.*
"""
    return report


def generate_management_report(df_summary: pd.DataFrame) -> str:
    """
    Yönetim Raporu Üretici (Hibrit: LLM + Kural Tabanlı Fallback).
    Önce LLM API'si denenilir, erişilemezse kural tabanlı rapora geçilir.

    Args:
        df_summary (pd.DataFrame): Toplu analiz sonucu DataFrame.

    Returns:
        str: Markdown formatında yönetim raporu.
    """
    if df_summary is None or df_summary.empty:
        return "⚠️ Rapor oluşturulabilmesi için analiz edilecek veri bulunamadı."

    context = _build_report_context(df_summary)

    # Önce LLM dene
    llm_report = _generate_llm_report(context)
    if llm_report:
        return llm_report

    # Fallback: Kural tabanlı rapor
    logger.info("Kural tabanlı yönetim raporu oluşturuluyor")
    return _generate_rule_based_report(context)


if __name__ == "__main__":
    from core.logging_config import get_logger as _get_logger
    _logger = _get_logger(__name__)
    # Test amaçlı
    test_state = run_agent(
        customer_id="123", churn_probability=0.85, risk_level="Yüksek"
    )
    _logger.info(f"Test sonucu: {test_state}")
