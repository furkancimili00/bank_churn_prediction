from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

# Durum tanımı (State)
class CustomerState(TypedDict):
    customer_id: Optional[str]
    churn_probability: float
    risk_level: str
    recommended_action: Optional[str]

# Düğüm: Aksiyon Belirleyici
def determine_action(state: CustomerState) -> CustomerState:
    """
    Müşterinin risk seviyesine göre alınacak otomatik aksiyonu belirler.
    """
    prob = state.get("churn_probability", 0.0)

    if prob >= 0.70:
        action = "Acil İletişim & %20 İndirim Maili Gönder"
    elif prob >= 0.40:
        action = "Kredi Kartı Kampanyası Öner"
    else:
        action = "İşlem Yok (Sadık Müşteri)"

    state["recommended_action"] = action
    return state

# Ajan Akışını (Graph) Oluşturma
workflow = StateGraph(CustomerState)

# Düğümleri ekleme
workflow.add_node("determine_action_node", determine_action)

# Akışı bağlama (Edge'ler)
workflow.set_entry_point("determine_action_node")
workflow.add_edge("determine_action_node", END)

# Çalıştırılabilir uygulamayı (Agent) derleme
agent_app = workflow.compile()

def run_agent(customer_id: str, churn_probability: float, risk_level: str) -> CustomerState:
    """
    Dışarıdan çağrılacak ana ajan fonksiyonu.
    """
    initial_state = CustomerState(
        customer_id=customer_id,
        churn_probability=churn_probability,
        risk_level=risk_level,
        recommended_action=None
    )

    result = agent_app.invoke(initial_state)
    return result

if __name__ == "__main__":
    # Test amaçlı
    test_state = run_agent(customer_id="123", churn_probability=0.85, risk_level="Yüksek")
    print(test_state)
