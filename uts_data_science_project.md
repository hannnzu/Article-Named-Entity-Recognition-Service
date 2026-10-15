# UTS Data Science — Article Named-Entity Recognition (NER) Service

> Dokumen ini adalah **brief proyek** untuk dikerjakan bersama AI Agent di IDE.
> Isinya: ketentuan tugas (sesuai `study_case.pdf`), profil data hasil eksplorasi, daftar pekerjaan bertahap, dan checklist penyelesaian.
> **Aturan emas untuk agent:** semua persyaratan di bagian "Ketentuan Tugas" bersifat wajib. Jika ada konflik antara dokumen ini dan `study_case.pdf`, `study_case.pdf` yang benar.

---

## 0. Instruksi untuk AI Agent

1. Baca seluruh dokumen ini sebelum menulis kode.
2. Kerjakan **per fase** (Bagian 6). Jangan lompat fase. Setelah tiap fase selesai, jalankan tes/verifikasi dan centang checklist (Bagian 11).
3. Semua hasil harus **reproducible**: seed tetap, perintah terdokumentasi, versi dependensi tercatat.
4. **Jangan** meng-hard-code entitas untuk contoh demo.
5. **Jangan** menyalin/commit ulang data artikel asli dari dosen (`sample/`). Data dibaca dari path yang dikonfigurasi, dan `.gitignore` harus mengecualikannya.
6. **Jangan** menyentuh test set sampai evaluasi akhir. Catat jika ada pelanggaran.
7. Anotasi akhir yang dipakai untuk evaluasi **harus ditinjau manusia** (pengguna). Agent boleh membuat pra-anotasi (model-assisted), tetapi harus menandainya dan meminta pengguna mengoreksi.
8. Jika ada keputusan desain yang ambigu, tulis asumsinya di README, jangan diam-diam memilih.
9. Tulis kode yang sederhana dan bisa dijelaskan oleh mahasiswa saat presentasi. Hindari over-engineering.

---

## 1. Gambaran Tugas

Sebuah tim pemantau berita membutuhkan layanan kecil yang mengidentifikasi **named entity** dalam artikel. Pengguna memasukkan **judul** dan **isi** artikel pada sebuah panel web, lalu menerima daftar entitas yang ditemukan.

Tujuannya adalah **prototipe yang berfungsi**, bukan platform ekstraksi informasi berskala produksi. Asumsi harus eksplisit, pendekatan NLP harus beralasan, dan layanan harus didemonstrasikan pada artikel yang umum maupun yang sulit.

Pekerjaan kelompok/individu dinilai pada tiga area utama:

| Area | Fokus penilaian |
|---|---|
| **NER implementation** | Kebenaran pipeline terlatih/teradaptasi, span & label entitas, pemakaian data sampel, integrasi dengan layanan |
| **Evaluation** | Anotasi & split data yang sehat, training/testing reproducible, metrik yang tepat, perbandingan baseline, analisis error |
| **API design** | Kontrak input/output jelas, validasi, penanganan error, determinisme, koneksi andal antara panel dan pipeline NER akhir |

UI, kualitas kode, dokumentasi, dan diskusi penggunaan data yang bertanggung jawab menjadi pembeda antar submission yang setara.

**Konteks perkuliahan:** tugas dari praktisi industri (mata kuliah Data Science, sesi 3), tenggat dua minggu bertepatan dengan UTS (bisa diperpanjang jadi tiga minggu), nilai masuk komponen UTS, dikumpulkan sebagai repository publik atau `.zip`, lalu dipresentasikan.

---

## 2. Ketentuan Tugas (WAJIB)

### 2.1 Layanan web

- Panel yang menerima: (1) **judul artikel**, (2) **isi artikel**.
- Saat disubmit, layanan menganalisis **gabungan judul + isi** dan mengembalikan entitas.
- Stack: Python + **Flask atau FastAPI** (atau stack lain yang disetujui dosen).
- Boleh memakai model/library NER yang sudah ada, tetapi **wajib menjelaskan model apa yang dipilih dan alasannya**.
- Tidak perlu: akun pengguna, penyimpanan persisten, scraping artikel, deployment cloud.

