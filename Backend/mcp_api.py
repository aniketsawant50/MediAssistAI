from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from App.MCP.query_router import ask_database

app = FastAPI(
    title="MediAssist MCP API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():

    return {
        "status": "running",
        "service": "MediAssist MCP"
    }


@app.get("/ask")
def ask(query: str):

    result = ask_database(query)

    return result