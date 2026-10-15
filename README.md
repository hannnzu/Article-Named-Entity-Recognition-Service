# Article Named-Entity Recognition (NER) Service

> Proyek UTS Data Science — Prototipe layanan ekstraksi Named Entity dari artikel berita.

---

## Deskripsi Singkat

Layanan web kecil yang menerima **judul** dan **isi** artikel, lalu mengidentifikasi *named entity* (orang, organisasi, tempat, tanggal, dsb.) menggunakan pipeline NLP.

**Arsitektur:**
```
Browser (HTML form)
    │  POST JSON {title, body}
    ▼
FastAPI backend  →  NER Pipeline (spaCy)
    │
    ▼
JSON response {entities[], meta{}}
```

---

## Setup

### Prasyarat
- Python 3.10+
- pip / virtualenv

### Instalasi

```bash
# 1. Clone repo
git clone <repo-url>
cd Article-Named-Entity-Recognition-Service

# 2. Buat virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 3. Install dependensi
pip install -r requirements.txt

# 4. Download model spaCy (pilih sesuai MODEL_NAME di .env)
python -m spacy download en_core_web_sm
# atau untuk multibahasa:
# python -m spacy download xx_ent_wiki_sm

# 5. Konfigurasi (salin .env.example ke .env dan sesuaikan)
cp .env.example .env
# Edit DATA_DIR di .env agar menunjuk ke direktori CSV dari dosen
```

### Konfigurasi DATA_DIR

Data artikel asli (8 file CSV) tidak di-commit ke repo. Atur path-nya lewat env var:

```bash
# .env
DATA_DIR=D:\path\ke\folder\csv
```

---

## Menjalankan Layanan

```bash
# Aktifkan venv terlebih dahulu
venv\Scripts\activate   # Windows

# Start server
uvicorn src.api:app --reload --port 8000
```

Buka panel: **http://localhost:8000**

---

## Profiling & Training

```bash
# Profiling data (Fase 1)
python -m src.profiling

# Dedup dan split data (Fase 2) — belum tersedia
# python -m src.dedup_split

# Training (Fase 4) — belum tersedia
# python -m src.train

# Evaluasi (Fase 5) — belum tersedia
# python -m src.evaluate
```

---

## Penggunaan API

### Endpoint

`POST /extract-entities`

### Contoh Request

```bash
curl -X POST http://localhost:8000/extract-entities \
  -H "Content-Type: application/json" \
  -d '{"title": "Maybank Reports Record Profit", "body": "Kuala Lumpur — Maybank announced a record profit for Q3 2026."}'
```

### Contoh Response

```json
{
  "entities": [
    {"text": "Maybank", "label": "ORG", "start": 0, "end": 7},
    {"text": "Kuala Lumpur", "label": "GPE", "start": 37, "end": 49},
    {"text": "Q3 2026", "label": "DATE", "start": 84, "end": 91}
  ],
  "meta": {
    "entity_count": 3,
    "model": "en_core_web_sm",
    "analyzed_length": 95,
    "title_body_separator": "\n\n"
  }
}
```

### Kode Error

| Status | Kondisi |
|---|---|
| 400 | title & body keduanya kosong |
| 400 | JSON malformed |
| 400 | title atau body bukan string |
| 400 | Input melebihi `MAX_INPUT_CHARS` (default: 200.000 karakter) |
| 500 | Error internal server |

### Format Teks yang Dianalisis

```
analyzed_text = title + "\n\n" + body
```

Offset `start`/`end` dihitung pada `analyzed_text` ini (zero-based, eksklusif di `end`).

---

## Pilihan Model & Alasan

| Model | Dipilih | Alasan |
|---|---|---|
| `en_core_web_sm` (spaCy) | ✅ Baseline | Ringan, cepat di CPU, offset karakter alami, mudah di-deploy |
| `xx_ent_wiki_sm` (spaCy) | Opsional | Multibahasa (en+ms), akurasi lebih rendah |
| `xlm-roberta-base` (HuggingFace) | Opsional | Multibahasa kuat, butuh GPU |

**Label yang didukung:** `PERSON`, `ORG`, `GPE`, `LOC`, `DATE`, `EVENT`

> Catatan: spaCy `en_core_web_sm` menggunakan label standar OntoNotes. Label seperti `NORP`, `FAC`, `PRODUCT` dipetakan atau dikecualikan — lihat `src/ner_service.py`.

---

## Ringkasan Data

> *Akan diisi setelah profiling (Fase 1 selesai)*

- **Total baris:** 1.291 (8 file CSV)
- **Unik (original_id):** 846
- **Bahasa utama:** Inggris (en), Melayu (ms)
- **Panjang body:** median ~2.700 karakter

---

## Hasil Evaluasi

> *Akan diisi setelah Fase 4–5*

---

## Menjalankan Tes

```bash
pytest tests/ -v
```

---

## Keterbatasan

- Model `en_core_web_sm` lemah pada teks Melayu dan Mandarin.
- Artikel > 200.000 karakter ditolak (dikonfigurasi via `MAX_INPUT_CHARS`).
- Kolom `entities` pada data asli kosong — tidak ada ground truth dari sumber.
- Gelar kehormatan Malaysia (Datuk, Tan Sri, Dato') mungkin tidak dikenali dengan baik.

---

## Etika & Penggunaan Bertanggung Jawab

- Data artikel adalah milik sumber media; tidak disebarluaskan.
- Model NER dapat mengandung bias terhadap bahasa/budaya Barat.
- Nama orang yang diekstraksi harus diperlakukan dengan hati-hati (privasi).
- Tujuan layanan: prototipe riset/edukasi, bukan produksi.

---

## Dependensi & Versi

Lihat [requirements.txt](requirements.txt).

| Komponen | Versi |
|---|---|
| Python | ≥ 3.10 |
| FastAPI | 0.115.12 |
| spaCy | 3.8.7 |
| pandas | 2.2.3 |

---

## Asumsi yang Didokumentasikan

1. Data CSV menggunakan encoding UTF-8.
2. Format tanggal adalah `dd/mm/yyyy hh.mm.ss` (pemisah jam = titik).
3. Bahasa yang didukung utama: Inggris (`en`) dan Melayu (`ms`).
4. Tamil tidak ada di dataset (berbeda dari yang disebut di rapat — lihat Bagian 15 brief).
5. Format penggabungan: `title + "\n\n" + body`.
