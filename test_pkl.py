import joblib

pack = joblib.load('bank-churn-prediction-main/churn_thesis_model.pkl')
print(type(pack['model']))
print(type(pack['scaler']))
print(pack['features'])
