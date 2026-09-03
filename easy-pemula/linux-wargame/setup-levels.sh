#!/bin/bash
# Dijalankan sekali saat "docker build" untuk membuat akun level0..level3,
# dan menyiapkan soal tiap level.
#
# Setiap level punya DUA string:
#   1. FLAG   -> STATIC, disubmit ke CTFd
#   2. PASS   -> RANDOM, dipakai untuk SSH ke level selanjutnya
# Ganti nilai FLAG di bawah sebelum `docker build` bila perlu.
set -euo pipefail

genpass() { tr -dc 'A-Za-z0-9' </dev/urandom | head -c 20 || true; }

# --- Password SSH tiap level (random tiap build) ---
declare -A PASS
PASS[0]="level0"
for i in 1 2 3; do
  PASS[$i]="$(genpass)"
done

# --- Flag CTFd tiap level (static) ---
declare -A FLAG
FLAG[0]="FLAG{sp4s1_d1_n4m4_f1l3}"
FLAG[1]="FLAG{h1dd3n_f1l3_d0tf1l3}"
FLAG[2]="FLAG{str1ngs_b1n4ry_r34d}"
FLAG[3]="FLAG{gr3p_r3curs1v3_m4st3r}"

for i in 0 1 2 3; do
  useradd -m -s /bin/bash "level$i"
  echo "level$i:${PASS[$i]}" | chpasswd
  # kunci home directory supaya user lain tidak bisa mengintip nama file
  chmod 700 "/home/level$i"
done

# ---------- Level 0 -> 1 : nama file mengandung spasi ----------
{
  echo "${FLAG[0]}"
  echo "Password untuk ke level selanjutnya: ${PASS[1]}"
} > "/home/level0/spasi di nama file ini"
chown level0:level0 "/home/level0/spasi di nama file ini"
chmod 600 "/home/level0/spasi di nama file ini"

# ---------- Level 1 -> 2 : hidden file .flag ----------
{
  echo "${FLAG[1]}"
  echo "Password untuk ke level selanjutnya: ${PASS[2]}"
} > "/home/level1/.flag"
chown level1:level1 "/home/level1/.flag"
chmod 600 "/home/level1/.flag"

# ---------- Level 2 -> 3 : file biner, harus dibaca dengan `strings` ----------
{
  head -c 512 /dev/urandom
  echo
  echo "${FLAG[2]}"
  echo "Password untuk ke level selanjutnya: ${PASS[3]}"
  head -c 512 /dev/urandom
} > /home/level2/flag
chown level2:level2 /home/level2/flag
chmod 600 /home/level2/flag

# ---------- Level 3 : 200 file berisi 2 kata random, satu berisi FLAG ----------
WORDS=(langit rumah kucing meja lampu jalan gunung sungai kopi buku
       kertas jendela pintu mobil sepeda hujan angin pasir laut awan
       bintang bulan matahari daun pohon batu besi kayu kaca plastik)

mkdir -p /home/level3/data
target=137

for n in $(seq -w 1 200); do
  w1=${WORDS[$((RANDOM % ${#WORDS[@]}))]}
  w2=${WORDS[$((RANDOM % ${#WORDS[@]}))]}
  echo "$w1 $w2" > "/home/level3/data/file_$n.txt"
done

target_file=$(printf "/home/level3/data/file_%03d.txt" "$target")
echo "${FLAG[3]}" > "$target_file"

chown -R level3:level3 /home/level3/data
chmod 600 /home/level3/data/*

# ---------- Kunci jawaban untuk guru ----------
{
  echo "=== JAWABAN / ANSWER KEY (untuk guru saja, jangan dibagikan ke siswa) ==="
  echo "level0 password : ${PASS[0]}  (memang publik, ini titik awal)"
  echo "level1 password : ${PASS[1]}"
  echo "level2 password : ${PASS[2]}"
  echo "level3 password : ${PASS[3]}"
  echo
  echo "FLAG level0 (CTFd) : ${FLAG[0]}"
  echo "FLAG level1 (CTFd) : ${FLAG[1]}"
  echo "FLAG level2 (CTFd) : ${FLAG[2]}"
  echo "FLAG level3 (CTFd) : ${FLAG[3]}"
} > /root/ANSWER_KEY.txt
chmod 600 /root/ANSWER_KEY.txt
