from celery import Celery
import pandas as pd
import os
import joblib
from pycaret.classification import *
from pycaret.regression import *

celery = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

UPLOAD_FOLDER = "uploads"
MODEL_FOLDER = "models"
os.makedirs(MODEL_FOLDER, exist_ok=True)

@celery.task
def train_model(filename, target):
    path = os.path.join(UPLOAD_FOLDER, filename)
    df = pd.read_csv(path)

    if df[target].dtype == "object":
        setup(df, target=target, silent=True)
        best = compare_models()
    else:
        setup(df, target=target, silent=True)
        best = compare_models()

    model_name = f"{filename}_model.pkl"
    joblib.dump(best, os.path.join(MODEL_FOLDER, model_name))

    return {"model_file": model_name}