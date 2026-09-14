import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings 

from langchain_community.document_loaders import (
    PyPDFLoader, 
    Docx2txtLoader, 
    UnstructuredExcelLoader
)

load_dotenv(override=True)

embedding_model = FastEmbedEmbeddings()

LOKASI_DB = "./vector_db"

def inisialisasi_db():
    return Chroma(persist_directory=LOKASI_DB, embedding_function=embedding_model)

def simpan_dokumen_ke_db(file_path: str, nama_file: str):
    """Menerima dan memproses PDF, Word (.docx), atau Excel (.xlsx)"""
    print(f"📥 [Sistem]: Menerima dokumen baru -> {nama_file}")
    
    try:
        nama_file_kecil = nama_file.lower()
        
        if nama_file_kecil.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif nama_file_kecil.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
        elif nama_file_kecil.endswith(".xlsx") or nama_file_kecil.endswith(".xls"):
            loader = UnstructuredExcelLoader(file_path, mode="elements")
        else:
            return f"❌ Format tidak didukung. Harap unggah PDF, DOCX, atau XLSX: {nama_file}"

        dokumen_mentah = loader.load()
        
        pemotong = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        potongan_teks = pemotong.split_documents(dokumen_mentah)

        Chroma.from_documents(
            documents=potongan_teks, 
            embedding=embedding_model, 
            persist_directory=LOKASI_DB
        )
        
        print(f"✅ [Sistem]: SUKSES! {len(potongan_teks)} potongan teks disimpan ke ChromaDB.")
        return "✅ Dokumen berhasil dianalisis dan disimpan ke memori AI."
        
    except Exception as e:
        print(f"❌ [Sistem]: GAGAL MEMPROSES DOKUMEN! Error: {str(e)}")
        return f"Gagal memproses dokumen: {str(e)}"


# ... (Bagian import dan inisialisasi_db di atas TETAP SAMA)

@tool
def alat_baca_dokumen(pertanyaan: str) -> str:
    """
    Gunakan alat ini JIKA pengguna bertanya tentang informasi dari dokumen, 
    laporan, pedoman, PDF, Microsoft Word, atau Microsoft Excel yang telah diunggah.
    """
    print("🤖 [Sistem]: Agen mencari dokumen menggunakan algoritma MMR...")
    try:
        db_vektor = Chroma(persist_directory=LOKASI_DB, embedding_function=embedding_model)
        
        # Menerapkan MMR: AI mengambil 20 kandidat (fetch_k), lalu memilih 4 yang paling beragam (k)
        hasil_pencarian = db_vektor.max_marginal_relevance_search(pertanyaan, k=4, fetch_k=20)
        
        if not hasil_pencarian:
            return "Maaf, tidak ditemukan informasi yang relevan di dokumen."
            
        teks_konteks = "\n\n".join([doc.page_content for doc in hasil_pencarian])
        return f"Informasi dari dokumen:\n{teks_konteks}"
        
    except Exception as e:
        return f"Gagal membaca dokumen. Error: {str(e)}"

@tool
def cek_daftar_dokumen(pertanyaan: str = "") -> str:
    """
    Gunakan alat ini HANYA JIKA pengguna menanyakan daftar dokumen, file, atau laporan 
    apa saja yang sudah diunggah/tersimpan di dalam sistem saat ini.
    """
    print("🤖 [Sistem]: Agen merekap daftar dokumen di ChromaDB...")
    try:
        db_vektor = Chroma(persist_directory=LOKASI_DB, embedding_function=embedding_model)
        
        data = db_vektor.get(include=["metadatas"])
        metadatas = data.get("metadatas", [])
        
        if not metadatas:
            return "Saat ini belum ada dokumen yang diunggah ke sistem."

        daftar_file = set()
        for meta in metadatas:
            if meta and "source" in meta:
                nama_file = os.path.basename(meta["source"])
                daftar_file.add(nama_file)

        if not daftar_file:
            return "Dokumen ada, tapi sistem tidak menemukan riwayat nama filenya."

        hasil = "Daftar dokumen yang tersedia di sistem saat ini:\n"
        for i, nama in enumerate(sorted(daftar_file), 1):
            hasil += f"{i}. {nama}\n"
        return hasil
        
    except Exception as e:
        return f"Gagal mengambil daftar dokumen. Error: {str(e)}"