# Voice Arena: Question 1 Video Walkthrough Script
## 2-Minute Compulsory Presentation Script (Word-for-Word)
**Target Duration:** 1 minute 55 seconds (under 2:00 limit) | **Tone:** Confident, analytical, structured PM presentation

---

### Video Walkthrough Guidelines
* **Recording Platform:** Loom, Zoom (record to computer), or unlisted YouTube video.
* **Format:** Screen share of your Leaderboard Mockup / Slides with your webcam visible in the corner.
* **Total Word Count:** ~275 words (ideal pace: 140 words per minute).

---

### The Script (Timed)

#### [0:00 - 0:25] The Problem & The Mission
> "Hi everyone, I'm [Your Name], presenting my evaluation design for Voice Arena’s Speaker Diarization Leaderboard. 
> 
> Speaker diarization—answering *who spoke when*—is critical for meeting summarizers, call center analytics, and clinical scribes. But right now, teams pick models based on synthetic vendor benchmarks that fall apart in production. Our mission with this leaderboard is simple: give enterprise teams an unbiased, production-grounded benchmark so they can choose the right model with statistical confidence."

#### [0:25 - 0:55] Systems Evaluated & Fair Comparison
> "We evaluate 10 flagship systems across open-source and commercial APIs—including pyannote 3.1, NVIDIA NeMo MSDD, WhisperX, Deepgram Nova-2, and AWS Transcribe. 
> 
> To keep the comparison fair between pure diarizers and ASR services, we decouple timestamps from text tokens, enforce a strict zero-oracle policy—meaning no model is given the speaker count upfront—and we test systems across two dedicated operational tracks: Batch and Real-Time Streaming."

#### [0:55 - 1:25] Benchmark Insights & Key Design Choices
> "Reading benchmarks like DIHARD III, VoxConverse, and CHiME-8 taught us that real conversation breaks models. That led to our two most critical design choices:
> 
> First, **a strict 0ms collar**. Traditional 250ms collars forgive 500 milliseconds of boundary error around every turn, which hides fatal interruptions. 
> 
> Second, **mandatory overlapping speech scoring**. 12% of human conversation is cross-talk, driving over half of downstream errors. We never forgive overlap, and we report a dedicated Overlap-DER."

#### [1:25 - 1:55] Statistical Rigor & Leaderboard UX
> "Next to each score, we don’t just show a single number. We publish 95% bootstrap confidence intervals, Wilcoxon significance indicators, Real-Time Factor, and cost per audio hour. Users can filter by their exact domain—like Enterprise Meetings, Telephony, or Medical.
> 
> In our empirical pilot on meeting audio, pyannote 3.1 achieved 12.8% DER, while legacy baselines collapsed to 32% purely due to overlap failure."

#### [1:55 - 2:00] Conclusion
> "This leaderboard bridges the gap between research metrics and real-world ROI. Thank you!"

---

### Step-by-Step Recording Instructions for Complete Submission
1. Open the interactive Leaderboard Mockup (`leaderboard_mockup.html` or slides).
2. Start Loom or Zoom with camera on and screen shared.
3. Read the script at a natural, steady pace. Practice once with a stopwatch to hit the 1:50–1:58 mark.
4. Export or get the link (Loom link, unlisted YouTube link, or Google Drive shareable link with "Anyone with link can view").
5. Paste the link into your `Firstname_Lastname_Q1_Main.pdf` and submission form!
