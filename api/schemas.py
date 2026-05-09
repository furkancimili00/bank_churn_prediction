from pydantic import BaseModel, Field

class CustomerData(BaseModel):
    """Tekil müşteri verisi şeması."""
    CreditScore: int = Field(..., ge=300, le=850, description="Müşterinin kredi notu (300-850)")
    Geography: str = Field(..., description="Müşterinin bulunduğu ülke (örn: France, Germany, Spain)")
    Gender: str = Field(..., description="Müşterinin cinsiyeti (Male, Female)")
    Age: int = Field(..., ge=18, le=100, description="Müşterinin yaşı (18-100)")
    Tenure: int = Field(..., ge=0, le=20, description="Müşterinin bankayla çalışma süresi (yıl)")
    Balance: float = Field(..., ge=0.0, description="Hesap bakiyesi")
    NumOfProducts: int = Field(..., ge=1, le=10, description="Kullandığı ürün sayısı")
    HasCrCard: int = Field(..., ge=0, le=1, description="Kredi kartı var mı? (1: Evet, 0: Hayır)")
    IsActiveMember: int = Field(..., ge=0, le=1, description="Aktif üye mi? (1: Evet, 0: Hayır)")
    EstimatedSalary: float = Field(..., ge=0.0, description="Tahmini yıllık maaşı")

class BatchCustomerData(BaseModel):
    """Toplu müşteri verisi şeması."""
    customers: list[CustomerData]
