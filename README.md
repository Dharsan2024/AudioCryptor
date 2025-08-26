# AudioCryptor-Advanced-Audio-Steganography-App

AudioCryptor is a desktop application developed to provide a secure and user-friendly environment for hiding and extracting confidential information inside audio files. 
---

## ✨ Features

### 🎨 Modern GUI Interface

* Sleek dark theme built with Tkinter + custom styled widgets
* Tabbed interface for encoding, decoding, and settings
* Password generator with clipboard copy functionality
* Capacity checker to show how much data can be hidden in audio
* Save encoded audio files to custom locations
* Real-time progress indicators during processing
* Clipboard auto-clear for enhanced security

---

### 🔒 Security Features

* **AES-256 GCM Encryption**: Strong authenticated encryption standard
* **Secure Key Derivation**: PBKDF2-HMAC-SHA256 with random salt (200k iterations)
* **Key Management**: Passwords never stored; safe clipboard copy for generated keys
* **No Hardcoded Keys**: All keys are user-provided or securely generated
* **Bit Scattering**: Random distribution of hidden bits for steganalysis resistance
* **Data Integrity**: Custom header with CRC32 check prevents corruption

---

### 📁 File Support

* **Currently Supported**: WAV (lossless PCM, 16-bit)
* **Future Support** (when `ffmpeg` is available): MP3, FLAC, M4A, OGG
* Output audio files saved in chosen directory
* Capacity calculation ensures safe embedding without exceeding limits

---

### 🛡️ Security Considerations

* Messages are always encrypted before being embedded
* Keys are never embedded in audio files
* All encryption operations use secure random salt + nonces
* AES-GCM authentication tags prevent message tampering
* Error handling prevents leaking sensitive information

---

## 📋 Requirements

### Python Dependencies

The application requires the following Python packages:

* `tkinter` - GUI framework (built into Python)
* `numpy` - Audio data processing
* `cryptography` - AES-GCM encryption/decryption
* `pydub` - Audio format conversion (requires ffmpeg)
* `simpleaudio` - Cross-platform audio playback

### System Dependencies

* **ffmpeg** → Required for MP3, M4A, OGG, and FLAC support
* **Audio Drivers** → Needed for playback via simpleaudio

⚠️ Current Limitation:

* Without **ffmpeg** → Only WAV files supported
* Without **simpleaudio** → Audio playback won’t work

---

## 🚀 Quick Start

### Installation

1. Clone or download the project files
2. Install required dependencies:

   ```bash
   pip install numpy cryptography pydub simpleaudio
   ```
3. (Optional) Install **ffmpeg** for extended audio format support

### Running the Application

```bash
python main.py
```

---
