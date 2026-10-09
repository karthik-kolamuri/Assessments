# Voice Arena Leaderboard: Executive One-Pager
## Product Overview & Evaluation Framework for Speaker Diarization
**Target Reviewer:** Executive Team & Engineering Leadership | **Read Time:** 2 Minutes

---

### The Problem & Market Need
Speaker diarization ("who spoke when") is essential for meeting intelligence, contact centers, and clinical scribes. Yet published vendor accuracy numbers are systematically misleading: they rely on sterile academic datasets, forgive boundary errors with generous 250ms collars, and ignore cross-talk overlap. Product teams select systems based on marketing claims only to encounter severe conversational turn scrambling in production.

**Voice Arena’s Mission:** Provide the definitive, unbiased, production-grounded benchmark for speech diarization systems.

---

### Core Leaderboard Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       VOICE ARENA EVALUATION ENGINE                         │
├──────────────────────┬───────────────────────────────┬──────────────────────┤
│    TEST DATASET      │      EVALUATED SYSTEMS        │   SCORING & RIGOR    │
│  120 Hours Curated   │      10 Flagship Models       │ Dual-Collar Scoring  │
│  • Meetings (40h)    │ • Open-Source: pyannote 3.1,  │ • Primary: 0ms       │
│  • Telephony (30h)   │   NeMo MSDD, WhisperX,        │ • Legacy: 250ms      │
│  • Clinical (20h)    │   SpeechBrain                 │ Overlap: Mandatory   │
│  • Social/Casual(15h)│ • Commercial Cloud APIs:      │ Speakers: Unknown    │
│  • Noisy Fields (15h)│   Deepgram, AssemblyAI, AWS,  │ Bootstrap 95% CIs    │
│  Triple-pass audit   │   Google Chirp, Azure, Rev AI │ Wilcoxon (p < 0.01)  │
└──────────────────────┴───────────────────────────────┴──────────────────────┘
```

---

### The 4 Crucial Design Choices

| Design Choice | Rationale & Trade-off |
| :--- | :--- |
| **1. Strict 0ms Boundary Collar** | Traditional 250ms collars erase half a second of error per speaker turn, hiding speech collisions. 0ms reflects true production turn-taking. |
| **2. Mandatory Overlap Evaluation** | 12% of real conversation is cross-talk, driving 60%+ of downstream errors. We score overlap without forgiveness and report dedicated Overlap-DER. |
| **3. JER Alongside DER** | Diarization Error Rate is time-weighted and hides failures on quiet participants. Jaccard Error Rate treats all speakers equally, preventing conversational bias. |
| **4. Paired Statistical Significance** | Benchmark scores often differ by fractions of a percent. We enforce 1,000 bootstrap resamples and Wilcoxon significance flags before declaring a winner. |

---

### Leaderboard Output: What Decision-Makers See
Next to each ranked model, the leaderboard publishes:
1. **DER (0ms & 250ms)** with $\pm 95\%$ confidence bounds.
2. **Overlap Diarization Error Rate (OV-DER)** to gauge multi-speaker robustness.
3. **Operational Metrics:** Real-Time Factor (RTF), Streaming Latency, and Cost per 1,000 audio hours.
4. **Domain Breakdown Radar:** Instant filtering by Enterprise Meetings, Telephony, or Medical.

### Key Takeaway for Voice AI Teams
> **A model with an 8% DER on clean benchmark audio can collapse to 35% DER in real multi-speaker meetings.** Voice Arena eliminates blind vendor selection by pairing realistic acoustic stress-tests with statistical confidence intervals and cost-latency profiling.