### 2.2 Input API

Request JSON:

```json
{
  "title": "Example article title",
  "body": "The full article text goes here."
}
```

Aturan validasi (backend **dan** panel):

- `title` dan `body` harus bertipe **string**.
- Tolak (status **400**) jika: title dan body keduanya kosong, JSON malformed, atau input melebihi **batas panjang maksimum yang didokumentasikan**.

### 2.3 Output API

Untuk request valid, kembalikan JSON. Setiap entitas memuat:

| Field | Arti |
|---|---|
| `text` | Teks span yang terdeteksi (persis) |
| `label` | Kategori entitas, mis. `PERSON`, `ORG`, `GPE`, `LOC`, `DATE`, `EVENT` |
| `start` | Offset karakter awal (zero-based) pada teks yang dianalisis |
| `end` | Offset karakter akhir (eksklusif) pada teks yang dianalisis |

Contoh respons:

```json
{
  "entities": [
    {"text": "Ada Lovelace", "label": "PERSON", "start": 0, "end": 12},
    {"text": "London", "label": "GPE", "start": 28, "end": 34}
  ],
  "meta": {
    "entity_count": 2,
    "model": "documented-model-name"
  }
}
```

- Respons error harus jelas, sebaiknya HTTP **400** untuk request tidak valid.
- Output harus **deterministik** untuk input dan versi model yang sama.
- Offset `start`/`end` mengacu pada **teks gabungan yang dianalisis**; format penggabungan (mis. `title + "\n\n" + body`) harus didokumentasikan.

### 2.4 Persyaratan fungsional

- [ ] Panel browser dengan field judul dan isi
- [ ] Tombol submit + **status loading/processing** yang terlihat
- [ ] Tampilan terbaca untuk **teks entitas dan tipe entitas** (tabel sudah cukup)
- [ ] Endpoint backend yang menjalankan analisis NER
- [ ] Validasi input di panel **dan** backend
- [ ] Minimal **5 tes otomatis** atau test case reproducible
- [ ] README: instalasi, cara start, penggunaan API, pilihan model, keterbatasan

### 2.5 Spesifikasi teknis minimum

- Layanan berjalan **lokal** dengan perintah terdokumentasi.
- **Satu endpoint** ekstraksi, mis. `POST /extract-entities`, mengembalikan JSON + status HTTP yang sesuai.
- Panel **tidak boleh crash** ketika backend mengembalikan error.
- Entitas contoh demo **tidak boleh di-hard-code**.
- Dependensi dan versi model **dicatat** (`requirements.txt`/`package.json`, versi model di README/meta).
- Secret (jika ada) lewat **environment variable**, tidak di-commit.

---

## 3. Data yang Diberikan

### 3.1 Sumber dan format

- Lokasi menurut soal: `use_cases/pnm_study_case/sample/` (di repo dosen). Di mesin lokal, atur path lewat konfigurasi/env var, mis. `DATA_DIR`.
- 8 file CSV **berpemisah titik koma (`;`)**, ekspor artikel media online Malaysia (kliping Maybank, 07 Sep – 07 Okt 2026).
- Kolom penting: `title`, `body`, `language`, `entities`, `original_id`, `source_name`, `date_published`.
- Teks dikutip (quoted) → pastikan parser CSV **mempertahankan teks berkutip dengan benar** (gunakan `pandas.read_csv(sep=";")` atau modul `csv` dengan quoting yang benar).
- **Dilarang** commit salinan kedua artikel asli.

### 3.2 Pemetaan file → nama kliping

| # | Kliping | File (akhiran) |
|---|---|---|
| 1 | Hong Leong Bank | `...9xtqAsPitG.csv` |
| 2 | CIMB Group Malaysia | `...bRQ9afwSIP.csv` |
| 3 | Public Bank Berhad | `...4sxH8Dz0hr.csv` |
| 4 | RHB Bank | `...58yzyiBQ9U.csv` |
| 5 | MDV | `...WdjZl0bRfZ.csv` |
| 6 | Maybank CSR | `...i3BJEnT77K.csv` |
| 7 | Maybank Foundation | `...-nwub4cROX.csv` |
| 8 | Maybank Group | `...hMxhx9QLTq.csv` |

