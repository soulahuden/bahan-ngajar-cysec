# Linux Command Wargame (ala OverTheWire Bandit)

Wargame SSH sederhana untuk melatih siswa SMK memakai command line Linux.
Siswa login lewat SSH sebagai `level0`, menyelesaikan soal untuk menemukan
password `level1`, lalu login sebagai `level1`, dan seterusnya sampai
`level3` yang menghasilkan FLAG akhir.

## Daftar level

| Level | Skill yang dilatih | Login sebagai |
|---|---|---|
| 0 -> 1 | Nama file mengandung spasi (quoting / tab-completion) | level0 |
| 1 -> 2 | File tersembunyi `.flag` (`ls -la`) | level1 |
| 2 -> 3 | File berisi data biner, dibaca dengan `strings` | level2 |
| 3 -> FLAG | 200 file isi kata random, satu berisi flag (`cat *`) | level3 |

Password `level0` sengaja dibuat publik (`level0`), sama seperti `bandit0`
di OverTheWire, karena itu adalah titik masuk. Password level1-3 dan FLAG
akhir di-random tiap kali image di-build, tersimpan di dalam container di
`/root/ANSWER_KEY.txt` (hanya bisa dibaca root/guru).

## Build & jalankan (lokal, untuk uji coba)

```bash
cd linux-wargame
docker compose build
docker compose up -d
```

Cek port yang dipakai (default `2222`) lalu coba login:

```bash
ssh level0@127.0.0.1 -p 2222
# password: level0
```

## Lihat kunci jawaban (untuk guru)

```bash
docker exec -it linux-wargame cat /root/ANSWER_KEY.txt
```

Simpan output ini di tempat aman (jangan dibagikan ke siswa). Kalau perlu
password baru (misal untuk kelas/angkatan berikutnya), cukup build ulang
image (`docker compose build --no-cache`) — semua password & FLAG akan
di-random ulang.

## Deploy ke VPS

1. Salin folder `linux-wargame/` ke VPS (via `git`, `scp`, atau `rsync`).
2. Pastikan Docker & Docker Compose terpasang di VPS.
3. Sesuaikan port publik di `docker-compose.yml` kalau perlu (default
   `2222:22`). Pakai port non-standar mengurangi noise bot scanning.
4. Build & jalankan:
   ```bash
   docker compose build
   docker compose up -d
   ```
5. Ambil kunci jawaban dengan `docker exec` seperti di atas, simpan untuk
   diri sendiri.
6. Bagikan ke siswa: alamat IP/domain VPS, port yang dipakai, dan
   `ssh level0@<ip> -p <port>` dengan password `level0`. Banner SSH juga
   sudah menampilkan info ini otomatis saat mereka connect.

### Catatan keamanan untuk VPS

- **Ini adalah container multi-user dengan shell SSH sungguhan** — siswa
  bisa menjalankan command bebas di dalam container (tapi tidak di host
  VPS, selama Docker terkonfigurasi normal). Jangan mount Docker socket
  atau folder sensitif host ke dalam container ini.
- Semua sesi SSH berbagi satu kernel/namespace proses, jadi siswa yang
  jeli bisa melihat proses siswa lain lewat `ps aux` — ini sama seperti
  keterbatasan level awal di Bandit asli, bukan bug.
- Disarankan pasang **fail2ban** atau batasi rate percobaan SSH di level
  host VPS untuk mencegah brute force ke akun level1-level3 dari luar
  kelas.
- Container dibatasi memori (`mem_limit`) dan jumlah proses
  (`pids_limit`) di `docker-compose.yml` supaya satu siswa nakal (fork
  bomb, dsb.) tidak menghabiskan resource VPS. Sesuaikan angkanya kalau
  perlu.
- Reset progres: kalau container jalan lama dan ingin di-reset ke kondisi
  awal, cukup:
  ```bash
  docker compose down
  docker compose up -d --force-recreate
  ```
  (password akan tetap sama selama image tidak di-build ulang; untuk
  password baru gunakan `docker compose build --no-cache`).

## Menambah level baru

Semua logika pembuatan soal ada di satu file: `setup-levels.sh`, yang
dijalankan sekali saat `docker build`. Pola untuk tiap level:

1. Tambah user baru: `useradd -m -s /bin/bash levelN` lalu set password.
2. Simpan password level berikutnya (atau FLAG untuk level terakhir) ke
   dalam sebuah file/tantangan di home directory `levelN`, sesuai skill
   yang ingin dilatih.
3. Tambahkan `levelN` ke daftar `AllowUsers` di `sshd_config`.
4. Tambahkan barisnya ke `ANSWER_KEY.txt` di bagian akhir skrip.

## Struktur file

```
linux-wargame/
├── Dockerfile
├── docker-compose.yml
├── sshd_config        # konfigurasi SSH server (hardened, AllowUsers dibatasi)
├── banner.txt         # pesan yang tampil sebelum login SSH
├── setup-levels.sh    # membuat semua akun + soal tiap level (jalan saat build)
├── entrypoint.sh       # start sshd saat container jalan
├── howtosolve.txt      # walkthrough command penyelesaian tiap level (untuk guru)
└── README.md
```
