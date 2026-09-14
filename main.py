import os
from fastapi import FastAPI
from pydantic import BaseModel

from agent.groq_agent import tanya_agen
from tools.doc_tool import simpan_dokumen_ke_db

app = FastAPI(title="AI Service DDM")

class DocumentPayload(BaseModel):
    file_path: str

@app.post("/chat")
async def chat_endpoint(data: dict):
    pertanyaan = data.get("pertanyaan", "")
    session_id = data.get("session_id", "sesi_default") 
    
    try:
        jawaban_ai = tanya_agen(pertanyaan, thread_id=session_id) 
        return {"jawaban": jawaban_ai, "sumber": "Sistem AI PT Sage"}
    except Exception as e:
        return {"jawaban": f"Error di mesin AI: {str(e)}", "sumber": "Error"}

@app.post("/webhook/document")
async def webhook_document(payload: DocumentPayload):
    try:
        lokasi_file = payload.file_path
        
        if not os.path.exists(lokasi_file):
            return {"status": "error", "message": f"File tidak ditemukan di: {lokasi_file}"}
            
        nama_file = os.path.basename(lokasi_file)
        
        pesan_status = simpan_dokumen_ke_db(lokasi_file, nama_file)
        
        return {"status": "success", "message": pesan_status}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}