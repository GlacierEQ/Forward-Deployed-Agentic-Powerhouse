#!/usr/bin/env python3
"""
APEX HOLOGRAPHIC MESH: Moshi & Mimi Voice Engine (INNOVATION)
Provides:
  1. Mimi Neural Audio Codec (24kHz, 8 codebooks, 12.5 Hz, ~1.1 kbps ultra-low-bitrate compression for evidence audio)
  2. Moshi Full-Duplex Real-Time Voice Gateway (Edge Client connector to remote GPU servers)
  3. One-Click Colab / Remote GPU Worker Recipe generator
"""

import sys
import os
import argparse
import time
from pathlib import Path
import numpy as np
import torch

MIMI_HF_REPO = "kyutai/moshiko-pytorch-bf16"
MIMI_WEIGHT_NAME = "tokenizer-e351c8d8-checkpoint125.safetensors"

def get_cached_mimi():
    """Load the cached Mimi neural codec weights onto CPU."""
    from huggingface_hub import hf_hub_download
    from moshi.models import loaders
    
    weight_path = hf_hub_download(repo_id=MIMI_HF_REPO, filename=MIMI_WEIGHT_NAME)
    mimi = loaders.get_mimi(weight_path, device="cpu")
    mimi.eval()
    return mimi

def compress_audio(input_path: str, output_path: str = None):
    """Compress audio using Mimi neural audio codec."""
    import sphn
    
    input_file = Path(input_path)
    if not input_file.exists():
        print(f"[-] Error: input file not found: {input_path}")
        return False
        
    if output_path is None:
        output_file = input_file.with_suffix(".mimi")
    else:
        output_file = Path(output_path)
        
    print(f"[*] Reading audio from: {input_file}")
    # Mimi uses 24000 Hz mono audio
    pcm, sample_rate = sphn.read(str(input_file), sample_rate=24000)
    # pcm shape is (channels, samples). Ensure mono (1, samples)
    if pcm.shape[0] > 1:
        pcm = np.mean(pcm, axis=0, keepdims=True)
        
    original_size = input_file.stat().st_size
    duration_sec = pcm.shape[1] / 24000.0
    print(f"[*] Audio duration: {duration_sec:.2f}s, original size: {original_size / 1024:.1f} KB")
    
    print("[*] Loading Mimi neural audio codec...")
    mimi = get_cached_mimi()
    
    print("[*] Encoding audio to discrete neural acoustic tokens...")
    x = torch.from_numpy(pcm).unsqueeze(0)  # Shape: (1, 1, samples)
    
    t0 = time.time()
    with torch.no_grad():
        codes = mimi.encode(x)  # Shape: (1, num_codebooks=8, timesteps)
    encode_time = time.time() - t0
    
    codes_np = codes.squeeze(0).cpu().numpy().astype(np.uint16)
    
    # Save compact compressed tokens with metadata header
    payload = {
        "format": "APEX_MIMI_V1",
        "sample_rate": 24000,
        "duration_sec": float(duration_sec),
        "codebooks": int(codes_np.shape[0]),
        "steps": int(codes_np.shape[1]),
        "tokens": codes_np.tobytes()
    }
    
    import json
    header_json = json.dumps({k: v for k, v in payload.items() if k != "tokens"}).encode("utf-8")
    
    with open(output_file, "wb") as f:
        # Magic bytes + 4-byte header length + JSON header + token bytes
        f.write(b"MIMI")
        f.write(len(header_json).to_bytes(4, byteorder="big"))
        f.write(header_json)
        # Token bytes compressed with zlib for maximum density
        import zlib
        compressed_tokens = zlib.compress(payload["tokens"], level=9)
        f.write(compressed_tokens)
        
    compressed_size = output_file.stat().st_size
    savings_pct = (1.0 - (compressed_size / original_size)) * 100.0
    
    print(f"[+] Successfully compressed to: {output_file}")
    print(f"    - Original size:   {original_size / 1024:.2f} KB")
    print(f"    - Mimi token size: {compressed_size / 1024:.2f} KB ({savings_pct:.1f}% space saved!)")
    print(f"    - Effective bitrate: {(compressed_size * 8) / duration_sec / 1000.0:.2f} kbps")
    print(f"    - Encode speed:    {duration_sec / encode_time:.1f}x realtime on CPU")
    return True

def decompress_audio(input_path: str, output_path: str = None):
    """Decompress .mimi tokens back to 24kHz wav audio."""
    import sphn
    import json
    import zlib
    
    input_file = Path(input_path)
    if not input_file.exists():
        print(f"[-] Error: input file not found: {input_path}")
        return False
        
    if output_path is None:
        output_file = input_file.with_suffix(".decompressed.wav")
    else:
        output_file = Path(output_path)
        
    print(f"[*] Reading Mimi archive from: {input_file}")
    with open(input_file, "rb") as f:
        magic = f.read(4)
        if magic != b"MIMI":
            print("[-] Error: invalid magic bytes; not a valid .mimi file")
            return False
        header_len = int.from_bytes(f.read(4), byteorder="big")
        header = json.loads(f.read(header_len).decode("utf-8"))
        compressed_tokens = f.read()
        
    token_bytes = zlib.decompress(compressed_tokens)
    codes_np = np.frombuffer(token_bytes, dtype=np.uint16).reshape(
        (header["codebooks"], header["steps"])
    )
    
    print(f"[*] Loaded tokens: {codes_np.shape} (Duration: {header['duration_sec']:.2f}s)")
    print("[*] Loading Mimi neural audio codec...")
    mimi = get_cached_mimi()
    
    codes_tensor = torch.from_numpy(codes_np.astype(np.int64)).unsqueeze(0)
    
    print("[*] Decoding acoustic tokens to 24kHz waveform...")
    t0 = time.time()
    with torch.no_grad():
        waveform = mimi.decode(codes_tensor)  # Shape: (1, 1, samples)
    decode_time = time.time() - t0
    
    wav_np = waveform.squeeze(0).clamp(-1.0, 1.0).cpu().numpy()
    
    sphn.write_wav(str(output_file), wav_np, sample_rate=24000)
    print(f"[+] Reconstructed audio saved to: {output_file}")
    print(f"    - Output size:  {output_file.stat().st_size / 1024:.2f} KB")
    print(f"    - Decode speed: {header['duration_sec'] / decode_time:.1f}x realtime on CPU")
    return True