Nama lengkap file: `Maybank_Malaysia_OnlineMedia_07-Sep-2026_07-Oct-2026_<akhiran>`.

### 3.3 Hasil profiling awal (sudah diverifikasi)

> Agent harus **mereproduksi** angka-angka ini lewat skrip profiling dan menyimpannya di laporan. Jika berbeda, percayai skripnya dan catat selisihnya.

| Hal | Temuan |
|---|---|
| Total baris | **1.291** (35 kolom) |
| Baris per kliping | Maybank Group 534, CIMB 347, Maybank CSR 160, RHB 105, Hong Leong 96, Maybank Foundation 29, MDV 18, Public Bank 2 |
| `original_id` unik | **846** (445 baris duplikat) |
| Unik berdasarkan `title`+`body` | **741** |
| Unik berdasarkan `body` | **720** |
| Judul/isi kosong | 0 / 0 |
| Distribusi bahasa (setelah dedup `original_id`) | en 656, ms 146, zh 28, id 14, vi 1, es 1 |
| Panjang isi | median ≈ 2.700 karakter; min 5; maks 186.026; 9 artikel < 200 karakter; 14 artikel > 20.000 karakter |
| Kolom `entities` | **Kosong di semua baris** → tidak ada gold maupun weak label |
| Kolom `spokePerson1` | hanya 2 baris terisi → tidak berguna untuk supervisi |
| `id` `original_id` dengan isi berbeda | 0 (id sama ⇒ isi sama) |

### 3.4 Jebakan data yang harus ditangani

1. **Awalan kutip tunggal** pada nilai kolom (mis. `'en`, `'ms`) — hapus dengan `lstrip("'")` sebelum filter bahasa/ID.
2. **Format tanggal** `dd/mm/yyyy hh.mm.ss` (pemisah jam berupa titik) — parse dengan format eksplisit.
3. **Duplikasi lintas file**: artikel sama muncul di beberapa kliping, dan ada artikel dengan `original_id` berbeda tetapi isi identik/nyaris identik → harus ditangani agar tidak bocor antar split.
4. **Panjang ekstrem** → tentukan dan dokumentasikan batas maksimum panjang input API serta strategi pemotongan/chunking saat training.
5. **Bahasa**: Inggris + Melayu ≈ 95% data. Mandarin sedikit (28). Tamil **tidak ada** di sampel (berbeda dari yang disebut di rapat). Dokumentasikan keputusan bahasa yang didukung.
6. **Kolom `entities`**: kosong → dokumentasikan format/provenance (kosong, tidak span-labeled) dan jelaskan bahwa ia **tidak dipakai sebagai ground truth**.

---

## 4. Anotasi

- Buat anotasi **tingkat span** dengan **skema label terdokumentasi**.
- Label minimum: **orang (PERSON), organisasi (ORG), tempat (LOC/GPE)**. Tambahkan **DATE, EVENT**, atau lainnya bila sesuai.
- Format penyimpanan (pilih satu): **JSONL**, spaCy **DocBin**, **BIO/IOB2**, atau format machine-readable lain.
- Simpan **ID artikel asli (`original_id`)** dan **referensi baris sumber** (nama file + nomor baris) untuk tiap anotasi.
- Boleh memulai dari kolom `entities` (kosong di sini), kamus entitas, atau **saran model (model-assisted)**, tetapi **manusia harus meninjau** semua label yang dipakai pada set evaluasi akhir.
- Catat: **pedoman anotasi**, **ketidaksepakatan**, dan **koreksi**.

### 4.1 Rekomendasi skema label (silakan ubah, lalu dokumentasikan)

