"""Load the initial portfolio content (GitHub + LinkedIn + résumé).

    python manage.py seed_portfolio            # only fills an empty database
    python manage.py seed_portfolio --reset    # wipes content and reloads it

After the first run, edit everything from /admin instead.
"""
from datetime import date
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image

from portfolio.models import (
    Achievement,
    Certification,
    Project,
    ProjectImage,
    ProjectMetric,
    SiteProfile,
    SkillGroup,
    Stat,
    TimelineEntry,
)

SEED_MEDIA = Path(settings.BASE_DIR) / "seed_media"
GH = "https://github.com/Yadu080/"


def optimised(filename: str, max_width: int = 2000) -> ContentFile | None:
    src = SEED_MEDIA / filename
    if not src.exists():
        return None
    im = Image.open(src).convert("RGB")
    if im.width > max_width:
        im = im.resize((max_width, round(im.height * max_width / im.width)), Image.LANCZOS)
    buf = BytesIO()
    im.save(buf, "WEBP", quality=82, method=6)
    return ContentFile(buf.getvalue(), name=Path(filename).stem + ".webp")


PROFILE = dict(
    full_name="Yadunandan M Nimbalkar",
    hero_first_line="Yadunandan",
    hero_second_line="Nimbalkar",
    role="AI / ML Engineer",
    statement="I build AI systems that *show their work.*",
    manifesto=(
        "I'm a computer science student in Bengaluru specialising in AI & ML. I like models that "
        "*explain themselves*: recommenders that audit their own label leakage, health screens "
        "reported with *honest error bars*, and assistants that say *“I don't know”* and hand "
        "over to a human instead of guessing."
    ),
    bio=(
        "AI & ML engineering student at Global Academy of Technology, Bengaluru. Builds recommendation "
        "systems, retrieval-augmented assistants, speech and vision models, and the interfaces that make "
        "them explorable."
    ),
    location="Bengaluru, India",
    timezone="Asia/Kolkata",
    currently="B.E. Computer Science (AI & ML) · Global Academy of Technology · Class of 2027",
    open_to_work=True,
    availability_text="Open to AI Engineer & Data Scientist roles — on-site, hybrid or remote",
    email="yadunandanmn@gmail.com",
    github_username="Yadu080",
    github_url="https://github.com/Yadu080",
    linkedin_url="https://www.linkedin.com/in/yadunandan-m-nimbalkar-45950b211/",
    twitter_url="https://x.com/Techyness_8",
    closing_heading="Let's build something that *shows its work.*",
    meta_description=(
        "Portfolio of Yadunandan M Nimbalkar — AI/ML engineer building recommendation systems, RAG "
        "assistants, speech and vision models in Bengaluru."
    ),
)

STATS = [
    ("8.83", "CGPA", "B.E. CSE (AI & ML), 7th semester"),
    ("Top 20", "of 1,500+ teams", "Google Gen AI Academy APAC 2026"),
    ("39", "public repositories", "github.com/Yadu080"),
    ("10", "certifications", "Google, IBM, Cisco, Scaler"),
]

