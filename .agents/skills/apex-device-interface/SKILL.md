---
name: apex-device-interface
description: "Full hardware control: battery, sensors, camera, TTS, vibration, clipboard, and host command bridge on port 8990."
version: 1.0.0
status: active
---

# APEX Device Interface — Mega-Skill 3

**Full Hardware Control** — Complete Android device access via Termux/PRoot bridge.

## Composed Sub-Skills

| Sub-Skill | Role | Entry Point |
|-----------|------|-------------|
| apex-sovereign-supreme/device_access_supreme.py | Battery, sensors, camera, torch, TTS, vibration, clipboard, notifications, WiFi, GPS, host exec | `device_access_supreme.py` |
| apex-device-rpc | JSON-RPC/REST device bridge on 127.0.0.1:8990 | Service 8990 |

## Unified Capabilities (apex.capabilities/v1)

```yaml
schema: apex.capabilities/v1
repository: GlacierEQ/Pro-DOCTOR-STRANGE
mega_skill: apex-device-interface
capabilities:
  - id: device.telemetry
    description: Battery, thermal, RAM, storage, WiFi, CPU
    entrypoint: device_access_supreme.py system_info
    interface: cli|library|http|rpc
    outputs:
      - battery: {type: object, properties: {percentage: number, temperature: number, health: string, status: string, voltage: number, current: number, cycles: integer}}
      - storage: {type: object, properties: {sdcard: object, proot_root: object, termux_home: object}}
      - wifi: {type: object, properties: {ssid: string, ip: string, speed_mbps: number, rssi: number}}
      - ram: {type: object, properties: {total_kb: integer, available_kb: integer}}

  - id: device.sensors
    description: GPS, accelerometer, gyroscope, light, proximity
    entrypoint: device_access_supreme.py sensors
    interface: cli|library|http|rpc
    outputs:
      - gps: {type: object}
      - accelerometer: {type: object}
      - gyroscope: {type: object}
      - light: {type: object}
      - proximity: {type: object}

  - id: device.media
    description: Camera photo, torch, TTS, vibration, volume
    entrypoint: device_access_supreme.py media
    interface: cli|library|http|rpc
    inputs:
      - action: {type: string, enum: [camera_photo, torch_on, torch_off, tts_speak, vibrate, volume_get, volume_set]}
      - params: {type: object}
    outputs:
      - result: object

  - id: device.ui
    description: Notifications, toasts, clipboard
    entrypoint: device_access_supreme.py ui
    interface: cli|library|http|rpc
    inputs:
      - action: {type: string, enum: [notification, toast, clipboard_get, clipboard_set]}
      - params: {type: object}
    outputs:
      - result: object

  - id: device.network
    description: WiFi scan, cell info, host command bridge
    entrypoint: device_access_supreme.py network
    interface: cli|library|http|rpc
    inputs:
      - action: {type: string, enum: [wifi_scan, cell_info, exec_host_command]}
      - params: {type: object}
    outputs:
      - result: object

  - id: device.rpc
    description: JSON-RPC/REST on 127.0.0.1:8990
    entrypoint: apex-device-rpc service
    interface: rpc|http
    inputs:
      - method: {type: string}
      - params: {type: object}
    outputs:
      - result: object
```

## CLI Interface

```bash
apex-device <command> [options]

# Telemetry
apex-device telemetry                    # Full system info (battery, storage, wifi, ram)
apex-device telemetry --battery          # Battery only
apex-device telemetry --wifi             # WiFi only
apex-device telemetry --storage          # Storage only
apex-device telemetry --ram              # RAM only

# Sensors
apex-device sensors                      # All sensors
apex-device sensors --gps                # GPS location
apex-device sensors --accelerometer      # Accelerometer
apex-device sensors --gyroscope          # Gyroscope
apex-device sensors --light              # Light sensor
apex-device sensors --proximity          # Proximity sensor

# Media
apex-device media camera_photo           # Take photo
apex-device media torch_on               # Turn on flashlight
apex-device media torch_off              # Turn off flashlight
apex-device media tts_speak --text "..." # Text-to-speech
apex-device media vibrate --pattern 100,200,100
apex-device media volume_get
apex-device media volume_set --level 50

# UI
apex-device ui notification --title "..." --body "..." 
apex-device ui toast --message "..." --duration long
apex-device ui clipboard_get
apex-device ui clipboard_set --text "..."

# Network
apex-device network wifi_scan
apex-device network cell_info
apex-device network exec_host --command "ls -la"

# RPC
apex-device rpc --method device.telemetry --params '{}'
```

## Verification Gates

| Gate | Test | Pass Criteria |
|------|------|---------------|
| G1 | `telemetry` | Returns battery % (0-100), temp, health, storage GB, WiFi SSID, RAM |
| G2 | `sensors` | GPS returns lat/lon, accelerometer returns x/y/z |
| G3 | `media.camera_photo` | Returns photo path/base64 |
| G4 | `media.torch_on/off` | Flashlight toggles |
| G5 | `media.tts_speak` | Audio plays |
| G6 | `ui.notification` | System notification appears |
| G7 | `network.wifi_scan` | Returns AP list with RSSI |
| G8 | `rpc` | JSON-RPC call succeeds on port 8990 |