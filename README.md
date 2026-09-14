Markdown
# JIKA PAKAI EMBEDDING FILE PAKAI API REPO INI,JIKA PAKAI PC KSI PAKE YANG REPO "ENGINEGROQ"
# Panduan Deployment - AI Service DDM PT Sage

Dokumen ini berisi catatan langkah-langkah teknis untuk melakukan *deploy* mesin AI (FastAPI & LangChain) ke server VPS berbasis Ubuntu.

---

## 1. Persiapan Server & Instalasi Modul Dasar
Masuk ke VPS melalui SSH, lalu jalankan perintah berikut untuk memperbarui sistem dan menginstal paket yang dibutuhkan:

```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx supervisor unzip -y
2. Pemindahan File & Pembuatan Lingkungan Virtual
Kompres folder agent, tools, vector_db, serta file .env, main.py, dan requirements.txt menjadi satu arsip bernama ai_backend.zip.

Unggah file zip tersebut ke direktori tujuan di server.

Selanjutnya, jalankan perintah ini di terminal server:

Bash
# Buat direktori tujuan dan ekstrak file
sudo mkdir -p /var/www/ai-sage
sudo unzip ai_backend.zip -d /var/www/ai-sage
cd /var/www/ai-sage

# Buat dan aktifkan virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Instal semua kebutuhan library
pip install -r requirements.txt
3. Konfigurasi Kredensial & Hak Akses
Sesuaikan konfigurasi pada file .env di dalam folder proyek:

Ubah DB_HOST dengan IP database MySQL (gunakan 127.0.0.1 jika database berada di server yang sama).

Pastikan GROQ_API_KEY sudah terisi dengan benar.

Berikan hak akses tulis pada folder vector_db supaya sistem ChromaDB bisa memproses dokumen dengan lancar tanpa kendala permission:

Bash
sudo chmod -R 775 /var/www/ai-sage/vector_db
sudo chown -R www-data:www-data /var/www/ai-sage/vector_db
4. Menjalankan AI di Background (Supervisor)
Buat file konfigurasi baru untuk Supervisor agar layanan FastAPI dapat berjalan otomatis 24/7 di latar belakang:

Bash
sudo nano /etc/supervisor/conf.d/ai-sage.conf
Isikan konfigurasi berikut ke dalamnya:

Ini, TOML
[program:ai-sage]
directory=/var/www/ai-sage
command=/var/www/ai-sage/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8001
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/ai-sage.err.log
stdout_logfile=/var/log/ai-sage.out.log
Simpan file (Ctrl+X, lalu Y, dan Enter), kemudian muat ulang Supervisor:

Bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ai-sage
5. Konfigurasi Nginx (Reverse Proxy)
Atur Nginx sebagai jembatan agar port internal 8001 dapat diakses melalui domain atau IP publik dengan aman:

Bash
sudo nano /etc/nginx/sites-available/ai-sage
Isikan blok kode berikut (sesuaikan server_name dengan domain atau IP VPS Anda):

Nginx
server {
    listen 80;
    server_name api-ai.domainanda.com;

    location / {
        proxy_pass [http://127.0.0.1:8001](http://127.0.0.1:8001);
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
Aktifkan konfigurasi tersebut dan lakukan restart Nginx:

Bash
sudo ln -s /etc/nginx/sites-available/ai-sage /etc/nginx/sites-enabled/
sudo systemctl restart nginx
6. Penyesuaian Aplikasi Laravel
Sebagai langkah terakhir, buka file .env pada proyek utama Laravel Anda, lalu arahkan alamat layanan ke URL server AI yang baru:

Cuplikan kode
AI_SERVICE_URL=[http://api-ai.domainanda.com](http://api-ai.domainanda.com)