# ---------------------------------------------------------------------------
PROJECTS = [
    dict(
        title="RECOMAI",
        kicker="A two-stage neural movie recommender, built from scratch and deployed.",
        summary=(
            "Two-tower neural retrieval over MovieLens 20M, gradient-boosted re-ranking with an "
            "explanation for every pick, cold-start onboarding and a streaming-style React front end."
        ),
        year=2026, category="ml", role="Solo build", context="Recommendation systems",
        stack="Python, PyTorch, scikit-learn, FastAPI, PostgreSQL, React, Tailwind CSS",
        repo_url=GH + "Two-Tower_Recommendation_System",
        live_url="https://two-tower-recommendation-system.vercel.app",
        github_repo="Yadu080/Two-Tower_Recommendation_System",
        cover="recomai-landing.png", gallery=[("recomai-genres.png", "Cold-start genre picker — a taste vector from three clicks")],
        cover_style="constellation", featured=True, order=1, stars=1,
        metrics=[("29.5%", "Recall@100 on 2,000 held-out users"), ("~20 ms", "retrieval → ranked results"),
                 ("0.93", "honest validation AUC after a leakage audit (was 0.98)"), ("10,523", "films in the served catalogue")],
        body="""
## The problem
Scoring every one of 10,523 films with a heavyweight model on each page load is too slow. RECOMAI splits the work into two stages with very different cost profiles — the standard industry answer, implemented end to end.

## Stage 1 — Retrieval
Each user is a 128-dimensional vector combining a learned ID embedding with a normalised genre-preference vector. Both towers L2-normalise their output, so the dot product *is* cosine similarity and retrieval collapses to a single matrix multiply. The top 500 candidates survive. The network is trained with an InfoNCE loss on MovieLens 20M (20M ratings from 138,493 users).

## Stage 2 — Re-ranking
The 500 candidates pass through a gradient-boosted classifier scoring each (user, movie) pair on eight engineered features — embedding similarity, average rating, popularity, genre overlap and cross terms. Every result is annotated with *why* it was chosen.

## The leakage audit
The first ranker reported a validation AUC of 0.98 — too good to be true. Tracing the features revealed label leakage in ranker training. Fixing it dropped AUC to an **honest 0.93**, which is the number reported.

## Cold start
New users have no learned embedding, so one is synthesised by averaging the item vectors of films in their chosen genres — placing them in the same space as trained users with no special-casing downstream.

## Results
- Recall@10 = 11.7% (about 123× random), Recall@100 = 29.5%, NDCG@100 = 11.2% on 2,000 held-out users
- ~20 ms typical latency from retrieval to ranked results, served by FastAPI + PostgreSQL
""",
    ),
    dict(
        title="Silence Engine",
        kicker="Detect what should have happened, but didn't.",
        summary=(
            "An early-warning tool that tells a real service-access gap from a broken data feed — and "
            "says plainly what it cannot conclude. Built for the IBM Z Datathon 2026."
        ),
        year=2026, category="data", role="Solo build", context="IBM Z Datathon 2026 · Wildcard theme",
        stack="Python, Flask, SQLite, React, TypeScript, IBM LinuxONE",
        repo_url=GH + "silence-engine", github_repo="Yadu080/silence-engine",
        cover="silence-map.jpg", gallery=[("silence-overview.jpg", "Overview — expected versus observed activity across services")],
        cover_style="grid", featured=True, order=2,
        metrics=[("4", "triage hypotheses, each with evidence for and against"), ("8 wk", "strictly causal same-weekday baseline"),
                 ("s390x", "runs on IBM LinuxONE as well as macOS and Linux"), ("100%", "synthetic data — no real-world claims")],
        body="""
## The idea
Most monitoring looks at events that occurred. Silence Engine also investigates **expected activity that never appeared** at public-service locations — clinics, benefits offices, food hubs, water points — and asks *why*.

A falling count is ambiguous: people may have been unable to reach a service, or the data feed may simply have broken. Treating those as the same thing sends help to the wrong place.

## Four hypotheses, never verdicts
- **Potential service-access gap** — trusted counts far below baseline while the feed looks healthy
- **Likely reporting problem** — missing records, flatlines, stale values, partial uploads
- **Expected variation** — scheduled closures, ordinary variation
- **Uncertain: investigate** — conflicting or insufficient evidence

## How it works
1. Validate aggregate daily records — a blank count is *missing*, never zero.
2. Check feed health independently of activity: heartbeats, freshness, flatlines, placeholder zeros, duplicates.
3. Expect: the median of the same weekday over the previous 8 weeks, using only days that were trustworthy at the time.
4. Measure the gap with a robust z-score and a CUSUM, requiring persistence over days.
5. Triage into the four hypotheses with limitations and verification steps. Every human review lands in a hash-chained audit log.

The silence map shows each service as a row and each day as a cell: amber means trustworthy counts fell below expectation; hatched means there is *no trustworthy count* — unknown, not zero.
""",
    ),
    dict(
        title="MusicDNA",
        kicker="Your taste, mapped — a galaxy of artists you can fly through.",
        summary=(
            "Turns listening history into an archetype, a genre-gravity profile, taste drift over time "
            "and an interactive 3D artist galaxy rendered in a single GPU draw call."
        ),
        year=2026, category="ml", role="Solo build", context="Taste modelling · 3D visualisation",
        stack="Next.js, TypeScript, Three.js, FastAPI, Python, Tailwind CSS",
        repo_url=GH + "musicdna", github_repo="Yadu080/musicdna",
        cover="musicdna-galaxy.png",
        gallery=[("musicdna-landing.png", "Landing — “Your taste, mapped.”"), ("musicdna-report.png", "The DNA report: archetype, genre gravity and eras")],
        cover_style="constellation", featured=True, order=3,
        metrics=[("118", "tests, strict TypeScript"), ("60 fps", "on an 8 GB MacBook Air, no GPU"),
                 ("1", "draw call for every star in the galaxy"), ("8", "musical archetypes")],
        body="""
## What you get
Connect Spotify, upload your listening history, or just say what you like. A minute later you have:

- **A musical archetype** — one of eight, computed from the acoustic shape of everything you play (*Nocturnal Cartographer*, *Circuit Dreamer*, *Solar Anthemist*)
- **Genre gravity** — a weighted distribution, not a list
- **Distance from the charts** — measured against how widely known your artists actually are
- **Taste drift** — your all-time self against your recent self
- **Listening eras** — a narrative timeline built from real dates

## The galaxy
Every artist is a star and every genre a constellation. Drag to orbit, scroll to zoom, click a star and the camera flies to it, opening its nearest neighbours in taste-space.

It runs at 60 fps on a MacBook Air because every star is drawn in **one GPU draw call** with the glow computed in a shader — no per-star objects, no post-processing. Quality scales to the device, and there is a full list view for anyone who would rather read than fly.

## No black box
Every import shows *what it read* next to *what it concluded* — how many artists, tracks and playlists went in, and exactly which genres came out.

## The lab
Four analysers you can point at anything: paste a lyric for its emotional weather, upload album art for its palette and mood, and more.
""",
    ),
    dict(
        title="MoodScript",
        kicker="An AI journal that reads how you feel — and a paper on why calibration matters.",
        summary=(
            "Text and face emotion detection fused with calibration-aware logic, a therapist companion "
            "with long-term memory, crisis-aware safety and support for Hindi and Kannada."
        ),
        year=2026, category="genai", role="Team project", context="Multimodal emotion AI · Research",
        stack="Python, FastAPI, React, PostgreSQL, Hugging Face, Groq, Cloud Run, GitHub Actions",
        repo_url=GH + "MoodScript", live_url="https://moodscript-frontend-2wr445ogxq-uc.a.run.app/",
        github_repo="Yadu080/MoodScript", cover_style="waves", featured=True, order=4,
        metrics=[("0.235 → 0.035", "text-model ECE after temperature scaling"), ("+7.11 pts", "best accuracy lift from calibrating before fusion"),
                 ("2", "modalities fused — text and face"), ("3", "languages: English, Hindi, Kannada")],
        body="""
## What it is
A full-stack emotional journaling app. You write, speak or show your face, and MoodScript detects your emotion, fuses the signals, and responds as **Aria** — a therapist-persona companion that remembers your last conversation, your last week and your long-term patterns.

## The headline finding
The original fusion rule — a confidence-weighted linear blend — performed **worse than the face model alone**: 83.36% against 88.39%. Fusion was destroying information.

The cause was a calibration mismatch. The text model (DistilRoBERTa) was badly overconfident, with an Expected Calibration Error of 0.235; the face model (ViT) was already well calibrated at 0.029. A confidence-weighted rule treats “0.9 from text” and “0.9 from face” as equal evidence. They are not.

Temperature-scaling each model *before* combining them lifted every classical combination rule tested, by between 1.67 and 7.11 percentage points. The project produced a paper on exactly this question.

## Built responsibly
- Crisis signals surface helpline resources only when something is genuinely serious
- LIME explainability behind a “why?” button on every response
- An LLM arbiter was implemented, measured, and **disabled by default** because it did not improve accuracy
- A soundtrack built on music therapy's iso-principle: meet the listener where they are, then move gradually
""",
    ),
    dict(
        title="Voice·PD",
        kicker="Screening for Parkinson's disease from three seconds of voice.",
        summary=(
            "A multilingual self-supervised speech model (wav2vec2-XLS-R) that screens for Parkinson's "
            "from a sustained vowel — evaluated with subject-grouped cross-validation."
        ),
        year=2026, category="health", role="Co-developed · team", context="AI for health",
        stack="Python, PyTorch, wav2vec2-XLS-R, scikit-learn, XGBoost, LightGBM, Flask",
        repo_url=GH + "Parkinson-s_voice_detection", github_repo="Yadu080/Parkinson-s_voice_detection",
        cover="voicepd-hero.png", cover_style="bars", featured=True, order=5,
        metrics=[("0.972", "cross-validated AUC (± 0.034)"), ("95.1%", "subject-level accuracy, 58 of 61"),
                 ("0.31", "AUC of hand-crafted features across languages — why we shipped wav2vec2"), ("3 s", "of “aaah” is enough")],
        body="""
## The approach
Two pipelines were compared on 831 recordings from 61 subjects:

- **Frozen wav2vec2-XLS-R embeddings** (1024-dimensional, pretrained on 128 languages) feeding a logistic regression
- **A 56-feature acoustic pipeline** — jitter, shimmer, MDVP measures — feeding an XGBoost, LightGBM and Random Forest ensemble

## Honest evaluation
Everything is evaluated with 5-fold **subject-grouped** cross-validation, so no speaker ever appears in both train and test. Results: CV AUC 0.972 ± 0.034, F1 0.945, subject-level accuracy 95.1% (58/61).

## The cross-language finding
Hand-crafted acoustic features looked strong in-language but collapsed across languages — Italian-trained to English-tested AUC of **0.31**, worse than chance. The multilingual self-supervised model did not care what language you speak, so that is the model that shipped, behind a Flask API accepting six audio formats.

*A screening prototype, not a diagnostic tool.*
""",
    ),
    dict(
        title="CivicPulse AI",
        kicker="Community decision intelligence — not just answers, better decisions.",
        summary=(
            "Turns raw civic complaint data into prioritised, explainable decisions. Deterministic analytics "
            "first, Gemini second. Ranked Top 20 of 1,500+ teams in Google Gen AI Academy APAC."
        ),
        year=2026, category="genai", role="Team of 3 · CodeSickos", context="Google Gen AI Academy APAC · Top 20",
        stack="Python, Pandas, Streamlit, Gemini API, Vertex AI, Docker, Cloud Run, Cloud Build",
        repo_url=GH + "CivicPulse-AI", github_repo="Yadu080/CivicPulse-AI", cover_style="rings", featured=True, order=6,
        metrics=[("Top 20", "of 1,500+ teams across 12 APAC nations"), ("4", "metric priority scoreboard"),
                 ("0", "API keys stored in production — keyless Vertex AI auth"), ("4", "input formats: CSV, JSON, PDF, text")],
        body="""
## Not another chatbot
CivicPulse AI helps cities, communities and operations teams decide what to fix first. Upload local service data, ask questions in plain language, detect emerging anomalies and generate executive briefs.

## Deterministic first, LLM second
Python computes trends, hotspot areas, severity mix, open-case rates and z-score anomalies **before** Gemini is involved. Gemini then explains what matters and recommends next steps — strictly grounded in the computed analytics. Rule-based fallbacks keep every feature usable during model outages.

## Shipped on Google Cloud
Containerised with Docker and deployed on Cloud Run through a Cloud Build pipeline, authenticated with a Vertex AI service account so no API key is stored in production.

## Recognition
Selected 20th among the top 100 teams out of 1,500+ in the Google Gen AI Academy APAC Edition, Cohort 2 — builders from India, Singapore, Indonesia, Japan, South Korea, Malaysia, the Philippines, Thailand, Vietnam, Australia and more. Built with Aadithya AR (lead) and Kenisha P.
""",
    ),
    # ---- archive ----------------------------------------------------------
    dict(
        title="ModelHunter", kicker="Autonomous adversarial ML security evaluation platform.",
        summary="Load a model, run white- and black-box attacks, apply defences, explain with GradCAM and SHAP, and export PDF reports — every metric from real execution.",
        year=2026, category="security", role="Team project", context="ML security",
        stack="PyTorch, FastAPI, SQLAlchemy, React, Captum, SHAP, Docker",
        repo_url=GH + "Model_Hunter", github_repo="Yadu080/Model_Hunter", cover_style="grid", order=10,
        metrics=[("5", "attacks: FGSM, PGD, C&W, ZOO, HopSkipJump"), ("3", "defence families"), ("3", "datasets: MNIST, CIFAR-10, GTSRB")],
        body="Evaluates the robustness of CNN, ResNet18 and MobileNetV2 models against adversarial attacks through a web dashboard. Defences include adversarial training, ensembles and input preprocessing; metrics cover clean vs adversarial accuracy, attack success rate, confidence shift, transferability and a robustness score. Runs on CUDA, Apple MPS or CPU with automatic detection.",
    ),
    dict(
        title="AI Codebase Analyzer", kicker="Ask any GitHub repository questions in plain English.",
        summary="RAG over source code: line-aware chunking, MiniLM embeddings, FAISS search and Llama 3.3 70B answers grounded in retrieved snippets, plus an AST import graph.",
        year=2026, category="genai", role="Solo build", context="Retrieval-augmented generation",
        stack="Python, FastAPI, FAISS, Sentence-Transformers, Groq, Next.js",
        repo_url=GH + "AI-Codebase-Analyzer", live_url="https://democodebaseanalyser-q.streamlit.app/",
        github_repo="Yadu080/AI-Codebase-Analyzer", cover_style="constellation", order=11, stars=3,
        metrics=[("384-d", "MiniLM embeddings"), ("Top-5", "retrieved chunks to Llama 3.3 70B"), ("SHA", "indexes cached per commit")],
        body="Clones a public repository, splits it into semantically meaningful chunks, embeds them into a FAISS index and answers questions with the actual code as context. A static AST import graph maps module dependencies without executing anything, and the pipeline is hardened against command injection, memory blow-ups, vendored-code noise and cross-session leakage.",
    ),
    dict(
        title="ClauseGuard", kicker="Catches the rewrite that quietly changed the rule.",
        summary="A rule-based NLP detector for critical meaning drift in rewritten policies: dropped negations, must→may, missing exceptions, narrowed bounds and changed numbers — with evidence for every flag.",
        year=2026, category="genai", role="Solo build", context="Explainable NLP",
        stack="Python, Regex, Streamlit", repo_url=GH + "clauseguard", github_repo="Yadu080/clauseguard",
        cover_style="bars", order=12,
        metrics=[("5", "explainable constraint checks"), ("152", "pair reproducible benchmark"), ("0", "LLMs or API keys needed")],
        body="Compares an original sentence with its rewrite and flags places where an important constraint may have been lost: a dropped *not*, a *must* that became *may*, a missing *unless*, a 75% that became 70%. Handles traps like “no more than” (a bound, not a negation) and “15 May” (a date, not a modal). Includes passage alignment, batch CSV audits and a CLI with exit codes.",
    ),
    dict(
        title="Synapse Notebook", kicker="An AI-first workspace for reading across documents.",
        summary="Multi-document RAG with grounded chat, summaries, flashcards, MCQs, knowledge-gap detection, concept battles and a browser-read podcast mode.",
        year=2026, category="genai", role="Solo build", context="Knowledge tools",
        stack="Next.js, TypeScript, Express, RAG", repo_url=GH + "Synapse_Notebook_llm",
        live_url="https://synapse-notebook-llm.vercel.app/", github_repo="Yadu080/Synapse_Notebook_llm",
        cover_style="waves", order=13, stars=1, metrics=[], body="",
    ),
    dict(
        title="ShopEase RAG Support Assistant", kicker="Customer support that escalates instead of hallucinating.",
        summary="LangGraph state machine over ChromaDB with intent routing and four human-in-the-loop escalation triggers, at under $0.004 per query.",
        year=2026, category="genai", role="Solo build", context="Production RAG",
        stack="Python, LangGraph, ChromaDB, FastAPI, Groq", repo_url=GH + "RAG-Based-E-Commerce-Customer-Support-Assistant",
        github_repo="Yadu080/RAG-Based-E-Commerce-Customer-Support-Assistant", cover_style="constellation", order=14,
        metrics=[("< $0.004", "per query"), ("4", "escalation triggers"), ("7", "routed intents")], body="",
    ),
    dict(
        title="Zephvion Voice Agent", kicker="An AI receptionist that answers calls 24/7.",
        summary="Books appointments on a real calendar, qualifies leads, raises tickets, warm-transfers to humans and speaks nine languages — on free tiers.",
        year=2026, category="fullstack", role="Solo build", context="Voice AI automation",
        stack="Python, Vapi, Google Calendar API, Webhooks", repo_url=GH + "zephvion-voice-agent",
        github_repo="Yadu080/zephvion-voice-agent", cover_style="bars", order=15, metrics=[], body="",
    ),
    dict(
        title="Gemini Journal & Reflections Vault", kicker="A private thought partner with tenant-isolated storage.",
        summary="Gemini-powered reflection with an automatic model fallback ladder, owner-bound Firestore rules, Google SSO and zero-secret Cloud Run deployment.",
        year=2026, category="genai", role="Solo build", context="Google Cloud · Accelerate AI with Cloud Run",
        stack="React, TypeScript, Firebase, Firestore, Gemini API, Cloud Run, Secret Manager",
        repo_url=GH + "Gemini_Journal", github_repo="Yadu080/Gemini_Journal", cover_style="waves", order=16, metrics=[], body="",
    ),
    dict(
        title="WhatsApp Ordering Bot", kicker="Browse, cart, checkout and pay without leaving the chat.",
        summary="Native WhatsApp catalog ordering with guided checkout (UPI/QR or cash) and an owner panel to change availability, fees and GST without code.",
        year=2026, category="fullstack", role="Solo build", context="Commerce automation",
        stack="Python, FastAPI, WhatsApp Cloud API", repo_url=GH + "whatsapp-ordering-bot",
        github_repo="Yadu080/whatsapp-ordering-bot", cover_style="grid", order=17, metrics=[], body="",
    ),
    dict(
        title="Resume Screener AI", kicker="Extract → match → score → explain → verdict.",
        summary="An LLM pipeline that reads a résumé against a job description like an experienced engineer, with a 0–100 score and a reasoned hire/hold decision.",
        year=2026, category="genai", role="Solo build", context="LLM pipelines",
        stack="Python, LLMs", repo_url=GH + "resume-screener-ai", github_repo="Yadu080/resume-screener-ai",
        cover_style="bars", order=18, metrics=[], body="",
    ),
    dict(
        title="ASD Early-Screen", kicker="Secure, explainable early autism-risk screening on IBM LinuxONE.",
        summary="Logistic regression with SHAP explanations and encrypted model artefacts, built by team Code Warriors (GAT-174) for the IBM Z Datathon 2025.",
        year=2025, category="health", role="Team · Code Warriors", context="IBM Z Datathon 2025",
        stack="Python, scikit-learn, SHAP, Flask, IBM LinuxONE", repo_url=GH + "ASD_Early-Screen",
        github_repo="Yadu080/ASD_Early-Screen", cover_style="rings", order=19, stars=1, metrics=[], body="",
    ),
    dict(
        title="LexAssist", kicker="Legal-document Q&A for people who can't afford a lawyer for every contract.",
        summary="Architecture for clause-cited answers in English or Hindi: clause-aware chunking, hybrid vector + BM25 search, re-ranking and Redis caching on Gemini Flash.",
        year=2026, category="genai", role="Architecture", context="Google GenAI APAC Challenge",
        stack="Gemini, RAG, BM25, Redis", cover_style="constellation", order=20, metrics=[], body="",
    ),
    dict(
        title="AI PDF Summarizer", kicker="Five summary styles, three export formats.",
        summary="Flask app on Gemini 2.5 Flash with live extraction progress, summary history and ratings, exporting to TXT, PDF and DOCX.",
        year=2026, category="genai", role="Solo build", context="Document AI",
        stack="Python, Flask, Gemini API, SQLite, WebSockets", repo_url=GH + "AI-PDF_SUMMARIZER",
        github_repo="Yadu080/AI-PDF_SUMMARIZER", cover_style="waves", order=21, metrics=[], body="",
    ),
    dict(
        title="Toxic Plant Identification", kicker="A CNN that tells toxic plants from safe ones.",
        summary="TensorFlow/Keras image classifier served through a Flask web interface, built with Sanjay and Rudraksh for the IBM Z Datathon 2024.",
        year=2024, category="ml", role="Team of 3", context="IBM Z Datathon 2024",
        stack="TensorFlow, Keras, OpenCV, Flask", repo_url=GH + "TOXIC_PLANT_IDENTIFICATION",
        github_repo="Yadu080/TOXIC_PLANT_IDENTIFICATION", cover_style="grid", order=22, metrics=[], body="",
    ),
    dict(
        title="Mentcare Patient Management", kicker="A software-engineering case study.",
        summary="Requirements, design and modelling for a mental-health patient management system, completed for the Software Development course.",
        year=2025, category="coursework", role="Team · coursework", context="Software engineering",
        stack="UML, Python", repo_url=GH + "Mentcare-Patient-Management-System",
        github_repo="Yadu080/Mentcare-Patient-Management-System", cover_style="rings", order=30, metrics=[], body="",
    ),
]

