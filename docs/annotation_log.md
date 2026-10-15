# Annotation Log — Article NER Service
# =====================================
# Catat di sini setiap ketidaksepakatan, koreksi, dan keputusan
# yang dibuat selama proses anotasi.
# Format: tanggal | anotator | kasus | keputusan

## Log Entri Keputusan & Koreksi

### [2026-10-15] Penanganan Gelar Kehormatan Malaysia pada PERSON
- **Konteks**: Berita Malaysia kerap menyebut tokoh penting perbankan dengan gelar formal majemuk seperti *Tan Sri Dato' Seri*, *Datuk Seri*, *Encik*, dsb.
- **Masalah**: Model baseline `en_core_web_sm` sering memisahkan atau mengabaikan gelar dan hanya mengenali nama inti sebagai `PERSON` (misalnya hanya mengenali `Zamzamzamin` alih-alih `Tan Sri Dato' Seri Zamzamzamin`).
- **Keputusan**: Sesuai Bagian 2.2 Panduan Anotasi, seluruh gelar kehormatan Malaysia digabungkan ke dalam span `PERSON` jika mendahului nama secara langsung.
- **Anotator**: Human Reviewer & Pre-annotator script (`src/annotation/pre_annotate.py`).

### [2026-10-15] Penanganan Suffix Badan Hukum "Berhad" / "Bhd"
- **Konteks**: Berita korporat menggunakan bentuk lengkap seperti *CIMB Group Berhad*, *Maybank Islamic Berhad*, *Hong Leong Bank Berhad*.
- **Masalah**: Model baseline sering berhenti sebelum kata "Berhad" (hanya melabeli "CIMB Group" atau "Hong Leong Bank").
- **Keputusan**: Kata "Berhad", "Bhd", dan "Group" yang melekat pada nama lembaga keuangan/korporasi disertakan sebagai satu span `ORG` tunggal.
- **Anotator**: Human Reviewer.

### [2026-10-15] Span Utuh "Bank Negara Malaysia"
- **Konteks**: Bank sentral Malaysia disebut dengan nama resmi Melayu dalam teks berbahasa Inggris maupun Melayu.
- **Masalah**: Model standar cenderung memecah menjadi `ORG` ("Bank Negara") dan `GPE` ("Malaysia").
- **Keputusan**: Ditetapkan sebagai satu span entitas `ORG` tunggal ("Bank Negara Malaysia") karena merujuk pada satu institusi regulator moneter, bukan pemisahan wilayah.
- **Anotator**: Human Reviewer.

### [2026-10-15] Simbol Tanda Baca Khusus dalam Nama Lembaga ("S&P Global")
- **Konteks**: Lembaga pemeringkat kredit *S&P Global* muncul dalam artikel keuangan.
- **Masalah**: Karakter ampersand (`&`) sering memicu fragmentasi token.
- **Keputusan**: Tetap dipertahankan sebagai satu kesatuan `ORG` utuh (`S&P Global`).
- **Anotator**: Human Reviewer.

### [2026-10-15] Penyusunan Contoh Negatif (Tanpa Entitas Bernama)
- **Konteks**: Evaluasi NER yang sehat memerlukan artikel atau teks tanpa entitas bernama untuk mengukur False Positive Rate.
- **Masalah**: Dataset berita perbankan hampir selalu memuat nama bank atau lokasi.
- **Keputusan**: Disusun dua contoh potongan edukasi/ketentuan umum (satu dalam Bahasa Melayu dan satu dalam Bahasa Inggris) yang sama sekali tidak memuat *named entity*.
- **Anotator**: Human Reviewer (dimasukkan dalam `data/evaluation_examples.json`).

---

## Ringkasan Statistik Anotasi

| Hal                    | Nilai |
|------------------------|-------|
| Total dokumen train    | 70 dokumen |
| Total span train       | 3.244 span |
| Total dokumen val      | 20 dokumen |
| Total span val         | 584 span |
| Total dokumen eval/test| 12 dokumen |
| Total span eval/test   | 71 span (100% human-reviewed) |
| Model-assisted         | 90 dokumen (Train + Val) |
| Human-curated Ground Truth | 12 dokumen (data/evaluation_examples.json) |
| Format penyimpanan     | JSONL (`data/annotations/`), JSON (`data/evaluation_examples.json`), DocBin (`data/processed/*.spacy`) |