| Label | Cakupan | Catatan |
|---|---|---|
| `PERSON` | Nama orang | Termasuk gelar? Putuskan (mis. "Datuk Seri", "Tan Sri") dan tulis di pedoman |
| `ORG` | Perusahaan, bank, institusi, partai, LSM | Putuskan perlakuan singkatan (CIMB, RHB, DAP) |
| `GPE` | Negara, negara bagian, kota | Mis. Malaysia, Selangor, Kuala Lumpur |
| `LOC` | Lokasi non-politis | Gedung, sungai, kawasan |
| `DATE` | Ekspresi tanggal | Putuskan "early August 2025", "2% " (bukan DATE) |
| `EVENT` | Acara bernama | Mis. penghargaan, forum |

### 4.2 Hal yang perlu diputuskan di pedoman anotasi

- Batas span (apakah "Bank Negara Malaysia" satu ORG atau ORG + GPE?).
- Entitas bersarang/tumpang tindih (pilih satu aturan).
- Nama dengan tanda baca (mis. "Maybank Berhad.", "S&P", "Tan Sri Dr. Ng").
- Nama panggung/ejaan beda untuk entitas sama (mis. "Maybank" vs "Malayan Banking Berhad").
- Teks Melayu: awalan "Datuk", "Dato'", "Tan Sri", "Encik", dsb.

---

## 5. Pembagian Data (Data Split)

- Split **berdasarkan identitas artikel**, **bukan** per kalimat atau per baris — teks dari satu artikel tidak boleh muncul di lebih dari satu split.
- Gunakan **seed deterministik** yang terdokumentasi.
- Rasio default: **70% train / 15% validasi / 15% held-out test** (boleh berbeda jika ukuran data memaksa, jelaskan alasannya).
- **Duplikat dan near-duplicate** harus **berada di split yang sama** atau **dibuang dengan penjelasan** (rekomendasi: kelompokkan dahulu dengan kunci dedup, mis. hash isi ter-normalisasi + kemiripan, lalu split per grup).
- **Test set tidak boleh disentuh** sampai evaluasi akhir.

> Catatan praktis: dengan ±720–846 artikel unik, tidak perlu menganotasi semua. Anotasi **subset representatif** (mis. 60–150 artikel/potongan) lalu split per artikel. Putuskan ukuran subset berdasarkan waktu anotasi dan dokumentasikan. Set evaluasi minimal 10 artikel (Bagian 7) harus tetap tersedia dan idealnya berasal dari test split.

---

## 6. Pengembangan Model

Wajib:

1. Bangun **baseline** (model NER pra-latih terpilih **atau** baseline non-latih sederhana).
2. **Latih/fine-tune** model terpilih pada anotasi train, **atau adaptasi** pipeline NER-nya menggunakan train set.
3. Gunakan **data validasi** untuk memilih: preprocessing, pemetaan label, hyperparameter, dan kriteria stop.
4. Evaluasi model akhir **yang belum tersentuh** pada **test set**.
5. **Simpan model terlatih** atau sediakan **perintah training yang reproducible**.
6. **Sambungkan artefak akhir** ke endpoint layanan.

Catatan:
- Untuk dataset kecil, **transfer learning / few-shot adaptation diterima**; training dari nol tidak diwajibkan.
- **Rules-only tidak cukup** sebagai solusi akhir.
- Laporkan: jumlah dokumen dan span per split, setelan model, durasi training, seed acak, ketimpangan kelas.
- **Demo layanan harus memakai pipeline terlatih/teradaptasi yang sama** dengan yang dievaluasi di laporan.

### 6.1 Opsi model (pilih satu dan jelaskan alasannya di README)

| Opsi | Kelebihan | Kekurangan |
|---|---|---|
| **spaCy** `en_core_web_sm/md` → fine-tune dengan train DocBin | Ringan, cepat di CPU, deployment mudah, offset karakter alami | Inggris saja; Melayu lemah |
| **spaCy** `xx_ent_wiki_sm` (multibahasa) → fine-tune | Mencakup banyak bahasa | Skema label berbeda (PER/ORG/LOC/MISC), akurasi lebih rendah |
| **Hugging Face** `xlm-roberta-base` + token classification | Multibahasa kuat (Inggris, Melayu, Mandarin) | Butuh GPU/waktu lebih; perlu pemetaan subword → offset karakter |
| **Hugging Face** model NER pra-latih (mis. varian `bert-base-NER`) → fine-tune | Baseline kuat untuk Inggris | Inggris saja |

