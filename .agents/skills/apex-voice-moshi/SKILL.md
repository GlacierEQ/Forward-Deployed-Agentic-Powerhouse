---
name: apex-voice-moshi
description: Real-time conversational voice gateway and Mimi neural audio codec engine (24kHz, 8 codebooks, 12.5 Hz, ~1.2 kbps ultra-dense archival).
version: 1.0.0
status: active
---

# APEX Voice & Neural Audio Codec (Moshi & Mimi)

High-performance real-time speech and evidentiary audio compression engine.

## Capabilities

| Capability | Role | Entry Point |
|---|---|---|
| `mimi.neural.compress` | 99.7% audio compression into discrete neural tokens (~1.2 kbps) | `scripts/apex_moshi_voice_engine.py compress` |
| `mimi.neural.decompress` | Lossless 24kHz acoustic reconstruction to WAV | `scripts/apex_moshi_voice_engine.py decompress` |
| `moshi.voice.gateway` | Full-duplex conversational voice streaming to remote GPU server | `scripts/apex_moshi_voice_engine.py connect` |
| `moshi.colab.recipe` | 1-click Google Colab remote GPU server launcher | `scripts/apex_moshi_voice_engine.py colab-recipe` |

## Usage

```bash
# Compress evidence audio
python3 .agents/skills/apex-voice-moshi/scripts/apex_moshi_voice_engine.py compress <input_audio> -o <output.mimi>

# Decompress to 24kHz WAV
python3 .agents/skills/apex-voice-moshi/scripts/apex_moshi_voice_engine.py decompress <input.mimi> -o <output.wav>

# Connect to Moshi full-duplex server
python3 .agents/skills/apex-voice-moshi/scripts/apex_moshi_voice_engine.py connect --url wss://<tunnel-url>
```
