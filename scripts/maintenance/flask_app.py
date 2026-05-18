import sqlite3
from flask import Flask, request, jsonify
from services.model_loader import ModelLoader
from services.prediction_service import PredictionService

app = Flask(__name__)

# Initialize SQLite database for storing predictions
def init_db():
    conn = sqlite3.connect("predictions.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_data TEXT,
            churn_tahmini INTEGER,
            churn_ihtimali REAL,
            risk_seviyesi TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        loader = ModelLoader("churn_thesis_model.skops")
        loader.load()
        prediction_service = PredictionService(
            model=loader.get_model(),
            scaler=loader.get_scaler(),
            expected_features=loader.get_features()
        )
        
        result = prediction_service.predict_one(data)
        
        # Save to SQLite
        conn = sqlite3.connect("predictions.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO predictions 
            (customer_data, churn_tahmini, churn_ihtimali, risk_seviyesi) 
            VALUES (?, ?, ?, ?)
        """, (str(data), result["churn_tahmini"], result["churn_ihtimali"], result["risk_seviyesi"]))
        conn.commit()
        conn.close()
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(port=5000, debug=True)