Rekomendasi pragmatis: **baseline** = model pra-latih tanpa fine-tune; **final** = model yang sama di-fine-tune dengan anotasi train (spaCy untuk kemudahan, atau XLM-R bila perangkat memadai dan ingin dukungan Melayu yang lebih baik).

---

## 7. Evaluasi

### 7.1 Set evaluasi berlabel (`data/evaluation_examples.json`)

Minimal **10 artikel pendek atau potongan artikel** dari file sampel, dengan campuran:

- [ ] Orang, organisasi, tempat, tanggal, dan tipe entitas lain yang didukung
- [ ] Entitas yang **muncul lebih dari sekali**
- [ ] **Nama ambigu** dan **nama dengan tanda baca**
- [ ] Artikel **tanpa entitas bernama**
- [ ] Minimal satu contoh yang **menantang** bagi model terpilih

### 7.2 Metrik

- Minimal: **precision, recall, F1** untuk deteksi entitas.
- Nyatakan jenis pencocokan: **exact-span**, partial-span, atau entity-type-and-span. (Pelaporan wajib memakai **exact-span**; tipe pencocokan lain boleh sebagai tambahan.)
- Laporkan **validasi dan test secara terpisah**.
- Sertakan: **metrik keseluruhan**, **metrik per label**, **perbandingan baseline vs terlatih**.

### 7.3 Analisis error

- Minimal **3 kesalahan** (false positive/false negative) dari **test set**, dengan penjelasan penyebab (tokenisasi, kapitalisasi, bahasa, ambigu, batas span, dsb.).
- Pernyataan eksplisit: **apakah contoh test memengaruhi anotasi atau tuning** (jawaban idealnya: tidak).

---

## 8. Pertanyaan yang Harus Dijawab di Laporan/README

1. Apa yang membuat sebuah span teks menjadi *named entity* dalam masalah ini?
2. Mengapa **judul dan isi digabung** sebelum dianalisis? Informasi apa yang bisa hilang jika diproses terpisah?
3. Apa **label yang didukung** model terpilih, dan bagaimana **pemetaannya** ke kategori yang ditampilkan ke pengguna?
4. Bagaimana **tokenisasi, tanda baca, kapitalisasi, atau bahasa** memengaruhi hasil?
5. Apa perbedaan antara **teks**, **label**, dan **offset karakter** sebuah entitas?
6. Apa yang terjadi ketika entitas yang sama muncul **berulang dengan ejaan/kapitalisasi berbeda**?
7. Error mana yang **paling penting bagi pengguna pemantau berita**, dan bagaimana sistem bisa diperbaiki?
8. Apa kekhawatiran **privasi, hak cipta, bias, atau penggunaan yang bertanggung jawab** saat memproses teks artikel?

---

## 9. Struktur Repository yang Diwajibkan

```
project/
├── README.md
├── requirements.txt            # atau package.json
├── src/
├── tests/
├── data/
│   └── evaluation_examples.json
└── screenshots/                # hanya jika diminta dosen
```

Struktur `src/` yang disarankan (bebas, asal terdokumentasi):

```
src/
├── config.py                # path data, seed, batas panjang input, nama model
├── data_loader.py           # muat CSV (sep=";"), bersihkan kutip, parse tanggal
├── profiling.py             # hitung baris, duplikat, judul/isi kosong, distribusi bahasa
├── dedup_split.py           # grup duplikat + split 70/15/15 per artikel dengan seed
├── annotation/              # skrip pra-anotasi + konversi ke JSONL/DocBin/BIO, pedoman anotasi
├── train.py                 # fine-tune/adaptasi + simpan artefak + log setelan/durasi
├── evaluate.py              # metrik exact-span, per label, baseline vs terlatih
├── ner_service.py           # muat model, gabung title+body, ekstrak entitas, offset
├── api.py                   # FastAPI/Flask: POST /extract-entities + validasi
└── static/ atau templates/  # panel HTML (form, loading, tabel entitas, error)
tests/
├── test_api.py              # valid, kosong, JSON rusak, terlalu panjang, bukan string
├── test_service.py          # offset benar, determinisme, non-ASCII, teks panjang
└── test_data.py             # loader, dedup, split tanpa kebocoran
```

