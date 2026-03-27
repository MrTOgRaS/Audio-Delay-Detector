<div align="center">

# 🎵 Audio Delay Detector v1.0
*The ultimate tool for precise audio synchronization & dubbing alignment.*

![Language](https://img.shields.io/badge/Language-Python_3.x-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows_|_macOS_|_Linux-cyan?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

<br>

[**🇬🇧 English**](#english) • [**🇹🇷 Türkçe**](#türkçe)

<br>

*(📸 Projenin ekran görüntüsünü buraya ekleyebilirsiniz: `![Ekran Görüntüsü](screenshot.png)`)*

</div>

---

<a name="english"></a>
## 🇬🇧 English

> **Audio Delay Detector** is a lightweight, modern desktop tool that calculates the delay (offset) between two audio files with **millisecond precision**. Designed for dubbing, post-production, and broadcast workflows, it eliminates the guesswork without needing to re-encode your files.

### ✨ Key Features
- ⏱️ **Millisecond Precision:** Detects even sub-frame audio offsets perfectly.
- 🧠 **Smart Analysis Engines:** Powered by multiple advanced DSP algorithms (GCC-PHAT, Micro-Rhythm RMS, Onset Extraction).
- 🎞️ **Wide Format Support:** Works directly with MKV, MP4, AC3, EAC3, DTS, MP3, FLAC, AAC, WAV, and more *(via FFmpeg)*.
- 🎯 **Manual & Auto Modes:** Features "Smart Chunking" for long movies and ultra-precise "Micro-Rhythm" mapping for short manual selections.
- 🌓 **Modern UI:** A clean, dark-themed Tkinter dashboard.
- 💾 **Persistent Configurations:** Remembers your FFmpeg paths and language preferences automatically.

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
```

<div align="center">

# 🎵 Audio Delay Detector v1.0
*Milisaniye hassasiyetinde ses senkronizasyonu ve dublaj hizalama için profesyonel çözüm.*

![Dil](https://img.shields.io/badge/Dil-Python_3.x-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows_|_macOS_|_Linux-cyan?style=for-the-badge)
![Lisans](https://img.shields.io/badge/Lisans-MIT-green?style=for-the-badge)

<br>

![Audio Delay Detector Banner](https://raw.githubusercontent.com/MrTOgRaS/AudioDelayDetector/main/assets/banner_tr.png)

</div>

---

## 📝 Proje Açıklaması

**Audio Delay Detector**, iki ses dosyası arasındaki zaman farkını (offset) **milisaniye hassasiyetinde** hesaplayan hafif ve modern bir masaüstü aracıdır. Dublaj, post-prodüksiyon ve yayın iş akışları için tasarlanmıştır. Dosyalarınızı yeniden kodlamanıza (re-encode) gerek kalmadan saniyeler içinde kesin sonucu verir.

### ✨ Öne Çıkan Özellikler
- ⏱️ **Milisaniye Hassasiyeti:** Kare altı (sub-frame) ses gecikmelerini bile kusursuz şekilde tespit eder.
- 🧠 **Akıllı Analiz Motorları:** Gelişmiş DSP algoritmaları (GCC-PHAT, Mikro-Ritim RMS, Onset Vuruş Çıkarımı) ile güçlendirilmiştir.
- 🎞️ **Geniş Format Desteği:** MKV, MP4, AC3, EAC3, DTS, MP3, FLAC, AAC, WAV ve daha fazlasıyla doğrudan çalışır.
- 🎯 **Manuel ve Otomatik Modlar:** Uzun filmler için "Akıllı Kesit" ve kısa seçimler için ultra hassas "Mikro-Ritim" eşleştirme özelliği.
- 🌓 **Modern Arayüz:** Şık ve temiz, koyu tema (Dark Mode) Tkinter paneli.
- 💾 **Kalıcı Yapılandırmalar:** FFmpeg yollarınızı ve dil tercihlerinizi otomatik olarak hatırlar.

### ⚙️ Analiz Motorları
| Motor | En İyi Kullanım | Açıklama |
|---|---|---|
| **GCC-PHAT Segmented** | Aynı Kaynaklar | Faz dönüşümlü çapraz korelasyon. Tam eşleşmeler için idealdir. |
| **Envelope XCorr** | Farklı Diller | RMS enerji zarfı korelasyonu. Dublaj senkronizasyonu için mükemmeldir. |
| **Multi-Feature** | Karmaşık Sesler | Onset, HPSS ve Chromagram özelliklerini birleştirir. |
| **⭐ Akıllı Otomatik** | Tam Filmler | Akıllı kesitleme + Hece Ritim eşleştirme. Çok hızlı ve doğru. |

### 🛠️ Kurulum ve Kullanım

**1. Hazır Sürümü İndirin:**
Sağ taraftaki **Releases** sekmesine gidin ve `AudioDelayDetector_v1.0.exe` dosyasını indirin.

**2. Kaynak Koddan Çalıştırma:**
Sisteminizde [FFmpeg](https://ffmpeg.org/download.html) kurulu olduğundan emin olun.

```bash
# Repoyu klonlayın
git clone [https://github.com/MrTOgRaS/AudioDelayDetector.git](https://github.com/MrTOgRaS/AudioDelayDetector.git)
cd AudioDelayDetector

# Gerekli Python kütüphanelerini yükleyin
pip install numpy scipy librosa pydub soundfile

# Uygulamayı çalıştırın
python main.py

