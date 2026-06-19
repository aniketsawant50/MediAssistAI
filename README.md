
1. Run the ingest file
python -m App.ingest

2. Run the backend
 uvicorn Backend.main:app --reload

3. Run the streamlit
streamlit run ui/streamlit.py