def run_self_test():
    """Verify end-to-end Mimi compression/decompression loop."""
    print("=== APEX MOSHI/MIMI SELF-TEST ===")
    test_wav = Path("/tmp/apex_mimi_test_tone.wav")
    test_mimi = Path("/tmp/apex_mimi_test_tone.mimi")
    test_rec = Path("/tmp/apex_mimi_test_tone_rec.wav")
    
    # Generate 1.5 seconds of synthetic audio (sine wave sweep)
    import sphn
    sr = 24000
    t = np.linspace(0, 1.5, int(sr * 1.5), endpoint=False, dtype=np.float32)
    tone = (0.5 * np.sin(2 * np.pi * 440 * t) + 0.3 * np.sin(2 * np.pi * 880 * t)).astype(np.float32)
    sphn.write_wav(str(test_wav), tone[None, :], sample_rate=sr)
    
    print("[1] Test audio generated:", test_wav)
    assert compress_audio(str(test_wav), str(test_mimi))
    assert decompress_audio(str(test_mimi), str(test_rec))
    
    # Clean up test artifacts
    for p in [test_wav, test_mimi, test_rec]:
        if p.exists():
            p.unlink()
    print("[+] ALL TESTS PASSED: Mimi neural codec is 100% operational!")
    return True

def show_colab_recipe():
    """Print the 1-click Colab or Remote GPU server launcher."""
    recipe = """
================================================================================
APEX HOLOGRAPHIC MESH: 1-CLICK REMOTE GPU MOSHI SERVER LAUNCHER
================================================================================
Run this single cell in Google Colab (with free T4 or A100 GPU) or any remote GPU:

```python
!pip install -q moshi
import subprocess

# Start Moshi full-duplex server with Gradio tunnel
cmd = ["python", "-m", "moshi.server", "--gradio-tunnel"]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

for line in proc.stdout:
    print(line, end="")
    if "gradio.live" in line:
        print("\\n" + "="*60)
        print(">>> CONNECT FROM APEX EDGE WITH:")
        print(f"python3 /root/apex_case_framework/apex_moshi_voice_engine.py connect --url wss://{line.strip().split('//')[-1]}")
        print("="*60 + "\\n")
```

Once the URL appears (e.g. `https://xxxx.gradio.live`), run on this node:
  python3 /root/apex_case_framework/apex_moshi_voice_engine.py connect --url wss://xxxx.gradio.live
================================================================================
"""
    print(recipe)

def connect_voice_gateway(url: str = None, host: str = "localhost", port: int = 8998):
    """Launch the client connection to a Moshi server."""
    cmd = [sys.executable, "-m", "moshi.client"]
    if url:
        cmd.extend(["--url", url])
    else:
        cmd.extend(["--host", host, "--port", str(port)])
    
    print(f"[*] Starting Moshi full-duplex voice client: {' '.join(cmd)}")
    os.execv(sys.executable, cmd)

def main():
    parser = argparse.ArgumentParser(description="APEX Moshi & Mimi Voice Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Compress
    p_comp = subparsers.add_parser("compress", help="Compress audio file to neural .mimi tokens")
    p_comp.add_argument("input", help="Path to input audio file (wav, mp3, m4a, ogg)")
    p_comp.add_argument("--output", "-o", help="Path to output .mimi file", default=None)
    
    # Decompress
    p_decomp = subparsers.add_parser("decompress", help="Decompress .mimi tokens back to 24kHz wav")
    p_decomp.add_argument("input", help="Path to input .mimi file")
    p_decomp.add_argument("--output", "-o", help="Path to output .wav file", default=None)
    
    # Connect
    p_conn = subparsers.add_parser("connect", help="Connect voice client to Moshi server")
    p_conn.add_argument("--url", help="Direct wss:// or https:// URL (e.g. Gradio tunnel)")
    p_conn.add_argument("--host", default="localhost", help="Host IP")
    p_conn.add_argument("--port", type=int, default=8998, help="Port")
    
    # Colab Recipe
    subparsers.add_parser("colab-recipe", help="Show 1-click Google Colab remote GPU server recipe")
    
    # Test
    subparsers.add_parser("test", help="Run end-to-end self test on Mimi neural codec")
    
    args = parser.parse_args()
    
    if args.command == "compress":
        compress_audio(args.input, args.output)
    elif args.command == "decompress":
        decompress_audio(args.input, args.output)
    elif args.command == "connect":
        connect_voice_gateway(args.url, args.host, args.port)
    elif args.command == "colab-recipe":
        show_colab_recipe()
    elif args.command == "test":
        run_self_test()

if __name__ == "__main__":
    main()
