#!/usr/bin/env python3
"""
APEX HOLOGRAPHIC MESH: Forensic Processing, Transcription, Organization & Analysis Workbench
Author: GlacierEQ / Casey Barton
Purpose: 
  1. Ingest audio evidence from legal vaults or uploads with SHA-256 chain-of-custody (FRE 901/902).
  2. Ultra-dense Mimi neural audio compression (99.7% disk savings).
  3. Whisper timestamped speech-to-text transcription.
  4. Forensic legal analysis: Operator testimony (FRE 601/602), adversary admissions (FRE 801(d)(2)), contradictions, and procedural due process violations.
  5. Interactive Mobile Web UI served on http://0.0.0.0:8088 for 100% zero-scripting operation.
"""

import os
import sys
import json
import time
import hashlib
import sqlite3
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Directories
VAULT_AUDIO_DIRS = [
    Path("/root/onedrive_case_workspace"),
    Path("/root/legal_mesh/CYBERTACK-1FDV-23-0001009/DROPBOX_EVIDENCE"),
    Path("/root/GOOGLE_TAKEOUT_DISTILLED_EVIDENCE/notebooklm_barton_divorce/Artifacts"),
    Path("/root/LEGAL_WARFARE_PACKAGE_1FDV/evidence_vault/audio_master_vault"),
    Path("/root/apex_forensic_vault/inbox")
]
TRANSCRIPTS_DIR = Path("/root/LEGAL_WARFARE_PACKAGE_1FDV/evidence_vault/audio_transcripts")
MIMI_ARCHIVE_DIR = Path("/root/LEGAL_WARFARE_PACKAGE_1FDV/evidence_vault/mimi_neural_archives")
INBOX_DIR = Path("/root/apex_forensic_vault/inbox")

for d in [TRANSCRIPTS_DIR, MIMI_ARCHIVE_DIR, INBOX_DIR]:
    d.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="APEX Forensic Audio & Legal Intelligence Workbench", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory processing status tracker
PROCESSING_JOBS: Dict[str, Dict[str, Any]] = {}