ACHIEVEMENTS = [
    dict(headline="Top 20", title="of 1,500+ teams — Google Gen AI Academy APAC, Cohort 2",
         organization="Google Cloud × Hack2skill", year="2026", kind="award", highlight=True, order=1,
         description="Team CodeSickos was selected 20th among the top 100 teams from 12 Asia-Pacific nations for CivicPulse AI.",
         project="CivicPulse AI"),
    dict(headline="Elite", title="Invited to the Gen AI Elite Club",
         organization="Google Cloud × Hack2skill", year="2026", kind="award", highlight=True, order=2,
         description="Alumni community for top-performing participants of the Gen AI Academy APAC Edition."),
    dict(headline="Head Boy", title="School Head Boy & Best Student of the Year",
         organization="Podar International School, Bengaluru", year="2021", kind="leadership", highlight=True, order=3,
         description="Elected to lead the student body and coordinate school-wide initiatives."),
    dict(title="IBM Z Datathon 2026 — Silence Engine", organization="IBM · Theme 3, Wildcard “Beyond the Obvious”",
         year="2026", kind="hackathon", order=10, project="Silence Engine"),
    dict(title="Google Gen AI Academy APAC — Cohort 1 & Cohort 2 completion", organization="Google Cloud × Hack2skill",
         year="2026", kind="program", order=11),
    dict(title="Cognizant TechnoVerse Hackathon — Agent Builder Challenge", organization="Cognizant",
         year="2026", kind="hackathon", order=12),
    dict(title="Google GenAI APAC Challenge — LexAssist architecture", organization="Google Cloud × Hack2skill",
         year="2026", kind="hackathon", order=13, project="LexAssist"),
    dict(title="Google Gen AI Hackathon", organization="Google", year="2026", kind="hackathon", order=14),
    dict(title="IBM Z Datathon 2025 — ASD Early-Screen", organization="IBM · Team Code Warriors (GAT-174)",
         year="2025", kind="hackathon", order=15, project="ASD Early-Screen"),
    dict(title="PES CTF", organization="PES University", year="2025", kind="hackathon", order=16),
    dict(title="IBM Z Datathon 2024 — Toxic Plant Identification", organization="IBM",
         year="2024", kind="hackathon", order=17, project="Toxic Plant Identification"),
]

