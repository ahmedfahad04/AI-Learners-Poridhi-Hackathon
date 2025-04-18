from fastapi import APIRouter, File, UploadFile, HTTPException
import io
from database import QdrantDB

router = APIRouter()
db = QdrantDB()

@router.post("/upload_csv")
def upload_csv(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        num_uploaded = db.upload_csv_to_qdrant(io.BytesIO(contents))
        return {"message": f"Uploaded {num_uploaded} products to Qdrant."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
