DL-TOLMON app

1. Open terminal in the `app` folder.
2. Install packages: `pip install -r requirements.txt`
3. Run API: `uvicorn app:app --reload`
4. Open `dashboard_live.html` in a browser.
5. For live integration, connect the dashboard JavaScript to `http://127.0.0.1:8000/predict`.

Manual API test:
POST /predict
{
  "G1": 1,
  "G2": 0,
  "G3": 1,
  "G4": 0,
  "G5": 0,
  "G6": 0
}