CB = "https://www.cloudskillsboost.google/public_profiles/f60561b8-1334-4239-8f78-7d8e8a1bbda6/badges/"
CERTIFICATIONS = [
    ("AI Fundamentals: Foundations for Understanding AI", "IBM", date(2026, 7, 1),
     "https://www.credly.com/badges/6e8cc074-ec40-4762-a168-cfc73bc20030", ""),
    ("Engineer AI Agents with Agent Development Kit (ADK)", "Google", date(2026, 5, 1),
     "https://www.credly.com/badges/e56dc1e9-93ad-43d3-80ba-cc8321d0f16d", "Google ADK"),
    ("Gen AI Academy APAC Edition — Certificate of Completion", "Google Cloud × Hack2skill", date(2026, 4, 1), "", "Gemini, Vertex AI"),
    ("Data Science Essentials with Python", "Cisco Networking Academy", date(2025, 11, 1),
     "https://www.credly.com/badges/c88ba7e7-68ff-415d-a0f1-b08133915d2d", "Python, Data Science"),
    ("Computer Networking: Master Computer Networking", "Scaler", date(2025, 10, 1),
     "https://moonshot.scaler.com/s/sl/kwWBlwD9CQ", "Computer Networking"),
    ("Prompt Design in Vertex AI", "Google", date(2025, 5, 1), CB + "15534830", "Vertex AI, Prompt Engineering"),
    ("Getting Started with Artificial Intelligence", "IBM", date(2024, 10, 1),
     "https://www.credly.com/badges/fe63377a-c387-4f56-9bf4-fcbebc445bba", ""),
    ("Introduction to Large Language Models", "Google Cloud Skills Boost", date(2024, 8, 1), CB + "10593003", "LLMs"),
    ("Introduction to Generative AI", "Google Cloud Skills Boost", date(2024, 8, 1), CB + "10573326", "Generative AI"),
    ("NCC ‘A’ Certificate", "National Cadet Corps, India", date(2020, 3, 1), "", "Leadership, Discipline"),
]