Data asli diletakkan di luar repo atau di folder yang di-`.gitignore`. Tidak ada salinan artikel di Git.

---

## 10. Rencana Kerja Bertahap (Fase)

### Fase 1 — Setup dan profiling data
- [ ] Inisialisasi repo, virtualenv, `requirements.txt` (versi dipin), `.gitignore` (data & model besar & `.env`).
- [ ] `config.py` dengan `DATA_DIR`, `SEED`, `MAX_INPUT_CHARS`.
- [ ] Loader CSV (`sep=";"`, `dtype=str`, bersihkan awalan `'`, parse tanggal eksplisit).
- [ ] Skrip profiling → laporkan: **jumlah baris dimuat**, **duplikat**, **judul/isi kosong**, **distribusi bahasa**, panjang teks, status kolom `entities`.
- [ ] Dokumentasikan format & provenance kolom `entities` (kosong → bukan ground truth).

### Fase 2 — Definisi label, dedup, dan split
- [ ] Tentukan skema label dan **pedoman anotasi** (Bagian 4.1–4.2).
- [ ] Bangun grup duplikat/near-duplicate (hash isi ter-normalisasi + kemiripan, mis. MinHash/ukuran n-gram) dan putuskan: gabung di split sama atau buang (dengan alasan).
- [ ] Split **per artikel/grup** 70/15/15 dengan seed; simpan daftar ID per split (`splits.json`); **verifikasi tidak ada kebocoran** lewat tes.
- [ ] Pilih subset representatif untuk dianotasi (campuran sumber, bahasa, panjang, dan artikel tanpa entitas).

### Fase 3 — Anotasi
- [ ] Pra-anotasi dengan model baseline (ditandai sebagai *model-assisted*).
- [ ] **Pengguna** meninjau dan mengoreksi anotasi (tool: Label Studio, Doccano, Prodigy, atau edit JSONL manual).
- [ ] Simpan JSONL/DocBin/BIO dengan `original_id` + referensi baris sumber + sumber label (manual/model-assisted).
- [ ] Catat ketidaksepakatan dan koreksi di `docs/annotation_log.md`.
- [ ] Susun `data/evaluation_examples.json` (≥10 contoh, Bagian 7.1).

### Fase 4 — Baseline dan training
- [ ] Jalankan baseline pada validasi (belum fine-tune); simpan metrik.
- [ ] Fine-tune/adaptasi pada train; pilih hyperparameter dan preprocessing dengan **validasi saja**.
- [ ] Catat: seed, setelan, durasi training, jumlah dokumen/span per split, ketimpangan kelas.
- [ ] Simpan model (atau perintah training reproducible).

### Fase 5 — Evaluasi akhir
- [ ] Evaluasi **sekali** pada test set (exact-span P/R/F1 keseluruhan + per label).
- [ ] Tabel perbandingan **baseline vs terlatih** untuk validasi dan test.
- [ ] Analisis ≥3 error dari test set.
- [ ] Pernyataan: apakah test set memengaruhi anotasi/tuning.

### Fase 6 — Backend API
- [ ] Endpoint `POST /extract-entities` (JSON in/out).
- [ ] Gabungkan `title` + `body` dengan separator terdokumentasi; hitung offset pada teks gabungan.
- [ ] Validasi: tipe string, tidak boleh keduanya kosong, JSON malformed, batas panjang → **400** dengan pesan jelas.
- [ ] Respons berisi `entities` (`text`, `label`, `start`, `end`) dan `meta` (`entity_count`, `model`, versi).
- [ ] Pastikan determinisme (mode inferensi tetap, tanpa sampling acak).
- [ ] Muat **artefak terlatih** yang sama dengan yang dievaluasi.

