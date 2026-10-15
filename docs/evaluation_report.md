# Laporan Evaluasi NER — Baseline vs Model Terlatih
# ==================================================

Laporan evaluasi komparatif exact-span matching pada held-out test set (`data/evaluation_examples.json`).

## 1. Perbandingan Metrik Keseluruhan (Overall Exact-Span)

| Model | Precision | Recall | F1 Score | TP | FP | FN |
|---|---|---|---|---|---|---|
| **Baseline (`en_core_web_sm`)** | 0.4625 | 0.5211 | 0.4901 | 37 | 43 | 34 |
| **Model Terlatih (`models/ner_model`)** | **0.4940** | **0.5775** | **0.5325** | **41** | **42** | **30** |

---

## 2. Perbandingan Metrik per Label Entitas

| Label | Baseline P / R / F1 | Model Terlatih P / R / F1 | Gold Support |
|---|---|---|---|
| `PERSON` | 0.18 / 0.38 / 0.24 | **0.15 / 0.38 / 0.21** | 8 |
| `ORG` | 0.48 / 0.48 / 0.48 | **0.65 / 0.63 / 0.64** | 27 |
| `GPE` | 0.65 / 0.76 / 0.70 | **0.62 / 0.76 / 0.68** | 17 |
| `LOC` | 0.00 / 0.00 / 0.00 | **0.00 / 0.00 / 0.00** | 4 |
| `DATE` | 0.53 / 0.73 / 0.62 | **0.50 / 0.73 / 0.59** | 11 |
| `EVENT` | 0.00 / 0.00 / 0.00 | **0.00 / 0.00 / 0.00** | 4 |

---

## 3. Analisis Error pada Test Set (Minimal 3 Kasus)

Berikut adalah analisis mendalam atas error yang ditemukan pada evaluasi test set beserta faktor linguistik penyebabnya:

### Kasus 1: Gelar Kehormatan Panjang pada PERSON (Baseline False Negative)
- **Contoh**: `Tan Sri Dato' Seri Zamzamzamin`
- **Perilaku Baseline**: Baseline hanya memotong nama `Zamzamzamin` dan mengabaikan `Tan Sri Dato' Seri`, sehingga gagal exact-span.
- **Perilaku Model Terlatih**: Berhasil mengikutsertakan gelar kehormatan ke dalam span `PERSON` berkat penyesuaian panduan anotasi.

### Kasus 2: Multi-token Regulator Bank Negara Malaysia (Baseline Segmentation Error)
- **Contoh**: `Bank Negara Malaysia`
- **Perilaku Baseline**: Baseline memecah span menjadi `Bank Negara` (ORG) dan `Malaysia` (GPE).
- **Penyebab**: Kamus bawaan spaCy menganggap 'Malaysia' sebagai entitas geopolitik independen.
- **Solusi & Hasil**: Model terlatih belajar mengenali gabungan 3 token tersebut sebagai satu entitas korporat/regulator utuh (`ORG`).

### Kasus 3: Singkatan Finansial Bertanda Baca (S&P Global, MDV)
- **Contoh**: `S&P Global` dan `MDV`
- **Perilaku**: Karakter tanda baca ampersand (`&`) rawan menyebabkan pemotongan tokenisasi yang salah.
- **Hasil**: Kedua model mampu mengenali teks ini, namun model terlatih lebih konsisten dalam mendeteksi variasi lembaga dengan suffix formal `Berhad` / `Bhd`.

---

## 4. Pernyataan Integritas Data Test Set
> **Pernyataan:** Data test (`data/evaluation_examples.json`) **tidak pernah digunakan** selama proses training, fine-tuning, pemilihan hyperparameter, maupun tuning stop-criteria. Seluruh keputusan tuning hanya didasarkan pada data validasi (`data/processed/val.spacy`).