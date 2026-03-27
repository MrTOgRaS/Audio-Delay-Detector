<div align="center">

# 🎵 Audio Delay Detector v1.0
*The ultimate tool for precise audio synchronization & dubbing alignment.*

![Language](https://img.shields.io/badge/Language-Python_3.x-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows_|_macOS_|_Linux-cyan?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

<br>

[**🇬🇧 English**](#english) • [**🇹🇷 Türkçe**](#türkçe)

<br>

*(📸 Projenin ekran görüntüsünü buraya ekleyebilirsin: `![Ekran Görüntüsü](screenshot.png)`)*

</div>

---

<a name="english"></a>
## 🇬🇧 English

> **Audio Delay Detector** is a lightweight, modern desktop tool that calculates the delay (offset) between two audio files with **millisecond precision**. Designed for dubbing, post-production, and broadcast workflows, it eliminates the guesswork without needing to re-encode your files.

### ✨ Key Features
- ⏱️ **Millisecond Precision:** Detects even sub-frame audio offsets perfectly.
- 🧠 **Smart Analysis Engines:** Powered by multiple advanced DSP algorithms (GCC-PHAT, Micro-Rhythm RMS, Onset Extraction).
- 🎞️ **Wide Format Support:** Works directly with MKV, MP4, AC3, EAC3, DTS, MP3, FLAC, AAC, WAV, and more *(via FFmpeg)*.
- 🎯 **Manual & Auto Modes:** Features "Smart Chunking" for long movies (analyzes only the most active parts to save RAM) and ultra-precise "Micro-Rhythm" mapping for short manual selections.
- 🌓 **Modern UI:** A clean, dark-themed Tkinter dashboard.
- 💾 **Persistent Configurations:** Remembers your FFmpeg paths and language preferences automatically.
- 🌐 **Bilingual:** Switch between English and Turkish seamlessly.

### ⚙️ Analysis Engines
| Engine | Best For | Description |
|---|---|---|
| **GCC-PHAT Segmented** | Identical Sources | Phase Transform cross-correlation. Great for exact matches. |
| **Envelope XCorr** | Different Languages | RMS energy envelope correlation. Perfect for dubbing. |
| **Multi-Feature** | Complex Audio | Combines Onset, HPSS, and Chromagram features. |
| **⭐ Smart Auto** | Full Movies | Smart chunking + Syllable Rhythm matching. Super fast and accurate. |

### 🛠️ Installation & Usage

**1. Download the Portable Release:**
Go to the [Releases](../../releases) tab and download `AudioDelayDetector_v1.0.exe`.

**2. Running from Source:**
Make sure you have [FFmpeg](https://ffmpeg.org/download.html) installed on your system.
```bash
# Clone the repository
git clone [https://github.com/MrTOgRaS/AudioDelayDetector.git](https://github.com/MrTOgRaS/AudioDelayDetector.git)
cd AudioDelayDetector

# Install required Python libraries
pip install numpy scipy librosa pydub soundfile

# Run the app
python main.py

<div align="center">

# 🎵 Audio Delay Detector v1.0
*The ultimate tool for precise audio synchronization & dubbing alignment.*

![Language](https://img.shields.io/badge/Language-Python_3.x-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows_|_macOS_|_Linux-cyan?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

<br>

[**🇬🇧 English**](#english) • [**🇹🇷 Türkçe**](#türkçe)

<br>

*(📸 Projenin ekran görüntüsünü buraya ekleyebilirsin: `![Ekran Görüntüsü](screenshot.png)`)*

</div>

---

<a name="english"></a>
## 🇬🇧 English

> **Audio Delay Detector** is a lightweight, modern desktop tool that calculates the delay (offset) between two audio files with **millisecond precision**. Designed for dubbing, post-production, and broadcast workflows, it eliminates the guesswork without needing to re-encode your files.

### ✨ Key Features
- ⏱️ **Millisecond Precision:** Detects even sub-frame audio offsets perfectly.
- 🧠 **Smart Analysis Engines:** Powered by multiple advanced DSP algorithms (GCC-PHAT, Micro-Rhythm RMS, Onset Extraction).
- 🎞️ **Wide Format Support:** Works directly with MKV, MP4, AC3, EAC3, DTS, MP3, FLAC, AAC, WAV, and more *(via FFmpeg)*.
- 🎯 **Manual & Auto Modes:** Features "Smart Chunking" for long movies (analyzes only the most active parts to save RAM) and ultra-precise "Micro-Rhythm" mapping for short manual selections.
- 🌓 **Modern UI:** A clean, dark-themed Tkinter dashboard.
- 💾 **Persistent Configurations:** Remembers your FFmpeg paths and language preferences automatically.
- 🌐 **Bilingual:** Switch between English and Turkish seamlessly.

### ⚙️ Analysis Engines
| Engine | Best For | Description |
|---|---|---|
| **GCC-PHAT Segmented** | Identical Sources | Phase Transform cross-correlation. Great for exact matches. |
| **Envelope XCorr** | Different Languages | RMS energy envelope correlation. Perfect for dubbing. |
| **Multi-Feature** | Complex Audio | Combines Onset, HPSS, and Chromagram features. |
| **⭐ Smart Auto** | Full Movies | Smart chunking + Syllable Rhythm matching. Super fast and accurate. |

### 🛠️ Installation & Usage

**1. Download the Portable Release:**
Go to the [Releases](../../releases) tab and download `AudioDelayDetector_v1.0.exe`.

**2. Running from Source:**
Make sure you have [FFmpeg](https://ffmpeg.org/download.html) installed on your system.
```bash
# Clone the repository
git clone [https://github.com/MrTOgRaS/AudioDelayDetector.git](https://github.com/MrTOgRaS/AudioDelayDetector.git)
cd AudioDelayDetector

# Install required Python libraries
pip install numpy scipy librosa pydub soundfile

# Run the app
python main.py