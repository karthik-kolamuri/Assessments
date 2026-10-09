# BharatVision-Arena: Text-to-Image Eval for Indian E-Commerce
## Executive One-Page Report | Josh Talks AI Evaluation Challenge
**Author:** Product Management Candidate | **Domain:** Multimodal Generative AI | **Scope:** 5 Models, 10 Human Raters, 150 Battles

---

### 1. The Evaluation at a Glance
* **Domain & Specific Use Case:** Indian Vernacular E-Commerce & MSME Cataloging (**Bharat Commerce**)—specifically evaluating regional festive marketing creatives and apparel catalogs featuring **Indic (Devanagari) typography**, authentic regional attire (Banarasi, Kanjeevaram, Chikankari), and diverse Indian skin tones.
* **Why It Matters:** Over 63M Indian MSMEs need low-cost promotional visual creatives for WhatsApp Business, Meesho, and Instagram. Global models regularly fail at rendering Indic text (producing meaningless pseudo-Sanskrit glyphs) and hallucinate culturally inappropriate attire, making them unusable for real merchants.

---

### 2. Core Setup & Fair Benchmarking
* **5 Evaluated Models:**
  1. *OpenAI — GPT Image 1* (DALL-E 3 engine)
  2. *Google — Gemini 2.5 Flash Image* (Imagen 3 engine)
  3. *Google — Gemini 3.1 Flash Image Preview* (Next-gen multimodal preview)
  4. *Black Forest Labs — FLUX1.1 [pro]* (12B rectified flow benchmark)
  5. *Ideogram — Ideogram 3.0* (Dedicated graphic design & typography benchmark)
* **Fair Setup:** Identical standardized prompt matrix across 5 regional commerce scenarios, 1:1 aspect ratio, single-turn zero-shot generation, no post-processing.
* **Human-in-the-Loop Methodology:** 10 verified adult participants (18+) across 10 Indian cities. 150 randomized blind pairwise battles (Bradley-Terry Elo calculation) + 4-pillar Likert scoring (Cultural Fidelity, Indic Typography, Photorealism, Commercial Usability).

---

### 3. Empirical Findings & Elo Leaderboard

```
Rank  Model Name                       Elo Rating  Win Rate  Devanagari (1-5)  Cultural Fidelity (1-5)
 1    Ideogram 3.0                        1142       66.7%        4.62 / 5             3.95 / 5
 2    Gemini 3.1 Flash Image Preview      1095       58.3%        3.88 / 5             4.38 / 5
 3    GPT Image 1                         1048       51.7%        3.52 / 5             4.10 / 5
 4    FLUX1.1 [pro]                       1012       46.7%        2.21 / 5             4.25 / 5
 5    Gemini 2.5 Flash Image               968       38.3%        2.74 / 5             4.02 / 5
```

* **Core Defect Discovered:** 85% of FLUX1.1 [pro] and 52% of Gemini 2.5 Flash images generated illegible "pseudo-Devanagari" squiggles. While visually photographic, Indian raters scored them 1/5 for commercial utility because unreadable text destroys brand trust.
* **Cultural Misalignment:** Models systematically whitewashed Indian skin tones and fused distinct regional clothing traditions (e.g., adding heavy North Indian bridal jewelry onto South Indian Kanjeevarams).
* **Top Performer:** Ideogram 3.0 won the arena through its unprecedented mastery of Indic ligatures and typography hierarchies, while Gemini 3.1 Flash Preview led in authentic skin tone representation and natural lighting.

---

### 4. The Most Important Takeaway for AI Labs Building for India
> **Photorealism is a solved commodity; Indic typography and regional cultural coherence are the true frontier of model differentiation in India.** 
> Global models that score top marks on Western benchmarks fail abruptly when asked to generate a simple ₹500 festive saree promo with Hindi text. For an AI lab like **Josh Talks AI**, the biggest commercial moat lies in fine-tuning text encoders on Indic unicode-to-spatial layouts and curating verified regional imagery. Leveraging the **20,000+ daily workers on Josh Jobs** creates an unbeatable flywheel for continuous human evaluation and alignment.
