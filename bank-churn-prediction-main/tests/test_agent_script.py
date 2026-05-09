import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.churn_agent import run_agent
import logging

logging.basicConfig(level=logging.DEBUG)

customer_data = {
    "Age": 45,
    "CreditScore": 400,
    "Balance": 100000,
    "EstimatedSalary": 50000,
    "NumOfProducts": 1,
}

print("Running agent...")
result = run_agent(
    customer_id="TEST-1",
    churn_probability=0.85,
    risk_level="Yüksek",
    customer_data=customer_data
)

print("Agent Result:")
print("Gemini:", result.get("gemini_campaign"))
print("Groq:", result.get("groq_campaign"))
print("OpenAI:", result.get("openai_campaign"))
print("Campaign Message (fallback):", result.get("campaign_message"))