### Fase 7 — Panel web
- [ ] Form judul + isi dengan validasi sisi klien.
- [ ] Tombol submit + status loading yang terlihat.
- [ ] Tabel entitas (teks + tipe, opsional offset).
- [ ] Menangani respons error (tampilkan pesan, **tidak crash**).
- [ ] (Ekstensi) sorot span langsung di teks artikel.

### Fase 8 — Tes otomatis (minimal 5, disarankan ≥10)
- [ ] Input normal → entitas dikembalikan, format benar.
- [ ] Input kosong (judul + isi) → 400.
- [ ] JSON malformed → 400.
- [ ] Tipe bukan string → 400.
- [ ] Input melebihi batas → 400.
- [ ] Tanda baca, entitas berulang, angka/tanggal.
- [ ] Teks **non-ASCII** (mis. Mandarin/Melayu) → offset valid.
- [ ] Teks panjang → tidak crash/timeout.
- [ ] Determinisme: dua request sama → hasil identik.
- [ ] Offset: `text == analyzed_text[start:end]` untuk semua entitas.

### Fase 9 — Dokumentasi dan penyelesaian
- [ ] `README.md` (Bagian 12).
- [ ] Jawab 8 pertanyaan (Bagian 8).
- [ ] Verifikasi "Definition of Done" (Bagian 13) dari lingkungan bersih.
- [ ] Siapkan presentasi.

---

## 11. Checklist Akhir (Semua Wajib Tercentang)

**Layanan**
- [ ] Panel judul + isi, submit, loading, tabel entitas
- [ ] Validasi di panel dan backend
- [ ] Endpoint tunggal, JSON, status HTTP benar
- [ ] Panel tidak crash saat error
- [ ] Tidak ada hard-coded entities
- [ ] Berjalan lokal dengan perintah terdokumentasi
- [ ] Dependensi + versi model tercatat; secret via env var

**Data & anotasi**
- [ ] Semua CSV dimuat dengan benar (pemisah `;`, kutip dipertahankan)
- [ ] Dilaporkan: baris dimuat, duplikat, judul/isi kosong, distribusi bahasa
- [ ] Provenance kolom `entities` didokumentasikan; tidak dipakai sebagai ground truth tanpa validasi
- [ ] Anotasi span dengan skema label terdokumentasi (min. orang, organisasi, tempat)
- [ ] ID artikel + referensi baris sumber tersimpan
- [ ] Label evaluasi akhir ditinjau manusia; pedoman, ketidaksepakatan, koreksi tercatat
- [ ] Tidak ada salinan kedua artikel asli di repo

**Split & training**
- [ ] Split per artikel, seed terdokumentasi, 70/15/15 (atau alasan lain)
- [ ] Duplikat/near-duplicate di split sama atau dibuang dengan penjelasan
- [ ] Test set tidak disentuh sampai evaluasi akhir
- [ ] Baseline + model terlatih/teradaptasi (bukan rules-only)
- [ ] Validasi dipakai untuk memilih preprocessing/label/hyperparameter/stop
- [ ] Model tersimpan atau perintah training reproducible
- [ ] Dilaporkan: dokumen & span per split, setelan, durasi, seed, ketimpangan kelas
- [ ] Demo memakai pipeline yang sama dengan yang dievaluasi

**Evaluasi**
- [ ] ≥10 artikel/potongan berlabel dengan campuran kondisi (Bagian 7.1)
- [ ] Exact-span P/R/F1 keseluruhan + per label, validasi dan test terpisah
- [ ] Baseline vs terlatih
- [ ] ≥3 error test set dianalisis
- [ ] Pernyataan pengaruh test terhadap anotasi/tuning