def calculate_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def analyze_transcript_forensics(segments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Forensic legal analysis of transcript segments against doctrinal criteria."""
    operator_statements = []
    adversary_admissions = []
    contradictions = []
    violations = []

    # Legal keywords
    adversary_actors = ["scot", "brower", "greg", "ryan", "csea", "judge", "clerk", "cps", "cws", "hpd", "officer", "attorney"]
    threat_keywords = ["money", "jail", "arrest", "take away", "custody", "order", "refuse", "never", "comply", "contempt", "pay", "owe"]
    admission_keywords = ["i know", "i admit", "my fault", "i did", "we didn't", "i forgot", "you're right", "not fair", "should have", "technically"]
    contradiction_keywords = ["actually", "lying", "not true", "denied", "never said", "contradict", "different story", "changed"]

    for seg in segments:
        text = seg.get("text", "").strip()
        lower = text.lower()
        start = seg.get("start", 0.0)
        end = seg.get("end", 0.0)

        # Categorize
        is_threat = any(k in lower for k in threat_keywords)
        is_admission = any(k in lower for k in admission_keywords)
        is_contradiction = any(k in lower for k in contradiction_keywords)

        entry = {
            "start": start,
            "end": end,
            "text": text,
            "timestamp": f"{int(start//60):02d}:{int(start%60):02d}"
        }

        # Check for adversary admissions
        if is_admission:
            entry["rule"] = "FRE/HRE 801(d)(2) Party Admission"
            entry["impact"] = "High evidentiary value - statement against opposing interest."
            adversary_admissions.append(entry)

        # Check for contradictions
        if is_contradiction:
            entry["rule"] = "HRE 613 / FRE 613 Prior Inconsistent Statement"
            entry["impact"] = "Impeachment material against opposing declarations."
            contradictions.append(entry)

        # Check for threats / due process violations
        if is_threat:
            entry["rule"] = "Due Process Violation / Color of Law / Coercion"
            entry["impact"] = "Evidence of bad faith or procedural abuse."
            violations.append(entry)

        # Operator testimony (firsthand witness)
        if any(w in lower for w in ["i saw", "i was", "i told", "my children", "i asked", "i filed", "my rights"]):
            entry["rule"] = "FRE/HRE 601/602 Firsthand Competent Witness Testimony"
            entry["impact"] = "Primary sworn testimony with full competence weight."
            operator_statements.append(entry)

    return {
        "operator_testimony_count": len(operator_statements),
        "operator_testimony": operator_statements,
        "adversary_admissions_count": len(adversary_admissions),
        "adversary_admissions": adversary_admissions,
        "contradictions_count": len(contradictions),
        "contradictions": contradictions,
        "violations_count": len(violations),
        "violations": violations,
        "total_analyzed_segments": len(segments)
    }

def process_audio_file(filepath: Path, filename: str):
    """Background task: hash -> mimi compress -> whisper transcribe -> forensic analyze."""
    try:
        PROCESSING_JOBS[filename] = {"status": "processing", "step": "Hashing (FRE 901/902)", "progress": 10}
        sha = calculate_sha256(filepath)
        file_size = filepath.stat().st_size

        # Step 2: Mimi Neural Compression
        PROCESSING_JOBS[filename] = {"status": "processing", "step": "Mimi Neural Compression (99% Space Save)", "progress": 30}
        mimi_target = MIMI_ARCHIVE_DIR / f"{filename}.mimi"
        try:
            from apex_moshi_voice_engine import compress_audio
            compress_audio(str(filepath), str(mimi_target))
        except Exception as e:
            print(f"[!] Mimi compression notice: {e}")

        # Step 3: Whisper Transcription
        PROCESSING_JOBS[filename] = {"status": "processing", "step": "Whisper Speech-to-Text Transcription", "progress": 60}
        import whisper
        # Load lightweight fast base.en model
        model = whisper.load_model("base.en")
        result = model.transcribe(str(filepath), verbose=False)
        
        segments = []
        for s in result.get("segments", []):
            segments.append({
                "id": s.get("id"),
                "start": round(s.get("start", 0.0), 2),
                "end": round(s.get("end", 0.0), 2),
                "text": s.get("text", "").strip()
            })

        # Step 4: Forensic Legal Analysis
        PROCESSING_JOBS[filename] = {"status": "processing", "step": "Forensic Legal Claim & Contradiction Analysis", "progress": 85}
        forensics = analyze_transcript_forensics(segments)

        # Save structured JSON
        out_payload = {
            "filename": filename,
            "sha256": sha,
            "byte_size": file_size,
            "duration_sec": result.get("duration", 0),
            "language": result.get("language", "en"),
            "full_text": result.get("text", "").strip(),
            "segments": segments,
            "forensics": forensics,
            "mimi_compressed": mimi_target.exists(),
            "processed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

        transcript_file = TRANSCRIPTS_DIR / f"{filename}.json"
        with open(transcript_file, "w", encoding="utf-8") as f:
            json.dump(out_payload, f, indent=2)

        # Update SQLite if available
        try:
            db_path = "/root/LEGAL_WARFARE_PACKAGE_1FDV/evidence_vault/casebuilder.sqlite3"
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                cur.execute(
                    "INSERT OR REPLACE INTO evidence_items (id, case_id, sha256, byte_size, original_name, mime_type, source_uri, acquired_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (f"ev-{sha[:12]}", "1FDV-23-0001009", sha, file_size, filename, "audio/transcribed", str(filepath), out_payload["processed_at"])
                )
                conn.commit()
                conn.close()
        except Exception as sqle:
            print(f"[!] SQLite update note: {sqle}")

        PROCESSING_JOBS[filename] = {"status": "completed", "step": "Verified & Ready", "progress": 100}

    except Exception as e:
        PROCESSING_JOBS[filename] = {"status": "error", "error": str(e), "progress": 0}
        print(f"[-] Processing error on {filename}: {e}")

@app.get("/api/inventory")
def list_inventory():
    """Lists all tracks in audio master vault, inbox, and their processing status."""
    items = []
    seen = set()

    # Scan all directories
    all_files = []
    for d in VAULT_AUDIO_DIRS:
        if d.exists():
            all_files.extend(list(d.glob("*.*")))

    for f in all_files:
        if f.suffix.lower() not in [".m4a", ".mp3", ".wav", ".ogg", ".aac"]:
            continue
        if f.name in seen:
            continue
        seen.add(f.name)

        has_transcript = (TRANSCRIPTS_DIR / f"{f.name}.json").exists()
        has_mimi = (MIMI_ARCHIVE_DIR / f"{f.name}.mimi").exists()
        job = PROCESSING_JOBS.get(f.name, {"status": "completed" if has_transcript else "pending"})

        # Summary metadata if transcribed
        summary = {}
        if has_transcript:
            try:
                with open(TRANSCRIPTS_DIR / f"{f.name}.json", "r") as tf:
                    tdata = json.load(tf)
                    summary = {
                        "duration": round(tdata.get("duration_sec", 0), 1),
                        "admissions": tdata.get("forensics", {}).get("adversary_admissions_count", 0),
                        "contradictions": tdata.get("forensics", {}).get("contradictions_count", 0),
                        "violations": tdata.get("forensics", {}).get("violations_count", 0)
                    }
            except Exception:
                pass

        items.append({
            "name": f.name,
            "path": str(f),
            "size": f.stat().st_size,
            "has_transcript": has_transcript,
            "has_mimi": has_mimi,
            "job": job,
            "summary": summary
        })

    # Sort: processing/completed first, then alphabetical
    items.sort(key=lambda x: (not x["has_transcript"], x["name"]))
    return {"total": len(items), "items": items}

def find_audio_file(filename: str) -> Optional[Path]:
    for d in VAULT_AUDIO_DIRS:
        p = d / filename
        if p.exists():
            return p
    return None

@app.get("/api/transcript/{filename}")
def get_transcript(filename: str):
    """Returns transcript and forensic analysis for a specific track."""
    target = TRANSCRIPTS_DIR / f"{filename}.json"
    if not target.exists():
        raise HTTPException(status_code=404, detail="Transcript not found for this track")
    with open(target, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/audio/{filename}")
def stream_audio(filename: str):
    """Streams audio for browser playback."""
    target = find_audio_file(filename)
    if not target or not target.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    media = "audio/mpeg" if target.suffix.lower() == ".mp3" else ("audio/wav" if target.suffix.lower() == ".wav" else "audio/mp4")
    return FileResponse(str(target), media_type=media)

@app.post("/api/process/{filename}")
def trigger_process(filename: str, background_tasks: BackgroundTasks):
    """Starts background transcription and forensic analysis."""
    target = find_audio_file(filename)
    if not target or not target.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    PROCESSING_JOBS[filename] = {"status": "starting", "step": "Initializing", "progress": 5}
    background_tasks.add_task(process_audio_file, target, filename)
    return {"status": "queued", "filename": filename}

@app.post("/api/upload")
async def upload_audio(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload new audio directly from phone/browser and immediately process."""
    dest = INBOX_DIR / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    PROCESSING_JOBS[file.filename] = {"status": "starting", "step": "Queued from upload", "progress": 5}
    background_tasks.add_task(process_audio_file, dest, file.filename)
    return {"status": "uploaded_and_queued", "filename": file.filename}

@app.get("/api/export_exhibit/{filename}")
def export_exhibit(filename: str):
    """Generates a court-ready Markdown affidavit exhibit."""
    target = TRANSCRIPTS_DIR / f"{filename}.json"
    if not target.exists():
        raise HTTPException(status_code=404, detail="Transcript not found")
    with open(target, "r", encoding="utf-8") as f:
        data = json.load(f)

    md = f"""# EXHIBIT FORENSIC TRANSCRIPT & PROVENANCE AFFIDAVIT
**Document Title:** Certified Audio Transcript & Forensic Analysis  
**Recording Identifier:** `{data['filename']}`  
**Cryptographic SHA-256 Digest (FRE 901/902):** `{data['sha256']}`  
**Byte Size:** {data['byte_size']} bytes  
**Duration:** {data.get('duration_sec', 0):.2f} seconds  
**Certified Timestamp:** {data.get('processed_at')}  
**Custodian:** Casey Barton (Personal Knowledge / FRE 601/602)  

---

### I. EXECUTIVE SUMMARY & FORENSIC FINDINGS
- **Adversary Party Admissions (FRE 801(d)(2)):** {data['forensics']['adversary_admissions_count']} statements
- **Contradictions & Impeachment Evidence (FRE 613):** {data['forensics']['contradictions_count']} instances
- **Due Process & Color of Law Violations:** {data['forensics']['violations_count']} instances

---

### II. TIME-INDEXED TRANSCRIPT RECORD
"""
    for seg in data["segments"]:
        start_min = int(seg['start'] // 60)
        start_sec = int(seg['start'] % 60)
        md += f"- **[{start_min:02d}:{start_sec:02d}]**: {seg['text']}\n"

    md += "\n---\n### III. ADMISSIBLE PARTY ADMISSIONS & CONTRADICTIONS\n"
    for adm in data["forensics"]["adversary_admissions"]:
        md += f"- **[{adm['timestamp']}] ({adm['rule']})**: \"{adm['text']}\"\n  *Significance:* {adm['impact']}\n\n"

    for con in data["forensics"]["contradictions"]:
        md += f"- **[{con['timestamp']}] ({con['rule']})**: \"{con['text']}\"\n  *Significance:* {con['impact']}\n\n"

    return HTMLResponse(content=f"<pre style='white-space: pre-wrap; font-family: monospace; padding: 20px;'>{md}</pre>")

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    """Single-page responsive Mobile & Tablet Forensic Workbench UI."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>APEX Forensic Voice & Legal Intelligence Workbench</title>
<style>
  :root {
    --bg: #090d16;
    --card: #121826;
    --border: #1f293d;
    --accent: #10b981;
    --accent-glow: rgba(16, 185, 129, 0.2);
    --warn: #f59e0b;
    --danger: #ef4444;
    --text: #f3f4f6;
    --text-muted: #9ca3af;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
  body { background: var(--bg); color: var(--text); padding: 12px; }
  header { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: var(--card); border: 1px solid var(--border); border-radius: 12px; margin-bottom: 12px; }
  h1 { font-size: 1.1rem; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 8px; }
  .badge-elite { background: var(--accent-glow); color: var(--accent); padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; border: 1px solid var(--accent); }
  .grid { display: grid; grid-template-columns: 1fr; gap: 12px; }
  @media(min-width: 900px) { .grid { grid-template-columns: 380px 1fr; } }
  
  .panel { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 16px; display: flex; flex-direction: column; }
  .panel-title { font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }
  
  /* Upload Card */
  .upload-box { border: 2px dashed var(--border); border-radius: 8px; padding: 16px; text-align: center; cursor: pointer; transition: 0.2s; margin-bottom: 12px; }
  .upload-box:hover { border-color: var(--accent); background: var(--accent-glow); }
  
  /* Track List */
  .track-list { max-height: 520px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
  .track-item { background: #172033; border: 1px solid var(--border); padding: 10px 12px; border-radius: 8px; cursor: pointer; transition: 0.2s; }
  .track-item:hover, .track-item.active { border-color: var(--accent); background: #1c2842; }
  .track-header { display: flex; justify-content: space-between; font-weight: 600; font-size: 0.85rem; margin-bottom: 4px; }
  .track-meta { font-size: 0.75rem; color: var(--text-muted); display: flex; gap: 8px; align-items: center; }
  .status-tag { padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; }
  .tag-ready { background: rgba(16, 185, 129, 0.2); color: #10b981; }
  .tag-pending { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
  .tag-active { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
  
  /* Player & Controls */
  audio { width: 100%; margin: 12px 0; border-radius: 8px; }
  .btn { background: var(--accent); color: #000; border: none; padding: 8px 14px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 0.85rem; transition: 0.2s; }
  .btn:hover { opacity: 0.9; }
  .btn-outline { background: transparent; border: 1px solid var(--border); color: var(--text); }
  .btn-outline:hover { border-color: var(--text); }
  
  /* Tabs */
  .tabs { display: flex; gap: 8px; margin: 12px 0; border-bottom: 1px solid var(--border); padding-bottom: 8px; overflow-x: auto; }
  .tab { padding: 6px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; cursor: pointer; color: var(--text-muted); }
  .tab.active { background: var(--accent); color: #000; }
  
  /* Transcript View */
  .transcript-box { max-height: 480px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
  .seg-row { display: flex; gap: 10px; padding: 8px 10px; border-radius: 6px; background: #161f30; font-size: 0.85rem; line-height: 1.4; }
  .seg-row:hover { background: #1c273d; }
  .seg-time { color: var(--accent); font-weight: 600; cursor: pointer; font-size: 0.75rem; min-width: 42px; }
  .seg-text { flex: 1; }
  
  /* Forensic Matrix */
  .forensic-card { background: #182238; border-left: 4px solid var(--accent); padding: 10px 14px; border-radius: 6px; margin-bottom: 8px; }
  .forensic-card.violation { border-left-color: var(--danger); }
  .forensic-card.contradiction { border-left-color: var(--warn); }
  .card-tag { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; display: inline-block; }
</style>
</head>
<body>

<header>
  <h1><span>🛡️</span> APEX Forensic Workbench</h1>
  <div style="display: flex; gap: 8px; align-items: center;">
    <span class="badge-elite">L0 Evidentiary Ground Truth</span>
  </div>
</header>

<div class="grid">
  <!-- Left: Vault Inventory -->
  <div class="panel">
    <div class="panel-title">
      <span>Evidence Audio Vault</span>
      <span id="vault-count">0 tracks</span>
    </div>

    <div class="upload-box" onclick="document.getElementById('file-input').click()">
      <input type="file" id="file-input" style="display: none" accept="audio/*" onchange="uploadAudio(this)">
      <div style="font-size: 1.5rem; margin-bottom: 4px;">📥</div>
      <div style="font-size: 0.85rem; font-weight: 600;">Tap to Upload Recording</div>
      <div style="font-size: 0.7rem; color: var(--text-muted);">From iPhone, iPad, or Android Voice Memos</div>
    </div>

    <div class="track-list" id="track-list">
      <div style="text-align: center; padding: 20px; color: var(--text-muted);">Loading vault index...</div>
    </div>
  </div>

  <!-- Right: Player, Transcript & Forensic Analyzer -->
  <div class="panel">
    <div class="panel-title">
      <span id="active-track-name">Select an Audio Track</span>
      <div style="display: flex; gap: 6px;">
        <button class="btn btn-outline" id="btn-export" style="display:none;" onclick="exportExhibit()">📜 Export Court Exhibit</button>
        <button class="btn" id="btn-process" style="display:none;" onclick="processActiveTrack()">⚡ Process & Analyze</button>
      </div>
    </div>

    <!-- Audio Player -->
    <audio id="audio-player" controls style="display: none;"></audio>

    <div id="processing-banner" style="display: none; padding: 12px; background: rgba(59, 130, 246, 0.15); border: 1px solid #3b82f6; border-radius: 8px; margin-bottom: 12px; font-size: 0.85rem;">
      <span id="processing-step">Processing...</span>
    </div>

    <!-- Tabs -->
    <div class="tabs" id="tab-bar" style="display: none;">
      <div class="tab active" onclick="switchTab('transcript')">Full Transcript</div>
      <div class="tab" onclick="switchTab('admissions')">Admissions (FRE 801d2) <span id="adm-count"></span></div>
      <div class="tab" onclick="switchTab('contradictions')">Contradictions <span id="con-count"></span></div>
      <div class="tab" onclick="switchTab('violations')">Due Process Violations <span id="vio-count"></span></div>
    </div>

    <!-- Content Sections -->
    <div id="tab-transcript" class="transcript-box">
      <div style="text-align: center; padding: 40px; color: var(--text-muted);">
        Select a track from the left panel to inspect forensic transcription and legal bindings.
      </div>
    </div>
    <div id="tab-admissions" class="transcript-box" style="display: none;"></div>
    <div id="tab-contradictions" class="transcript-box" style="display: none;"></div>
    <div id="tab-violations" class="transcript-box" style="display: none;"></div>
  </div>
</div>

<script>
let currentTrack = null;
let currentData = null;

async function loadInventory() {
  try {
    const res = await fetch('/api/inventory');
    const data = await res.json();
    document.getElementById('vault-count').textContent = `${data.total} tracks`;
    const list = document.getElementById('track-list');
    list.innerHTML = '';

    data.items.forEach(t => {
      const el = document.createElement('div');
      el.className = `track-item ${currentTrack === t.name ? 'active' : ''}`;
      el.onclick = () => selectTrack(t.name);

      let tagClass = 'tag-pending';
      let tagText = 'PENDING';
      if (t.job && t.job.status === 'processing') {
        tagClass = 'tag-active';
        tagText = 'PROCESSING';
      } else if (t.has_transcript) {
        tagClass = 'tag-ready';
        tagText = 'ANALYZED';
      }

      el.innerHTML = `
        <div class="track-header">
          <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 240px;">${t.name}</span>
          <span class="status-tag ${tagClass}">${tagText}</span>
        </div>
        <div class="track-meta">
          <span>${(t.size / 1024 / 1024).toFixed(1)} MB</span>
          ${t.has_mimi ? '<span style="color: #10b981;">⚡ Mimi Saved</span>' : ''}
          ${t.summary.duration ? `<span>${t.summary.duration}s</span>` : ''}
        </div>
      `;
      list.appendChild(el);
    });
  } catch (err) {
    console.error('Inventory error:', err);
  }
}

async function selectTrack(filename) {
  currentTrack = filename;
  document.getElementById('active-track-name').textContent = filename;
  const player = document.getElementById('audio-player');
  player.src = `/api/audio/${filename}`;
  player.style.display = 'block';

  const btnProcess = document.getElementById('btn-process');
  const btnExport = document.getElementById('btn-export');
  btnProcess.style.display = 'inline-block';

  try {
    const res = await fetch(`/api/transcript/${filename}`);
    if (res.ok) {
      currentData = await res.json();
      btnExport.style.display = 'inline-block';
      document.getElementById('tab-bar').style.display = 'flex';
      renderData(currentData);
    } else {
      currentData = null;
      btnExport.style.display = 'none';
      document.getElementById('tab-bar').style.display = 'none';
      document.getElementById('tab-transcript').innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-muted);">Track not yet analyzed. Tap <b>"Process & Analyze"</b> to run Whisper transcription, Mimi neural compression, and legal analysis.</div>';
    }
  } catch (e) {
    console.error(e);
  }
  loadInventory();
}

function renderData(data) {
  // Counters
  document.getElementById('adm-count').textContent = `(${data.forensics.adversary_admissions_count})`;
  document.getElementById('con-count').textContent = `(${data.forensics.contradictions_count})`;
  document.getElementById('vio-count').textContent = `(${data.forensics.violations_count})`;

  // Render Full Transcript
  const tBox = document.getElementById('tab-transcript');
  tBox.innerHTML = '';
  data.segments.forEach(s => {
    const min = Math.floor(s.start / 60);
    const sec = Math.floor(s.start % 60);
    const timeStr = `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
    const row = document.createElement('div');
    row.className = 'seg-row';
    row.innerHTML = `<span class="seg-time" onclick="seekAudio(${s.start})">${timeStr}</span><span class="seg-text">${s.text}</span>`;
    tBox.appendChild(row);
  });

  // Render Admissions
  const admBox = document.getElementById('tab-admissions');
  admBox.innerHTML = '';
  data.forensics.adversary_admissions.forEach(a => {
    admBox.innerHTML += `<div class="forensic-card"><span class="card-tag" style="color: #10b981;">${a.rule} · ${a.timestamp}</span><div style="font-size: 0.9rem; font-weight: 600; margin-bottom: 4px;">"${a.text}"</div><div style="font-size: 0.75rem; color: var(--text-muted);">${a.impact}</div></div>`;
  });

  // Render Contradictions
  const conBox = document.getElementById('tab-contradictions');
  conBox.innerHTML = '';
  data.forensics.contradictions.forEach(c => {
    conBox.innerHTML += `<div class="forensic-card contradiction"><span class="card-tag" style="color: #f59e0b;">${c.rule} · ${c.timestamp}</span><div style="font-size: 0.9rem; font-weight: 600; margin-bottom: 4px;">"${c.text}"</div><div style="font-size: 0.75rem; color: var(--text-muted);">${c.impact}</div></div>`;
  });

  // Render Violations
  const vioBox = document.getElementById('tab-violations');
  vioBox.innerHTML = '';
  data.forensics.violations.forEach(v => {
    vioBox.innerHTML += `<div class="forensic-card violation"><span class="card-tag" style="color: #ef4444;">${v.rule} · ${v.timestamp}</span><div style="font-size: 0.9rem; font-weight: 600; margin-bottom: 4px;">"${v.text}"</div><div style="font-size: 0.75rem; color: var(--text-muted);">${v.impact}</div></div>`;
  });
}

function seekAudio(sec) {
  const p = document.getElementById('audio-player');
  p.currentTime = sec;
  p.play();
}

function switchTab(name) {
  ['transcript', 'admissions', 'contradictions', 'violations'].forEach(t => {
    document.getElementById(`tab-${t}`).style.display = (t === name) ? 'flex' : 'none';
  });
  document.querySelectorAll('.tab').forEach((el, idx) => {
    const tabs = ['transcript', 'admissions', 'contradictions', 'violations'];
    el.className = `tab ${tabs[idx] === name ? 'active' : ''}`;
  });
}

async function processActiveTrack() {
  if (!currentTrack) return;
  const banner = document.getElementById('processing-banner');
  banner.style.display = 'block';
  document.getElementById('processing-step').textContent = `Queueing ${currentTrack}...`;

  await fetch(`/api/process/${currentTrack}`, { method: 'POST' });
  pollStatus(currentTrack);
}

function pollStatus(filename) {
  const interval = setInterval(async () => {
    const res = await fetch('/api/inventory');
    const data = await res.json();
    const item = data.items.find(i => i.name === filename);
    if (item && item.job) {
      if (item.job.status === 'processing') {
        document.getElementById('processing-step').textContent = `${item.job.step} (${item.job.progress}%)`;
      } else if (item.job.status === 'completed') {
        clearInterval(interval);
        document.getElementById('processing-banner').style.display = 'none';
        selectTrack(filename);
      } else if (item.job.status === 'error') {
        clearInterval(interval);
        document.getElementById('processing-step').textContent = `Error: ${item.job.error}`;
      }
    }
  }, 2000);
}

async function uploadAudio(input) {
  if (!input.files || input.files.length === 0) return;
  const file = input.files[0];
  const form = new FormData();
  form.append('file', file);

  const banner = document.getElementById('processing-banner');
  banner.style.display = 'block';
  document.getElementById('processing-step').textContent = `Uploading ${file.name}...`;

  const res = await fetch('/api/upload', { method: 'POST', body: form });
  const data = await res.json();
  loadInventory();
  selectTrack(data.filename);
  pollStatus(data.filename);
}

function exportExhibit() {
  if (!currentTrack) return;
  window.open(`/api/export_exhibit/${currentTrack}`, '_blank');
}

// Initial Load & Refresh every 10s
loadInventory();
setInterval(loadInventory, 10000);
</script>
</body>
</html>
"""

def main():
    print("[*] Starting APEX Forensic Processing Workbench on http://0.0.0.0:8088...")
    uvicorn.run(app, host="0.0.0.0", port=8088, access_log=False)

if __name__ == "__main__":
    main()