TIMELINE = [
    ("education", "B.E. Computer Science & Engineering (AI & ML)", "Global Academy of Technology, Bengaluru",
     "2023 — 2027", "CGPA 8.83 / 10",
     "Machine Learning, Artificial Intelligence, Data Mining & Warehousing, DBMS, Data Structures & Algorithms, Cloud Computing, Software Engineering, Operating Systems."),
    ("education", "Grades 11 & 12 · CBSE (PCMC)", "Podar International School, Bengaluru", "2021 — 2023", "82%",
     "Elected School Head Boy; Best Student of the Year 2021."),
    ("education", "Grade 10 · CBSE", "Sri Vidya Kendra — The Smart School", "2020 — 2021", "91%", ""),
    ("volunteering", "Public Speaker", "Project Yagna", "May 2021 — Nov 2022", "Children & education",
     "Visited government schools across Karnataka with a team, running awareness sessions on hygiene, sanitation and human biology."),
]

SKILLS = [
    ("Languages", "Python, SQL, TypeScript, JavaScript, Java, C", True),
    ("Machine learning", "PyTorch, scikit-learn, XGBoost, LightGBM, TensorFlow, Keras, Pandas, NumPy, SHAP, LIME", True),
    ("Generative AI & NLP", "LLMs, RAG, LangGraph, Prompt engineering, Hugging Face Transformers, Sentence-Transformers, FAISS, ChromaDB, Gemini API, Groq API, Google ADK", True),
    ("Engineering", "FastAPI, Flask, Django, REST APIs, Streamlit, React, Next.js, Three.js, Tailwind CSS", False),
    ("Cloud & data", "Google Cloud Run, Vertex AI, Cloud Build, Docker, CI/CD, Git, PostgreSQL, MongoDB, MySQL, SQLite, IBM LinuxONE", False),
]


