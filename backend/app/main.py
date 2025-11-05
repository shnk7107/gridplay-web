from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import telemetry, predict, battles
from app.db import init_db  # 👈 add this line

app = FastAPI(title="GridPlay API")

# initialize database tables
init_db()  # 👈 add this line

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(telemetry.router, prefix="/api/telemetry", tags=["telemetry"])
app.include_router(predict.router, prefix="/api/predict", tags=["predict"])
app.include_router(battles.router, prefix="/api/battles", tags=["battles"])

@app.get("/")
def root():
    return {"message": "GridPlay Backend Running"}
