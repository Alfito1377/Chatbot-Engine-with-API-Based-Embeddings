import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from tools.db_tool import alat_baca_database
from tools.doc_tool import alat_baca_dokumen, cek_daftar_dokumen
from langchain_core.messages import SystemMessage

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b", 
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

daftar_alat = [alat_baca_database, alat_baca_dokumen]

instruksi_sistem = """Kamu adalah asisten AI internal PT Sage Mashlahat Indonesia.
Tugas utamamu adalah merespons pertanyaan pengguna dengan cepat dan memilih SATU alat yang paling tepat.

ATURAN MUTLAK:
1. DATABASE (alat_baca_database): Gunakan HANYA untuk pertanyaan seputar data transaksi, metrik, status, angka, atau isi tabel (misal: "data driver", "jumlah pengiriman", "stok di toko").
2. DOKUMEN (alat_baca_dokumen): Gunakan HANYA untuk pertanyaan konseptual seperti pedoman, kebijakan, SOP, atau regulasi perusahaan.
3. DILARANG BOLAK-BALIK ALAT. Cukup pilih 1 alat yang paling relevan, ambil datanya, buat kesimpulan, dan BERHENTI mencari.
4. Jika pertanyaan ambigu atau tidak jelas, JANGAN panggil alat apa pun. Langsung tanya pengguna agar lebih spesifik.
5. Susun jawaban akhir menggunakan Markdown yang rapi (gunakan poin-poin atau tabel jika perlu).
"""

memory = MemorySaver()

agent_executor = create_react_agent(
    llm, 
    tools=daftar_alat, 
    checkpointer=memory
)


def tanya_agen(pertanyaan_user: str, thread_id: str = "sesi_default") -> str:
    try:
        config = {"configurable": {"thread_id": thread_id}}

        respons = agent_executor.invoke(
            {"messages": [
                SystemMessage(content=instruksi_sistem),
                ("user", pertanyaan_user)
            ]},
            config=config
        )

        jawaban_mentah = respons["messages"][-1].content

        if isinstance(jawaban_mentah, str):
            jawaban_ai = jawaban_mentah
        elif isinstance(jawaban_mentah, list):
            jawaban_ai = "".join([
                bagian.get("text", "") if isinstance(bagian, dict) else str(bagian) 
                for bagian in jawaban_mentah
            ])
        else:
            jawaban_ai = str(jawaban_mentah)

        return jawaban_ai

    except Exception as e:
        return f"Maaf, agen mengalami kendala: {str(e)}"