class Command(BaseCommand):
    help = "Load initial portfolio content."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete existing content first.")

    @transaction.atomic
    def handle(self, *args, reset=False, **opts):
        if Project.objects.exists() and not reset:
            self.stdout.write(self.style.WARNING("Content already exists — use --reset to reload."))
            return
        if reset:
            for model in (Achievement, Certification, ProjectImage, ProjectMetric, Project, SkillGroup, Stat, TimelineEntry):
                model.objects.all().delete()

        profile = SiteProfile.load()
        for k, v in PROFILE.items():
            setattr(profile, k, v)
        profile.save()

        for i, (value, label, note) in enumerate(STATS):
            Stat.objects.create(value=value, label=label, note=note, order=i)

        by_title = {}
        for data in PROJECTS:
            data = dict(data)
            metrics = data.pop("metrics", [])
            gallery = data.pop("gallery", [])
            cover = data.pop("cover", None)
            data["body"] = data.get("body", "").strip()
            project = Project(**data)
            if cover and (f := optimised(cover)):
                project.cover.save(f.name, f, save=False)
            project.save()
            by_title[project.title] = project
            for i, (value, label) in enumerate(metrics):
                ProjectMetric.objects.create(project=project, value=value, label=label, order=i)
            for i, (img, caption) in enumerate(gallery):
                if f := optimised(img):
                    pi = ProjectImage(project=project, caption=caption, order=i)
                    pi.image.save(f.name, f, save=True)

        for data in ACHIEVEMENTS:
            data = dict(data)
            title = data.pop("project", None)
            Achievement.objects.create(project=by_title.get(title), **data)

        for i, (title, issuer, issued, url, skills) in enumerate(CERTIFICATIONS):
            Certification.objects.create(title=title, issuer=issuer, issued=issued, credential_url=url, skills=skills, order=i)

        for i, (kind, title, org, period, detail, desc) in enumerate(TIMELINE):
            TimelineEntry.objects.create(kind=kind, title=title, organization=org, period=period, detail=detail, description=desc, order=i)

        for i, (name, skills, marquee) in enumerate(SKILLS):
            SkillGroup.objects.create(name=name, skills=skills, in_marquee=marquee, order=i)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(PROJECTS)} projects, {len(CERTIFICATIONS)} certifications."))
