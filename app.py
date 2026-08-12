import sys
import os

import certifi
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()
mongo_db_url = os.getenv("MONGODB_URL_KEY")
print(mongo_db_url)
import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Request
from uvicorn import run as app_run
from fastapi.responses import Response
import pandas as pd

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel


client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)

from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from networksecurity.constant.training_pipeline import DATA_INGESTION_DATABASE_NAME

database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Single source of truth for "/" — serves the frontend directly.
# (Previously there were two competing @app.get("/") routes; FastAPI matched
# whichever was registered first, so the redirect to /docs always won and the
# frontend never loaded. Removed the redirect route entirely.)
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Simple health check — used by Render and by the frontend's status dot.
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/train")
async def train_route():
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise NetworkSecurityException(e, sys)


@app.post("/predict")
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
        preprocesor = load_object("final_model/preprocessor.pkl")
        final_model = load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocesor, model=final_model)

        y_pred = network_model.predict(df)
        df['predicted_column'] = y_pred

        # Ensure the output directory exists — on a fresh clone (e.g. Render),
        # this folder won't exist yet since it's generated output, not committed.
        os.makedirs("prediction_output", exist_ok=True)
        df.to_csv('prediction_output/output.csv')

        table_html = df.to_html(classes='table table-striped')
        return templates.TemplateResponse(
            "table.html", {"request": request, "table": table_html}
        )

    except Exception as e:
        raise NetworkSecurityException(e, sys)


if __name__ == "__main__":
    # Render's Docker runtime assigns a dynamic port via $PORT — falls back to
    # 8000 for local `python3 app.py` runs where $PORT isn't set.
    port = int(os.environ.get("PORT", 8000))
    app_run(app, host="0.0.0.0", port=port)