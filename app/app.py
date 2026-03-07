
from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.neural_network import MLPClassifier
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DL-TOLMON API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

raw = pd.read_excel("../data_tol.xlsx", header=None)
raw.columns = [f"G{i}" for i in range(1,7)]
records = []
for col in raw.columns:
    for t in raw[col].dropna():
        records.append((pd.to_datetime(t), col, 1))
events = pd.DataFrame(records, columns=["timestamp","gate","vehicle"])
pivot = events.assign(v=1).pivot_table(index="timestamp", columns="gate", values="v", aggfunc="sum", fill_value=0).reset_index().sort_values("timestamp")
pivot["total_vehicles"] = pivot[[f"G{i}" for i in range(1,7)]].sum(axis=1)
def make_label(n):
    if n <= 2:
        return "LOW"
    elif n <= 4:
        return "MEDIUM"
    return "HEAVY"
pivot["Label"] = pivot["total_vehicles"].apply(make_label)
X = pivot[[f"G{i}" for i in range(1,7)]].values
y = pivot["Label"].values
le = LabelEncoder()
y_enc = le.fit_transform(y)
X_train, X_test, y_train, y_test = train_test_split(X, y_enc, test_size=0.2, random_state=42)
model = MLPClassifier(hidden_layer_sizes=(32,64,32), activation="relu", solver="adam", learning_rate_init=0.001, max_iter=300, random_state=42)
model.fit(X_train, y_train)

class TrafficIn(BaseModel):
    G1: int
    G2: int
    G3: int
    G4: int
    G5: int
    G6: int

@app.get("/")
def root():
    return {"app": "DL-TOLMON API", "status": "ready"}

@app.post("/predict")
def predict(item: TrafficIn):
    arr = np.array([[item.G1, item.G2, item.G3, item.G4, item.G5, item.G6]])
    pred = model.predict(arr)[0]
    label = le.inverse_transform([pred])[0]
    total = int(arr.sum())
    recommendation = "GO" if label == "LOW" else ("CAUTION" if label == "MEDIUM" else "NOT GO")
    return {"label": label, "total_vehicles": total, "recommendation": recommendation}
