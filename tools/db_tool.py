import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_community.agent_toolkits import create_sql_agent

load_dotenv()
url_database = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', '127.0.0.1')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_DATABASE', 'SAGE')}"

tabel_penting = [
    "delivery_receipt_details", "delivery_receipts", "driver",  
    "logistic", "logistic_scans", "returns", "return_details",
    "stores", "store_stocks", "turnovers", "turnover_details", "vehicle"
]

db = SQLDatabase.from_uri(
    url_database,
    include_tables=tabel_penting,
    sample_rows_in_table_info=3  
)

llm_sql = ChatGroq(
    model="openai/gpt-oss-120b", 
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0 
)


instruksi_khusus = """Kamu adalah asisten AI ahli dalam menganalisis data logistik PT Sage.
Tugasmu adalah membuat query SQL MySQL yang akurat untuk menjawab pertanyaan pengguna.

Panduan penting:
1. Pahami terjemahan istilah: "sopir" (tabel driver), "kendaraan" (tabel vehicle), dsb.
2. Jangan pernah melakukan operasi DML (INSERT, UPDATE, DELETE). Hanya gunakan SELECT.
3. SEMBUNYIKAN UUID: Jangan pernah menampilkan kolom ID yang berbentuk UUID panjang (seperti 451f290f-...) di dalam tabel jawaban akhirmu. Cukup gunakan "Nama" atau identifier lain yang mudah dibaca manusia.
4. BATAS DATA (LIMIT): Jika pengguna meminta "semua data" atau "data driver", jangan gunakan LIMIT 3. Gunakan LIMIT 50 agar lebih banyak data yang tampil, kecuali pengguna secara spesifik meminta jumlah tertentu.
5. Susun jawaban menggunakan tabel Markdown yang rapi tanpa kolom ID.
"""

sql_agent_executor = create_sql_agent(
    llm=llm_sql,
    db=db,
    agent_type="tool-calling",
    verbose=True,
    handle_parsing_errors=True,
    prefix=instruksi_khusus 
)

@tool
def alat_baca_database(pertanyaan: str) -> str:
    """
    Gunakan alat ini HANYA JIKA pengguna bertanya tentang data metrik, angka, 
    status driver, jumlah stok, atau informasi tabel dari database MySQL logistik perusahaan.
    """
    print("🤖 [Sistem]: Agen sedang menganalisis dan mengeksekusi Query SQL...")
    try:
        hasil = sql_agent_executor.invoke({"input": pertanyaan})
        
        if isinstance(hasil, dict) and "output" in hasil:
            return str(hasil["output"])
        return str(hasil)
        
    except Exception as e:
        return f"Gagal mengeksekusi database MySQL. Error: {str(e)}"