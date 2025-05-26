import os
import pandas as pd

UPLOAD_FOLDER = "uploads"

def save_uploaded_file(project_name, file):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = f"{project_name}.csv"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    return filepath

def preview_data(project_name, n=10):
    filepath = os.path.join(UPLOAD_FOLDER, f"{project_name}.csv")
    if not os.path.exists(filepath):
        return None
    df = pd.read_csv(filepath)
    return df.head(n).to_dict(orient="records")
