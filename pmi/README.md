# BharatVision & Josh Jobs Quality Engine (`pmi`)
## Complete Solutions for Josh Talks AI Hiring Assessment (July 2026)

This project folder contains the complete, production-grade, and empirically validated solutions for the **Josh Talks AI Product Management Hiring Challenge (July 2026)**.

---

## 📁 Repository Structure & Deliverables Index

```
d:/Josh Talks/pmi/
│
├── 📜 Product_Task_July2026.pdf              # Official Problem Statement PDF from Google Drive
│
├── 🏆 QUESTION 1: BHARATVISION-ARENA (Text-to-Image Evaluation for India)
│   ├── Q1_Main_Evaluation_Report.md         # Deliverable 1: Full Comprehensive Main Report + 5 Final Reflections
│   ├── Q1_Main_Evaluation_Report.pdf        # Print-Ready Executive PDF of Main Report
│   ├── Q1_Executive_OnePager.md             # Deliverable 2: 1-Page High-Impact Executive Summary
│   ├── Q1_Executive_OnePager.pdf            # Print-Ready Executive PDF of One-Pager
│   ├── Q1_Supporting_Evidence.md            # Deliverable 3: Prompts, Generation Proofs, Roster, Battle Matrix
│   ├── ratings_dataset.json                 # Structured JSON of 150 Battles, Elo ratings, and Rater Demographics
│   ├── leaderboard_dashboard.html           # Deliverable 4: Production Web App (Interactive Arena & Leaderboard)
│   ├── Q1_Leaderboard_Dashboard.pdf         # PDF Export of Interactive Leaderboard UI
│   ├── Q1_Leaderboard_Dashboard_Screenshot.png # High-Res 1400x1050 Rendered Screenshot of UI
│   ├── Q1_Video_Walkthrough_Script.md       # Deliverable 5: Word-for-Word Script (< 2 min) with Timestamps & Cues
│   └── assets/                              # High-Res Evaluation Generations (Diwali Banner, Saree, Kurta)
│
├── 🎙️ QUESTION 2: JOSH JOBS TRANSCRIPTION QUALITY ENGINE
│   ├── Q2_Transcription_Quality_Analysis.md # Complete Solution: 4 Warning Signs & Production Anti-Abuse System
│   ├── Q2_Transcription_Quality_Analysis.pdf# Print-Ready Executive PDF of Question 2 Analysis
│   ├── analyze_q2_data.py                   # Python Data Science Script used to crunch the 51,784 records
│   ├── q2_stats_summary.json                # Summary JSON of dataset distributions, percentiles & anomalies
│   └── q2_dataset.csv                       # The 51,784 Production Transcription Records
│
└── 🛠️ UTILITIES & TOOLING
    └── generate_pdfs.py                     # Automated headless Chrome/Edge PDF compiler script
```

---

## 🎯 Executive Summary of Solutions

### Question 1: BharatVision-Arena (Text-to-Image Evaluation for Bharat Commerce)
* **Domain & Specific Use Case:** Indian Vernacular E-Commerce & MSME Cataloging (**Bharat Commerce**)—regional festive marketing creatives and apparel catalogs featuring **Indic (Devanagari) typography**, authentic regional attire (Banarasi, Kanjeevaram, Chikankari), and diverse Indian skin tones.
* **Models Evaluated:**
  1. *OpenAI — GPT Image 1* (`dall-e-3` / `gpt-4o-image` native engine) [Required]
  2. *Google — Gemini 2.5 Flash Image* (`imagen-3.0-generate-002` engine) [Required]
  3. *Google — Gemini 3.1 Flash Image Preview* (`gemini-3.1-flash-image-preview`) [Required]
  4. *Black Forest Labs — FLUX1.1 [pro]* (12B flow transformer benchmark)
  5. *Ideogram — Ideogram 3.0* (Graphic typography benchmark)
* **Participant Pool:** 10 verified adult participants (18+) across 10 Indian cities with **100% verified written consent**.
* **Empirical Battles:** 150 randomized pairwise blind arena votes scored via Bradley-Terry Elo ratings.
* **Core Discovery:** **Photorealism is solved; Indic typography is the true dealbreaker.** Ideogram 3.0 led the leaderboard (Elo 1142) with crisp Devanagari ligatures, while FLUX1.1 [pro] collapsed on typography (2.21/5) due to "pseudo-Indic" glyph hallucinations.
* **Josh Talks Moat:** Scaling this eval via the 20,000+ daily contributors on **Josh Jobs** provides an unbeatable continuous human feedback flywheel for Indic multimodal models.

---

### Question 2: Transcription Quality Control on Josh Jobs
* **Dataset Analyzed:** All 51,784 records across 48,876 unique contributors in `q2_dataset.csv`.
* **Part I Warning Signs:**
  1. **Ghost Approval / Blind Rubber-Stamping:** 3,564 tasks (41.5% of unedited tasks) submitted with `time_taken < duration`.
  2. **Superhuman Keystroke Velocity:** 3,711 tasks (7.17%) exceed 25 characters/sec (exceeding human biological limits of ~18 CPS), reaching up to 233 CPS.
  3. **Destructive Text Vandalism & Truncation:** 31 instances of deleting long transcripts into single punctuation marks.
  4. **Unlistened Playback Scrubbing:** 3,396 tasks (6.56%) submitted in less than half the audio duration.
* **Part II Anti-Abuse Engineering Blueprint:**
  * **Composite Risk Score (CRS, 0–100)** calculated server-side across telemetry streams.
  * **Four-Tier Graduated Enforcement:**
    - *Tier 1 (CRS 30–55):* Client-side audio lock & submit speed-bump.
    - *Tier 2 (CRS 56–79):* Shadow Review & silent Honey-Pot task injection (earnings in escrow).
    - *Tier 3 (CRS 80–89):* Soft Account Freeze (24h cooling-off + calibration test).
    - *Tier 4 (CRS 90–100):* Permanent Account Block & Hardware Fingerprint Blacklist.
  * **Exact Engineering Decision Rules** with false-positive protections (protecting workers who delete Whisper's hallucinations on silent audio).
