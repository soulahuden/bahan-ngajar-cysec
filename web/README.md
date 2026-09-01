# Web Exploitation CTF (untuk siswa SMK)

Tiga soal web exploitation dasar, masing-masing self-contained (folder +
Dockerfile sendiri), semuanya bertema satu perusahaan fiktif "PT Maju
Bersama" biar terasa satu skenario pentest.

## Daftar soal

| # | Nama | Skill | Port lokal |
|---|---|---|---|
| 1 | Inspector | Baca HTML source / Inspect Element | 8001 |
| 2 | robots.txt | Reconnaissance lewat robots.txt | 8002 |
| 3 | Cookies Admin | Manipulasi cookie (bisa pakai Burp Suite) | 8003 |

Flag bersifat statis (sama tiap kali di-build ulang), format `FLAG{...}`:

| Soal | Flag |
|---|---|
| Inspector | `FLAG{inspect_the_source}` |
| robots.txt | `FLAG{robots_txt_isnt_security}` |
| Cookies Admin | `FLAG{cookie_trust_issue}` |

Kalau mau ganti flag (misal biar tidak sama persis dengan yang ada di
repo ini kalau dipakai lintas kelas/tahun), tinggal edit langsung:
- Inspector & robots.txt: cari teks `FLAG{...}` di file HTML terkait
  (`01-inspector/html/index.html`,
  `02-robots-txt/html/internal-notes-x7k2q/index.html`).
- Cookies Admin: ubah baris `ENV FLAG=...` di
  `03-cookies-admin/Dockerfile`.

Semua flag juga tersalin ke `/answer_key.txt` di dalam masing-masing
container saat build, untuk kemudahan referensi guru.

## Build & jalankan (semua sekaligus)

```bash
cd web-ctf
docker compose build
docker compose up -d
```

Akses:
- Inspector: http://localhost:8001
- robots.txt: http://localhost:8002
- Cookies Admin: http://localhost:8003

## Lihat kunci jawaban (untuk guru)

```bash
docker exec web-ctf-inspector       cat /answer_key.txt
docker exec web-ctf-robots-txt      cat /answer_key.txt
docker exec web-ctf-cookies-admin   cat /answer_key.txt
```

## Deploy ke VPS

Sama seperti `linux-wargame/`: salin folder ini ke VPS, sesuaikan port
publik di `docker-compose.yml` kalau perlu (default 8001-8003), lalu
`docker compose build && docker compose up -d`. Kalau mau digabung jadi
satu domain (misal `web1.namadomain.com`, `web2.namadomain.com`, dst),
tinggal pasang reverse proxy (nginx/Caddy) di depan ketiga port ini —
tidak wajib untuk kelas kecil, akses lewat `http://ip-vps:PORT` juga
sudah cukup.

Untuk soal Cookies Admin, siswa boleh pakai DevTools browser (F12 >
Application/Storage > Cookies) atau intercept request dengan Burp Suite
untuk mengubah cookie-nya — keduanya jalan karena server memang cuma
percaya begitu saja pada value cookie yang dikirim client (tanpa
signature/verifikasi), itulah inti kerentanannya.

## Struktur folder

```
web-ctf/
├── docker-compose.yml
├── howtosolve.txt          # walkthrough tiap soal (untuk guru)
├── 01-inspector/
│   ├── Dockerfile
│   └── html/ (index.html, style.css)
├── 02-robots-txt/
│   ├── Dockerfile
│   └── html/ (index.html, robots.txt, style.css, internal-notes-x7k2q/index.html)
└── 03-cookies-admin/
    ├── Dockerfile
    ├── requirements.txt
    ├── app.py
    ├── templates/ (index.html, flag_ok.html, flag_denied.html)
    └── static/style.css
```