**Pengumpulan**
- [ ] Struktur `project/` sesuai Bagian 9
- [ ] ≥5 tes otomatis lulus
- [ ] README lengkap (Bagian 12)
- [ ] 8 pertanyaan terjawab
- [ ] Repo publik atau `.zip` (kode, model, dokumentasi)
- [ ] Presentasi siap (temuan, implementasi, evaluasi)

---

## 12. Isi README yang Diwajibkan

- Deskripsi singkat proyek dan **arsitektur** (diagram atau deskripsi singkat).
- **Setup**: versi Python, perintah instalasi, cara mengunduh/menaruh model, cara mengonfigurasi `DATA_DIR`.
- **Menjalankan**: perintah start server, URL panel, perintah training, perintah evaluasi, perintah tes.
- **Penggunaan API**: **satu contoh request dan respons** (`curl` atau HTTP), kode error, batas panjang input.
- **Pilihan model** dan alasannya, label yang didukung, dan pemetaan ke kategori tampilan.
- Ringkasan data (profiling), skema label, split, hasil evaluasi (validasi dan test), baseline vs terlatih.
- **Keterbatasan yang diketahui** dan diskusi etika/penggunaan bertanggung jawab (privasi, hak cipta, bias).
- Dependensi dan versi (Python, library, model).

Screenshot hanya jika dosen memintanya.

---

## 13. Definition of Done

Tugas dianggap selesai jika **orang lain** dapat mengikuti README untuk:

1. Menjalankan aplikasi **tanpa mengedit kode secara manual**,
2. Memasukkan judul + isi artikel di panel, men-submit, dan **melihat entitas yang teridentifikasi**,
3. **Mereproduksi** hasil evaluasi dan **menjalankan tes**.

---

## 14. Tantangan Ekstensi (Nilai Tambah, Opsional)

- Sorot span entitas langsung di teks artikel.
- Dukungan multi-bahasa dan bandingkan performa antar bahasa (en / ms / zh).
- Normalisasi entitas ekuivalen dengan tetap menyimpan teks asli.
- Skor kepercayaan (confidence) beserta penjelasan artinya.
- Containerize layanan (Docker).
- Bandingkan dua model NER pada set evaluasi yang sama.
- Endpoint batch untuk banyak artikel.

> Prioritas: selesaikan seluruh persyaratan wajib dahulu. Ekstensi yang paling murah dan relevan dengan data ini: **perbandingan en vs ms** dan **penyorotan span**.

---

## 15. Keputusan yang Perlu Dikonfirmasi ke Dosen (dari ringkasan rapat yang ambigu)

- [ ] Jumlah file/sampel yang dipakai (ringkasan menyebut "8–19 file"; yang tersedia 8 CSV).
- [ ] Pembagian kelompok (jumlah kelompok vs jumlah anggota per kelompok).
- [ ] Apakah **ringkasan otomatis** (abstraktif/ekstraktif) masih diwajibkan; `study_case.pdf` hanya mensyaratkan **NER**, tanpa ringkasan.
- [ ] Daftar label entitas pasti yang diharapkan.
- [ ] Bahasa yang wajib didukung (Tamil tidak ada di sampel; Indonesia dan Melayu ada).
- [ ] Platform komunikasi lanjutan (disebut "Novo", belum jelas).
- [ ] Persetujuan stack selain Flask/FastAPI (jika ingin memakai yang lain).
- [ ] Jadwal presentasi: dua minggu atau tiga minggu.

---

## 16. Contoh Prompt Awal untuk AI Agent

> "Baca `uts_data_science_project.md`. Kerjakan **Fase 1**: buat struktur repo, `config.py`, `data_loader.py`, dan `profiling.py`. Muat 8 CSV dari `DATA_DIR` (`sep=';'`, bersihkan awalan kutip tunggal), lalu cetak: jumlah baris, duplikat (berdasar `original_id` dan `title+body`), judul/isi kosong, distribusi bahasa, statistik panjang teks, dan status kolom `entities`. Bandingkan hasilnya dengan tabel di Bagian 3.3. Tulis tes untuk loader. Jangan commit data asli. Berhenti setelah Fase 1 dan laporkan hasilnya."
