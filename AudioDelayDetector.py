#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════╗
║   Audio Delay Detector  v1.0        ║
║   Developer   : MrTOgRaS            ║
║   WEB         : www.mrtogras.com    ║
║   Mail        : destek@mrtogras.com ║
╚══════════════════════════════════════╝

7 Motor  ×  3 Mod  =  21 Kombinasyon
─────────────────────────────────────
Motorlar:
  1. GCC-PHAT Segmented
  2. Envelope XCorr
  3. NumPy FFT XCorr
  4. SciPy XCorr
  5. Çoklu Özellik (Onset+HPSS+Chroma)
  6. 2 Aşamalı (RMS + İnce FFT)
  7. ⭐ Otomatik Akıllı Analiz (VAD + Enerji + HPSS + Onset + Drift)

Modlar:
  🎬 Eski Filmler  — konuşma bastırma ON (300-3500 Hz sıfırlanır)
  🎨 Animasyonlar  — hafif konuşma bastırma (500-3000 Hz)
  🎥 Yeni Filmler  — ön-işleme yok (M&E track paylaşılır)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import warnings
import datetime
import os
import json
import webbrowser
import subprocess
import tempfile
import shutil

import numpy as np
from scipy import signal

# ── Opsiyonel kütüphaneler ────────────────────────────────────────────────────
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

# ══════════════════════════════════════════════════════════════════════════════
#  ÇOK DİLLİ SİSTEM (EN / TR)
# ══════════════════════════════════════════════════════════════════════════════
STRINGS = {
    "tr": {
        # Başlık
        "app_title": "🎵  Audio Delay Detector  v1.0  —  MrTOgRaS",
        "header_title": "🎵  Audio Delay Detector",
        "header_version": " v1.0",
        # Dosya kartları
        "main_audio": "🔊  Ana Ses / Video",
        "main_audio_sub": "Film dosyası (MKV/MP4) veya ses dosyası",
        "dub_audio": "🎤  Dublaj Ses",
        "dub_audio_sub": "Gecikme tespiti yapılacak dosya",
        "file_not_selected": "Dosya seçilmedi",
        "btn_select": "📂 Seç",
        # Motor & Mod
        "engine_label": "⚙️  Motor :",
        "mode_old": "Eski Filmler",
        "mode_anim": "Animasyonlar",
        "mode_new": "Yeni Filmler",
        # Butonlar
        "btn_start": "▶   Analizi Başlat",
        "btn_cancel": "⏹  İptal",
        "btn_analyzing": "⏳  Analiz ediliyor...",
        "btn_about": "ℹ️  Hakkında",
        "btn_ffmpeg": "⚙️  FFmpeg Ayarları",
        "btn_lang": "🌐 EN",
        # Sonuç kutuları
        "results_title": "📊  Analiz Sonuçları",
        "res_delay": "Gecikme (ms)",
        "res_format": "Süre Formatı",
        "res_direction": "Gecikme Yönü",
        "res_engine": "Kullanılan Motor",
        # Log
        "log_title": "📋  Durum Logu",
        # FFmpeg
        "ffmpeg_set": "✅  FFmpeg  →  ",
        "ffmpeg_not_set": "⚠️  FFmpeg yolu ayarlanmadı — AC3/EAC3/DTS/MKV için gerekli  [ ⚙️ FFmpeg Ayarları ]",
        "ffmpeg_settings_title": "FFmpeg Ayarları",
        "ffmpeg_header": "⚙️  FFmpeg Yolu Ayarları",
        "ffmpeg_desc": "AC3, EAC3, DTS, MP3, AAC, MKV formatları için FFmpeg gereklidir.",
        "ffmpeg_path_label": "ffmpeg.exe  yolu :",
        "ffprobe_path_label": "ffprobe.exe yolu :",
        "ffmpeg_tip": "💡  Genellikle FFmpeg şu konumdadır:\n     C:\\ffmpeg\\bin\\ffmpeg.exe  ve  C:\\ffmpeg\\bin\\ffprobe.exe",
        "ffmpeg_save": "  Kaydet & Kapat  ",
        "ffmpeg_saved": "✅  FFmpeg ayarları kaydedildi.",
        "ffmpeg_save_err": "⚠️  Config kaydedilemedi: ",
        # Dosya seçiciler
        "pick_main": "Ana Ses / Video Seç",
        "pick_dub": "Dublaj Ses Seç",
        "pick_ffmpeg": " Seç",
        "main_selected": "Ana ses seçildi: ",
        "dub_selected": "Dublaj ses seçildi: ",
        # Uyarılar
        "warn_no_main": "Lütfen Ana Ses / Video dosyasını seçin!",
        "warn_no_dub": "Lütfen Dublaj Ses dosyasını seçin!",
        "warn_title": "Uyarı",
        # Bağımlılık
        "dep_check": "─── Bağımlılık Kontrolü ─────────────────────────────",
        "dep_ready": "Hazır — 7 motor × 3 mod. Dosya seçin ve başlatın.",
        "dep_librosa_ok": "✅  librosa",
        "dep_librosa_fail": "❌  librosa  →  pip install librosa",
        "dep_pydub_ok": "✅  pydub",
        "dep_pydub_fail": "⚠️  pydub  →  pip install pydub",
        "dep_sf_ok": "✅  soundfile",
        "dep_sf_fail": "⚠️  soundfile  →  pip install soundfile",
        "dep_ffmpeg_ok": "✅  FFmpeg  →  {}",
        "dep_ffmpeg_fail": "⚠️  FFmpeg  →  ⚙️ FFmpeg Ayarları butonundan yolu girin",
        # Analiz
        "loading_main": "Ana ses yükleniyor...",
        "loading_dub": "Dublaj ses yükleniyor...",
        "diff_sr": "⚠️  Farklı sample rate ({} ≠ {}) → yeniden örnekleniyor...",
        "resample_done": "  Yeniden örnekleme tamamlandı.",
        "no_preprocess": "  ✅ Sinyal ön-işleme YOK — ham sinyal analiz ediliyor",
        "analysis_done": "✅  Analiz tamamlandı!",
        "delay_label": "📌  Gecikme       :  {:+d} ms",
        "format_label": "📌  Süre formatı  :  {}",
        "dir_label": "📌  Yön           :  {}",
        "sample_label": "📌  Örnek farkı   :  {:,} @ {} Hz",
        "dir_audio2_late": "◀  Ses 2 gecikiyor",
        "dir_audio1_late": "Ses 1 gecikiyor ▶",
        "dir_sync": "✅  Senkronize",
        "dir_short_a2": "◀ Ses 2 Geride",
        "dir_short_a1": "Ses 1 Geride ▶",
        "dir_short_sync": "✅ Senkron",
        "cancel_msg": "⛔  Analiz iptal ediliyor...",
        "cancelled": "⛔  Analiz iptal edildi.",
        "error": "❌  Hata: ",
        "unknown_engine": "Bilinmeyen motor: ",
        # Motorlar
        "eng_gcc": "── Motor: GCC-PHAT Segmented ──",
        "eng_env": "── Motor: Envelope XCorr ──",
        "eng_numpy": "── Motor: NumPy FFT XCorr ──",
        "eng_scipy": "── Motor: SciPy XCorr ──",
        "eng_multi": "── Motor: Çoklu Özellik (Onset+HPSS+Chroma) ──",
        "eng_two": "── Motor: 2 Aşamalı (RMS + İnce FFT) ──",
        "eng_auto_title": "⭐ Motor: Otomatik Akıllı Analiz",
        "eng_auto_raw": "  Ham sinyal — hiçbir ön-işleme yok",
        # Motor detayları
        "segment": "  Segment {}/{}:  {:+d} ms  güven={:.1f}",
        "segments_agree": "  ✅ {}/{} segment uyumlu → {:+d} ms",
        "envelope_result": "  Envelope: {:+d} ms  ({} frame × {:.0f} ms)",
        "envelope_offset": "  Envelope: {:+d} ms  ({} frame × {:.0f} ms + {:+.0f} ms offset)",
        "numpy_result": "  NumPy FFT: {:+d} ms",
        "scipy_result": "  SciPy: {:+d} ms  (±{:.0f}s aralığında)",
        "fine_tune": "── İnce ayar (odaklanmış FFT) ──",
        "fine_result": "  İnce ayar: {:+d} ms  (arama: {:+.0f} ± {:.0f} ms)",
        "fine_empty": "  ⚠️ İnce ayar bölgesi boş — kaba sonuç kullanılıyor",
        "fine_drift": "  ⚠️ İnce ayar sapma → kaba: {:+d} ms",
        "methods_agree": "  ✅ {}/{} yöntem uyumlu → {:+d} ms",
        "summary": "  ─ Özet ─",
        "onset_corr": "  ─ Onset korelasyonu ─",
        "hpss_perc": "  ─ HPSS perküsif onset ─",
        "perc_rms": "  ─ Perküsif RMS zarfı ─",
        "perc_rms_fail": "    Perküsif RMS başarısız: ",
        "rms_env": "  ─ RMS zarfı (100ms) ─",
        "chromagram": "  ─ Chromagram ─",
        "no_librosa_flux": "  ⚠️ librosa yok, spektral akı",
        "coarse_label": "  Aşama 1: Kaba hizalama (RMS zarfı)",
        "coarse_result": "  Kaba: {:+d} ms  ({} frame × {:.0f} ms)",
        "fine_phase2": "  Aşama 2: İnce ayar (odaklanmış FFT)",
        "fine_ok": "  ✅ Sonuç: {:+d} ms",
        # Auto motor
        "vad_title": "─── Yöntem 1: VAD Sessizlik Deseni ───",
        "vad_desc": "  Konuşmanın zamanlamasını analiz ediyor (dile bağımsız)",
        "vad_result": "  VAD deseni: {:+d} ms  (güvenilirlik: {:.1f})",
        "env_title": "─── Yöntem 2: Makro Enerji Zarfı ───",
        "env_result": "  Enerji zarfı: {:+d} ms  (güvenilirlik: {:.1f})",
        "hpss_title": "─── Yöntem 3: HPSS Perküsif ───",
        "hpss_result": "  HPSS perküsif: {:+d} ms  (güvenilirlik: {:.1f})",
        "hpss_fail": "  ⚠️ HPSS başarısız: ",
        "hpss_no_librosa": "  ⚠️ librosa yok — HPSS atlanıyor",
        "onset_title": "─── Yöntem 4: Onset Zamanlaması ───",
        "onset_result": "  Onset: {:+d} ms  (güvenilirlik: {:.1f})",
        "onset_fail": "  ⚠️ Onset başarısız: ",
        "consensus": "📊 Konsensüs Analizi",
        "no_results": "❌ Hiçbir yöntem sonuç üretemedi!",
        "methods_disagree": "  ⚠️ Yöntemler uyuşmuyor — en güvenilir alınıyor",
        "drift_title": "─── Drift Kontrolü (enerji zarfı) ───",
        "drift_start": "Başlangıç",
        "drift_mid": "Orta",
        "drift_end": "Son",
        "drift_max": "  Max fark: {:.1f} ms",
        "drift_detected": "  ⛔ DRİFT TESPİT EDİLDİ!",
        "drift_amount": "  Film boyunca {:.0f} ms kayma.",
        "drift_cause": "  Muhtemelen fps farkı (23.976 vs 25 fps).",
        "drift_fix": "  Tek delay senkronize EDEMEZ.",
        "drift_solution": "  Çözüm: fps eşleştir veya time-stretch uygula.",
        "drift_none": "  ✅ Drift yok (fark: {:.0f} ms)",
        "sync_warn_title": "  ⛔ SENKRONİZASYON UYARISI",
        "sync_warn_desc": "  Yöntemler tutarsız sonuçlar veriyor.",
        "sync_warn_hint": "  Bu ses basit delay ile senkronlanamayabilir.",
        "sync_warn_reasons": "  Olası nedenler:",
        "sync_warn_r1": "    • Farklı frame rate (23.976 vs 25 fps)",
        "sync_warn_r2": "    • Farklı kaynak/master kullanılmış",
        "sync_warn_r3": "    • Ses dosyaları aynı içeriğe ait değil",
        "final_result": "📌 Final sonuç: {:+d} ms",
        "drift_active": "  ⚠️ Drift uyarısı aktif — sonuç güvenilir olmayabilir",
        # Yükleme
        "load_video": "  📦 {} — FFmpeg subprocess ile çıkarılıyor...",
        "load_video_reason": "video dosyası",
        "load_large_reason": "büyük dosya ({:.1f} GB)",
        "load_ffmpeg_ok": "  ✅ FFmpeg subprocess  ({} Hz)",
        "load_ffmpeg_fail": "  ⚠️ FFmpeg subprocess başarısız, diğer yükleyiciler deneniyor...",
        "load_ffmpeg_err": "  ⚠️ FFmpeg subprocess hata: ",
        "load_ffmpeg_timeout": "  ⚠️ FFmpeg zaman aşımı (120s)",
        "load_ffmpeg_extract_err": "  ⚠️ FFmpeg extract hata: ",
        "load_pydub_ok": "  ✅ pydub/FFmpeg  ({} Hz)",
        "load_pydub_fail": "  ⚠️ pydub başarısız: ",
        "load_sf_ok": "  ✅ soundfile  ({} Hz)",
        "load_sf_fail": "  ⚠️ soundfile başarısız: ",
        "load_librosa_ok": "  ✅ librosa  ({} Hz)",
        "load_none": "Hiçbir ses yükleyici çalışmadı!\npip install pydub soundfile librosa  +  FFmpeg kurun.",
        "first_min": "  Ana ses: ilk {} dk ({:.0f}s)",
        "dub_min": "  Dublaj: ilk {} dk ({:.0f}s)",
        "sample_info": "  → {:.2f} sn  |  {} Hz  |  {:,} örnek",
        # Manuel Arama
        "manual_title": "🎯  Manuel Arama",
        "manual_desc": "Ana seste belirli bir bölümü seç, dublajda ±10 dk aralığında arasın",
        "manual_start": "Başlangıç :",
        "manual_end": "Bitiş :",
        "manual_range": "Arama aralığı (dk) :",
        "manual_btn": "🎯  Manuel Ara",
        "manual_searching": "🎯  Arıyor...",
        "manual_enable": "Manuel Aramayı Aç",
        "manual_log_start": "─── Manuel Arama ───────────────────────────────",
        "manual_log_range": "  Ana ses bölümü: {} → {}",
        "manual_log_search": "  Dublajda arama: ±{} dk aralığında",
        "manual_log_extract": "  Ana sesten {} sn kesit çıkarılıyor...",
        "manual_log_dub_range": "  Dublajdan {} sn arama bölgesi çıkarılıyor...",
        "manual_log_corr": "  Korelasyon hesaplanıyor...",
        "manual_log_result": "  ✅ Bulunan gecikme: {:+d} ms",
        "manual_log_pos": "  Eşleşen konum (dublajda): {}",
        "manual_warn_time": "Geçersiz zaman formatı! sa:dk:sn şeklinde girin (örn: 0:05:30)",
        "manual_warn_range": "Bitiş zamanı başlangıçtan büyük olmalı!",
        "manual_tip_short": "💡 İpucu: Farklı dillerde 30 saniyeden kısa süre seçmek benzerlik yanılmalarına yol açabilir.",
        "manual_loading_main": "Ana sesten hedef bölge alınıyor...",
        "manual_no_audio": "⚠️ HATA: Seçtiğiniz bölgede ses yok!",
        "manual_loading_dub": "Dublajdan geniş arama bölgesi alınıyor...",
        "manual_micro_rhythm": "Mikro-Ritim Haritaları (1ms Çözünürlük) çıkarılıyor...",
        "manual_dir_left": "◀ Sola Çek (Dublaj Geç)",
        "manual_dir_right": "Sağa İtele (Dublaj Erken) ▶",
        "manual_dir_sync": "✅ Senkronize",
        "analysis_rms_extract": "Ses şiddet haritaları (RMS Envelope) çıkarılıyor...",
        # Desteklenen formatlar
        "fmt_all": "Tüm Desteklenen",
        "fmt_video": "Video Dosyaları",
        "fmt_audio": "Ses Dosyaları",
        "fmt_any": "Tüm Dosyalar",
        # Hakkında
        "about_title": "Hakkında",
        "about_version": "Versiyon 1.0  —  MrTOgRaS",
        "about_dev": "Geliştirici",
        "about_dev_val": "Murat Oğraş",
        "about_web_btn": "🌐  Web Sitesi",
        "about_github_btn": "🐙  GitHub Page",
        "about_mail_btn": "📧  E-Posta",
        "about_libs": "Kullanılan Kütüphaneler",
        "about_formats": "Desteklenen Formatlar",
        "about_combo": "7 Motor  ×  3 Mod  =  21 Kombinasyon",
        "about_modes_old": "🎬 Eski Filmler (konuşma bastırma ON)",
        "about_modes_anim": "🎨 Animasyonlar (hafif bastırma)",
        "about_modes_new": "🎥 Yeni Filmler (bastırma yok)",
        "about_close": "  Kapat  ",
        "about_mit": "📜  MIT Lisansı",
        "about_info": "ℹ️  Program Bilgileri",
        "about_info_title": "Program Bilgileri",
        "about_donate": "❤️  Destek Ol",
        "about_engines": "Motorlar",
        "about_modes": "Modlar",
        "engine_smart_rhythm": "⭐ Akıllı Ritim (RMS)",
        # MIT Lisansı
        "mit_title": "MIT Lisansı",
    },
    "en": {
        # Title
        "app_title": "🎵  Audio Delay Detector  v1.0  —  MrTOgRaS",
        "header_title": "🎵  Audio Delay Detector",
        "header_version": " v1.0",
        # File cards
        "main_audio": "🔊  Main Audio / Video",
        "main_audio_sub": "Movie file (MKV/MP4) or audio file",
        "dub_audio": "🎤  Dubbed Audio",
        "dub_audio_sub": "File for delay detection",
        "file_not_selected": "No file selected",
        "btn_select": "📂 Browse",
        # Engine & Mode
        "engine_label": "⚙️  Engine :",
        "mode_old": "Old Films",
        "mode_anim": "Animations",
        "mode_new": "New Films",
        # Buttons
        "btn_start": "▶   Start Analysis",
        "btn_cancel": "⏹  Cancel",
        "btn_analyzing": "⏳  Analyzing...",
        "btn_about": "ℹ️  About",
        "btn_ffmpeg": "⚙️  FFmpeg Settings",
        "btn_lang": "🌐 TR",
        # Result boxes
        "results_title": "📊  Analysis Results",
        "res_delay": "Delay (ms)",
        "res_format": "Time Format",
        "res_direction": "Delay Direction",
        "res_engine": "Engine Used",
        # Log
        "log_title": "📋  Status Log",
        # FFmpeg
        "ffmpeg_set": "✅  FFmpeg  →  ",
        "ffmpeg_not_set": "⚠️  FFmpeg path not set — required for AC3/EAC3/DTS/MKV  [ ⚙️ FFmpeg Settings ]",
        "ffmpeg_settings_title": "FFmpeg Settings",
        "ffmpeg_header": "⚙️  FFmpeg Path Settings",
        "ffmpeg_desc": "FFmpeg is required for AC3, EAC3, DTS, MP3, AAC, MKV formats.",
        "ffmpeg_path_label": "ffmpeg.exe  path :",
        "ffprobe_path_label": "ffprobe.exe path :",
        "ffmpeg_tip": "💡  FFmpeg is usually located at:\n     C:\\ffmpeg\\bin\\ffmpeg.exe  and  C:\\ffmpeg\\bin\\ffprobe.exe",
        "ffmpeg_save": "  Save & Close  ",
        "ffmpeg_saved": "✅  FFmpeg settings saved.",
        "ffmpeg_save_err": "⚠️  Could not save config: ",
        # File pickers
        "pick_main": "Select Main Audio / Video",
        "pick_dub": "Select Dubbed Audio",
        "pick_ffmpeg": " Select",
        "main_selected": "Main audio selected: ",
        "dub_selected": "Dubbed audio selected: ",
        # Warnings
        "warn_no_main": "Please select the Main Audio / Video file!",
        "warn_no_dub": "Please select the Dubbed Audio file!",
        "warn_title": "Warning",
        # Dependencies
        "dep_check": "─── Dependency Check ─────────────────────────────",
        "dep_ready": "Ready — 7 engines × 3 modes. Select files and start.",
        "dep_librosa_ok": "✅  librosa",
        "dep_librosa_fail": "❌  librosa  →  pip install librosa",
        "dep_pydub_ok": "✅  pydub",
        "dep_pydub_fail": "⚠️  pydub  →  pip install pydub",
        "dep_sf_ok": "✅  soundfile",
        "dep_sf_fail": "⚠️  soundfile  →  pip install soundfile",
        "dep_ffmpeg_ok": "✅  FFmpeg  →  {}",
        "dep_ffmpeg_fail": "⚠️  FFmpeg  →  Set path in ⚙️ FFmpeg Settings",
        # Analysis
        "loading_main": "Loading main audio...",
        "loading_dub": "Loading dubbed audio...",
        "diff_sr": "⚠️  Different sample rate ({} ≠ {}) → resampling...",
        "resample_done": "  Resampling complete.",
        "no_preprocess": "  ✅ No signal preprocessing — analyzing raw signal",
        "analysis_done": "✅  Analysis complete!",
        "delay_label": "📌  Delay         :  {:+d} ms",
        "format_label": "📌  Time format   :  {}",
        "dir_label": "📌  Direction     :  {}",
        "sample_label": "📌  Sample diff   :  {:,} @ {} Hz",
        "dir_audio2_late": "◀  Audio 2 is late",
        "dir_audio1_late": "Audio 1 is late ▶",
        "dir_sync": "✅  Synchronized",
        "dir_short_a2": "◀ Audio 2 Behind",
        "dir_short_a1": "Audio 1 Behind ▶",
        "dir_short_sync": "✅ In Sync",
        "cancel_msg": "⛔  Cancelling analysis...",
        "cancelled": "⛔  Analysis cancelled.",
        "error": "❌  Error: ",
        "unknown_engine": "Unknown engine: ",
        # Engines
        "eng_gcc": "── Engine: GCC-PHAT Segmented ──",
        "eng_env": "── Engine: Envelope XCorr ──",
        "eng_numpy": "── Engine: NumPy FFT XCorr ──",
        "eng_scipy": "── Engine: SciPy XCorr ──",
        "eng_multi": "── Engine: Multi Feature (Onset+HPSS+Chroma) ──",
        "eng_two": "── Engine: 2-Pass (RMS + Fine FFT) ──",
        "eng_auto_title": "⭐ Engine: Automatic Smart Analysis",
        "eng_auto_raw": "  Raw signal — no preprocessing",
        # Engine details
        "segment": "  Segment {}/{}:  {:+d} ms  conf={:.1f}",
        "segments_agree": "  ✅ {}/{} segments agree → {:+d} ms",
        "envelope_result": "  Envelope: {:+d} ms  ({} frames × {:.0f} ms)",
        "envelope_offset": "  Envelope: {:+d} ms  ({} frames × {:.0f} ms + {:+.0f} ms offset)",
        "numpy_result": "  NumPy FFT: {:+d} ms",
        "scipy_result": "  SciPy: {:+d} ms  (±{:.0f}s range)",
        "fine_tune": "── Fine tuning (focused FFT) ──",
        "fine_result": "  Fine tune: {:+d} ms  (search: {:+.0f} ± {:.0f} ms)",
        "fine_empty": "  ⚠️ Fine tune region empty — using coarse result",
        "fine_drift": "  ⚠️ Fine tune drift → coarse: {:+d} ms",
        "methods_agree": "  ✅ {}/{} methods agree → {:+d} ms",
        "summary": "  ─ Summary ─",
        "onset_corr": "  ─ Onset correlation ─",
        "hpss_perc": "  ─ HPSS percussive onset ─",
        "perc_rms": "  ─ Percussive RMS envelope ─",
        "perc_rms_fail": "    Percussive RMS failed: ",
        "rms_env": "  ─ RMS envelope (100ms) ─",
        "chromagram": "  ─ Chromagram ─",
        "no_librosa_flux": "  ⚠️ no librosa, spectral flux",
        "coarse_label": "  Phase 1: Coarse alignment (RMS envelope)",
        "coarse_result": "  Coarse: {:+d} ms  ({} frames × {:.0f} ms)",
        "fine_phase2": "  Phase 2: Fine tuning (focused FFT)",
        "fine_ok": "  ✅ Result: {:+d} ms",
        # Auto engine
        "vad_title": "─── Method 1: VAD Silence Pattern ───",
        "vad_desc": "  Analyzing speech timing (language independent)",
        "vad_result": "  VAD pattern: {:+d} ms  (reliability: {:.1f})",
        "env_title": "─── Method 2: Macro Energy Envelope ───",
        "env_result": "  Energy envelope: {:+d} ms  (reliability: {:.1f})",
        "hpss_title": "─── Method 3: HPSS Percussive ───",
        "hpss_result": "  HPSS percussive: {:+d} ms  (reliability: {:.1f})",
        "hpss_fail": "  ⚠️ HPSS failed: ",
        "hpss_no_librosa": "  ⚠️ no librosa — skipping HPSS",
        "onset_title": "─── Method 4: Onset Timing ───",
        "onset_result": "  Onset: {:+d} ms  (reliability: {:.1f})",
        "onset_fail": "  ⚠️ Onset failed: ",
        "consensus": "📊 Consensus Analysis",
        "no_results": "❌ No method produced results!",
        "methods_disagree": "  ⚠️ Methods disagree — using most reliable",
        "drift_title": "─── Drift Check (energy envelope) ───",
        "drift_start": "Start",
        "drift_mid": "Middle",
        "drift_end": "End",
        "drift_max": "  Max diff: {:.1f} ms",
        "drift_detected": "  ⛔ DRIFT DETECTED!",
        "drift_amount": "  {:.0f} ms drift across the film.",
        "drift_cause": "  Likely fps mismatch (23.976 vs 25 fps).",
        "drift_fix": "  Single delay CANNOT synchronize.",
        "drift_solution": "  Solution: match fps or apply time-stretch.",
        "drift_none": "  ✅ No drift (diff: {:.0f} ms)",
        "sync_warn_title": "  ⛔ SYNC WARNING",
        "sync_warn_desc": "  Methods give inconsistent results.",
        "sync_warn_hint": "  This audio may not sync with a simple delay.",
        "sync_warn_reasons": "  Possible reasons:",
        "sync_warn_r1": "    • Different frame rate (23.976 vs 25 fps)",
        "sync_warn_r2": "    • Different source/master used",
        "sync_warn_r3": "    • Audio files don't belong to same content",
        "final_result": "📌 Final result: {:+d} ms",
        "drift_active": "  ⚠️ Drift warning active — result may be unreliable",
        # Loading
        "load_video": "  📦 {} — extracting via FFmpeg subprocess...",
        "load_video_reason": "video file",
        "load_large_reason": "large file ({:.1f} GB)",
        "load_ffmpeg_ok": "  ✅ FFmpeg subprocess  ({} Hz)",
        "load_ffmpeg_fail": "  ⚠️ FFmpeg subprocess failed, trying other loaders...",
        "load_ffmpeg_err": "  ⚠️ FFmpeg subprocess error: ",
        "load_ffmpeg_timeout": "  ⚠️ FFmpeg timeout (120s)",
        "load_ffmpeg_extract_err": "  ⚠️ FFmpeg extract error: ",
        "load_pydub_ok": "  ✅ pydub/FFmpeg  ({} Hz)",
        "load_pydub_fail": "  ⚠️ pydub failed: ",
        "load_sf_ok": "  ✅ soundfile  ({} Hz)",
        "load_sf_fail": "  ⚠️ soundfile failed: ",
        "load_librosa_ok": "  ✅ librosa  ({} Hz)",
        "load_none": "No audio loader worked!\npip install pydub soundfile librosa  +  Install FFmpeg.",
        "first_min": "  Main audio: first {} min ({:.0f}s)",
        "dub_min": "  Dub: first {} min ({:.0f}s)",
        "sample_info": "  → {:.2f} sec  |  {} Hz  |  {:,} samples",
        # Manual Search
        "manual_title": "🎯  Manual Search",
        "manual_desc": "Select a section in main audio, search ±10 min range in dub",
        "manual_start": "Start :",
        "manual_end": "End :",
        "manual_range": "Search range (min) :",
        "manual_btn": "🎯  Manual Search",
        "manual_searching": "🎯  Searching...",
        "manual_enable": "Enable Manual Search",
        "manual_log_start": "─── Manual Search ───────────────────────────────",
        "manual_log_range": "  Main audio section: {} → {}",
        "manual_log_search": "  Searching in dub: ±{} min range",
        "manual_log_extract": "  Extracting {} sec from main audio...",
        "manual_log_dub_range": "  Extracting {} sec search region from dub...",
        "manual_log_corr": "  Computing correlation...",
        "manual_log_result": "  ✅ Detected delay: {:+d} ms",
        "manual_log_pos": "  Match position (in dub): {}",
        "manual_warn_time": "Invalid time format! Use h:mm:ss (e.g. 0:05:30)",
        "manual_warn_range": "End time must be greater than start time!",
        "manual_tip_short": "💡 Tip: Selecting less than 30 seconds in different languages may cause similarity artifacts.",
        "manual_loading_main": "Extracting target region from main audio...",
        "manual_no_audio": "⚠️ ERROR: No audio in the selected region!",
        "manual_loading_dub": "Extracting wide search region from dub...",
        "manual_micro_rhythm": "Extracting Micro-Rhythm Maps (1ms Resolution)...",
        "manual_dir_left": "◀ Pull Left (Dub Late)",
        "manual_dir_right": "Push Right (Dub Early) ▶",
        "manual_dir_sync": "✅ Synchronized",
        "analysis_rms_extract": "Extracting intensity maps (RMS Envelope)...",
        # Supported formats
        "fmt_all": "All Supported",
        "fmt_video": "Video Files",
        "fmt_audio": "Audio Files",
        "fmt_any": "All Files",
        # About
        "about_title": "About",
        "about_version": "Version 1.0  —  MrTOgRaS",
        "about_dev": "Developer",
        "about_dev_val": "Murat Oğraş",
        "about_web_btn": "🌐  Website",
        "about_github_btn": "🐙  GitHub Page",
        "about_mail_btn": "📧  Email",
        "about_libs": "Libraries Used",
        "about_formats": "Supported Formats",
        "about_combo": "7 Engines  ×  3 Modes  =  21 Combinations",
        "about_modes_old": "🎬 Old Films (speech suppression ON)",
        "about_modes_anim": "🎨 Animations (light suppression)",
        "about_modes_new": "🎥 New Films (no suppression)",
        "about_close": "  Close  ",
        "about_mit": "📜  MIT License",
        "about_info": "ℹ️  Program Info",
        "about_info_title": "Program Info",
        "about_donate": "❤️  Support Us",
        "about_engines": "Engines",
        "about_modes": "Modes",
        "engine_smart_rhythm": "⭐ Smart Rhythm (RMS)",
        # MIT License
        "mit_title": "MIT License",
    },
}

MIT_LICENSE_TEXT = """MIT License

Copyright (c) 2026 MrTOgRaS (Murat Oğraş)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

# ── Motor tanımları ──────────────────────────────────────────────────────────
ENGINE_LIST = [
    ("gcc_phat",  "GCC-PHAT Segmented"),
    ("envelope",  "Envelope XCorr"),
    ("numpy_fft", "NumPy FFT XCorr"),
    ("scipy",     "SciPy XCorr"),
    ("multi",     "Multi Feature (Onset+HPSS+Chroma)"),
    ("two_pass",  "2-Pass (RMS + Fine FFT)"),
    ("auto",      "⭐ Automatic (Smart Analysis)"),
]
ENGINE_LABELS = [e[1] for e in ENGINE_LIST]
ENGINE_KEYS   = [e[0] for e in ENGINE_LIST]

# ── Mod tanımları ────────────────────────────────────────────────────────────
MODES = [
    ("old",  "🎬"),
    ("anim", "🎨"),
    ("new",  "🎥"),
]

# ── Maksimum aranacak gecikme (ms) ──
MAX_DELAY_MS = 10_000

# ── 18 kombinasyon parametreleri ─────────────────────────────────────────────
TUNING = {
    ("gcc_phat", "old"):   {"cap_min": 8, "seg_sec": 20,
                            "max_lag_pct": 0.25, "phat_beta": 0.3},
    ("gcc_phat", "anim"):  {"cap_min": 3, "seg_sec": 10,
                            "max_lag_pct": 0.30, "phat_beta": 0.7},
    ("gcc_phat", "new"):   {"cap_min": 3, "seg_sec": 15,
                            "max_lag_pct": 0.25, "phat_beta": 0.5},
    ("envelope", "old"):   {"cap_min": 5, "frame_ms": 200, "offset_ms": 100},
    ("envelope", "anim"):  {"cap_min": 3, "frame_ms": 150},
    ("envelope", "new"):   {"cap_min": 3, "frame_ms": 100},
    ("numpy_fft", "old"):  {"cap_min": 5},
    ("numpy_fft", "anim"): {"cap_min": 3},
    ("numpy_fft", "new"):  {"cap_min": 3},
    ("scipy", "old"):      {"cap_min": 5},
    ("scipy", "anim"):     {"cap_min": 3},
    ("scipy", "new"):      {"cap_min": 3},
    ("multi", "old"):      {"cap_min": 5, "hop": 512, "fine_range_ms": 500},
    ("multi", "anim"):     {"cap_min": 3, "hop": 256, "fine_range_ms": 300},
    ("multi", "new"):      {"cap_min": 3, "hop": 512, "fine_range_ms": 300},
    ("two_pass", "old"):   {"cap_min": 5, "frame_ms": 200, "fine_range_ms": 500},
    ("two_pass", "anim"):  {"cap_min": 3, "frame_ms": 150, "fine_range_ms": 300},
    ("two_pass", "new"):   {"cap_min": 3, "frame_ms": 100, "fine_range_ms": 300},
    ("auto", "old"):       {"cap_min": 8, "vad_frame_ms": 30,
                            "env_frame_ms": 200, "drift_check": True},
    ("auto", "anim"):      {"cap_min": 5, "vad_frame_ms": 25,
                            "env_frame_ms": 150, "drift_check": True},
    ("auto", "new"):       {"cap_min": 5, "vad_frame_ms": 30,
                            "env_frame_ms": 100, "drift_check": True},
}

# ── Config dosyası ───────────────────────────────────────────────────────────
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "add_config.json")

# ── Renk paleti ─────────────────────────────────────────────────────────────
BG     = "#0d1117"
CARD   = "#161b22"
ACCENT = "#58a6ff"
GREEN  = "#3fb950"
TEXT   = "#e6edf3"
MUTED  = "#8b949e"
BORDER = "#30363d"
RED    = "#f85149"
YELLOW = "#d29922"
BTN_BG = "#21262d"


# ══════════════════════════════════════════════════════════════════════════════
class AudioDelayApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.lang = "tr"  # Varsayılan dil
        self.root.title(self.t("app_title"))
        self.root.geometry("1020x800")
        self.root.minsize(900, 720)
        self.root.configure(bg=BG)

        self.audio1_path  = tk.StringVar()
        self.audio2_path  = tk.StringVar()
        self.engine_var   = tk.StringVar(value=ENGINE_LABELS[6])
        self.mode_var     = tk.StringVar(value="new")
        self.ffmpeg_path  = tk.StringVar()
        self.ffprobe_path = tk.StringVar()
        self.mode_btns    = {}
        self._cancelled   = False
        self._analysis_thread = None

        # UI referansları (dil değişimi için)
        self._ui_refs = {}

        self._load_config()
        self._apply_ffmpeg_to_pydub()
        self._setup_styles()
        self._build_ui()
        self._check_deps()

    # ── Çeviri ─────────────────────────────────────────────────────────────
    def t(self, key):
        return STRINGS.get(self.lang, STRINGS["tr"]).get(key, key)

    def _get_formats(self):
        return [
            (self.t("fmt_all"),
             "*.mp3 *.flac *.aac *.ac3 *.eac3 *.ec3 *.dts *.wav *.m4a *.ogg *.wma "
             "*.mkv *.mp4 *.avi *.webm *.ts"),
            (self.t("fmt_video"), "*.mkv *.mp4 *.avi *.webm *.ts"),
            (self.t("fmt_audio"),
             "*.mp3 *.flac *.aac *.ac3 *.eac3 *.ec3 *.dts *.wav *.m4a *.ogg *.wma"),
            (self.t("fmt_any"), "*.*"),
        ]

    # ── Dil Değiştir ───────────────────────────────────────────────────────
    def _toggle_lang(self):
        self.lang = "en" if self.lang == "tr" else "tr"
        self._save_config()
        self._refresh_ui_texts()
        # Konsolu temizle ve bağımlılık kontrolünü yeni dilde tekrar bas
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self._check_deps()

    def _refresh_ui_texts(self):
        self.root.title(self.t("app_title"))
        refs = self._ui_refs
        # Başlık
        refs["header_title"].config(text=self.t("header_title"))
        refs["header_version"].config(text=self.t("header_version"))
        refs["btn_about"].config(text=self.t("btn_about"))
        refs["btn_ffmpeg"].config(text=self.t("btn_ffmpeg"))
        refs["btn_lang"].config(text=self.t("btn_lang"))
        # Dosya kartları
        refs["card1_title"].config(text=self.t("main_audio"))
        refs["card1_sub"].config(text=self.t("main_audio_sub"))
        refs["card1_btn"].config(text=self.t("btn_select"))
        refs["card2_title"].config(text=self.t("dub_audio"))
        refs["card2_sub"].config(text=self.t("dub_audio_sub"))
        refs["card2_btn"].config(text=self.t("btn_select"))
        # Motor
        refs["engine_label"].config(text=self.t("engine_label"))
        # Mod butonları
        mode_keys = ["old", "anim", "new"]
        mode_str_keys = ["mode_old", "mode_anim", "mode_new"]
        for mk, sk in zip(mode_keys, mode_str_keys):
            emoji = [m[1] for m in MODES if m[0] == mk][0]
            self.mode_btns[mk].config(text=f"{emoji}  {self.t(sk)}")
        # Başlat/İptal
        if self.analyze_btn.cget("state") == "disabled":
            self.analyze_btn.config(text=self.t("btn_analyzing"))
        else:
            self.analyze_btn.config(text=self.t("btn_start"))
        self.cancel_btn.config(text=self.t("btn_cancel"))
        # Sonuçlar
        refs["results_title"].config(text=self.t("results_title"))
        refs["res_delay_lbl"].config(text=self.t("res_delay"))
        refs["res_format_lbl"].config(text=self.t("res_format"))
        refs["res_dir_lbl"].config(text=self.t("res_direction"))
        refs["res_eng_lbl"].config(text=self.t("res_engine"))
        # Manuel Arama
        refs["manual_chk"].config(text=self.t("manual_enable"))
        refs["manual_desc"].config(text=self.t("manual_desc"))
        refs["manual_start_lbl"].config(text=self.t("manual_start"))
        refs["manual_end_lbl"].config(text=self.t("manual_end"))
        refs["manual_range_lbl"].config(text=self.t("manual_range"))
        if self.manual_btn.cget("state") == "disabled":
            self.manual_btn.config(text=self.t("manual_searching"))
        else:
            self.manual_btn.config(text=self.t("manual_btn"))
        # Log
        refs["log_title"].config(text=self.t("log_title"))
        # FFmpeg status
        self._update_ffmpeg_status_bar()

    # ── Config ────────────────────────────────────────────────────────────────
    def _load_config(self):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            self.ffmpeg_path.set(cfg.get("ffmpeg", ""))
            self.ffprobe_path.set(cfg.get("ffprobe", ""))
            if "lang" in cfg:
                self.lang = cfg["lang"]
        except Exception:
            pass

    def _save_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "ffmpeg":  self.ffmpeg_path.get(),
                    "ffprobe": self.ffprobe_path.get(),
                    "lang":    self.lang,
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._log(f"{self.t('ffmpeg_save_err')}{e}", "warn")

    def _apply_ffmpeg_to_pydub(self):
        if not PYDUB_AVAILABLE:
            return
        ffmpeg  = self.ffmpeg_path.get().strip()
        ffprobe = self.ffprobe_path.get().strip()
        if ffmpeg and os.path.isfile(ffmpeg):
            AudioSegment.converter = ffmpeg
            AudioSegment.ffmpeg    = ffmpeg
        if ffprobe and os.path.isfile(ffprobe):
            AudioSegment.ffprobe = ffprobe
        if ffmpeg:
            ffdir = os.path.dirname(ffmpeg)
            if ffdir and ffdir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = (ffdir + os.pathsep
                                      + os.environ.get("PATH", ""))

    # ── Stiller ──────────────────────────────────────────────────────────────
    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TFrame",       background=BG)
        s.configure("TLabel",       background=BG, foreground=TEXT,
                    font=("Segoe UI", 10))
        s.configure("TCombobox",    fieldbackground=BTN_BG,
                    foreground=TEXT, bordercolor=BORDER)
        s.map("TCombobox",
              fieldbackground=[("readonly", BTN_BG)],
              foreground=[("readonly", TEXT)])
        s.configure("TProgressbar", troughcolor=BTN_BG, background=ACCENT)

    # ── Ana Arayüz ──────────────────────────────────────────────────────────
    def _build_ui(self):
        main = tk.Frame(self.root, bg=BG, padx=18, pady=14)
        main.pack(fill="both", expand=True)
        refs = self._ui_refs

        # ── Başlık ──
        hdr = tk.Frame(main, bg=BG)
        hdr.pack(fill="x", pady=(0, 10))
        refs["header_title"] = tk.Label(
            hdr, text=self.t("header_title"),
            bg=BG, fg=TEXT, font=("Segoe UI", 17, "bold"))
        refs["header_title"].pack(side="left")
        refs["header_version"] = tk.Label(
            hdr, text=self.t("header_version"),
            bg=BG, fg=MUTED, font=("Segoe UI", 10))
        refs["header_version"].pack(side="left", pady=(7, 0))

        # Dil butonu
        refs["btn_lang"] = tk.Button(
            hdr, text=self.t("btn_lang"),
            command=self._toggle_lang,
            bg=BTN_BG, fg=ACCENT, font=("Segoe UI", 9, "bold"),
            relief="flat", padx=10, pady=4, cursor="hand2")
        refs["btn_lang"].pack(side="right", padx=(6, 0))

        refs["btn_about"] = tk.Button(
            hdr, text=self.t("btn_about"),
            command=self._show_about,
            bg=BTN_BG, fg=TEXT, font=("Segoe UI", 9),
            relief="flat", padx=10, pady=4, cursor="hand2")
        refs["btn_about"].pack(side="right", padx=(6, 0))

        refs["btn_ffmpeg"] = tk.Button(
            hdr, text=self.t("btn_ffmpeg"),
            command=self._show_ffmpeg_settings,
            bg=BTN_BG, fg=YELLOW, font=("Segoe UI", 9),
            relief="flat", padx=10, pady=4, cursor="hand2")
        refs["btn_ffmpeg"].pack(side="right")

        tk.Frame(main, bg=BORDER, height=1).pack(fill="x", pady=(0, 12))

        # ── FFmpeg durum ──
        self.ffmpeg_status_bar = tk.Label(
            main, text="", bg=BG, fg=MUTED,
            font=("Segoe UI", 8), anchor="w")
        self.ffmpeg_status_bar.pack(fill="x", pady=(0, 6))
        self._update_ffmpeg_status_bar()

        # ── Dosya Kartları ──
        fc = tk.Frame(main, bg=BG)
        fc.pack(fill="x", pady=(0, 12))
        fc.columnconfigure(0, weight=1)
        fc.columnconfigure(1, weight=1)
        self._file_card(fc, "main_audio", "main_audio_sub",
                        self.audio1_path, self._pick_audio1, 0, "1")
        self._file_card(fc, "dub_audio", "dub_audio_sub",
                        self.audio2_path, self._pick_audio2, 1, "2")

        # ── Motor Seçimi ──
        eng_card = self._card(main, pady=8)
        eng_card.pack(fill="x", pady=(0, 6))
        eng_row = tk.Frame(eng_card, bg=CARD)
        eng_row.pack(fill="x")
        refs["engine_label"] = tk.Label(
            eng_row, text=self.t("engine_label"),
            bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold"))
        refs["engine_label"].pack(side="left")
        cb = ttk.Combobox(eng_row, textvariable=self.engine_var,
                          width=38, state="readonly",
                          values=ENGINE_LABELS)
        cb.pack(side="left", padx=10)

        # ── Mod Seçimi + Başlat ──
        ctrl = self._card(main, pady=8)
        ctrl.pack(fill="x", pady=(0, 12))

        mode_str_keys = {"old": "mode_old", "anim": "mode_anim", "new": "mode_new"}
        for mode_key, emoji in MODES:
            is_sel = (mode_key == self.mode_var.get())
            btn = tk.Button(
                ctrl, text=f"{emoji}  {self.t(mode_str_keys[mode_key])}",
                command=lambda m=mode_key: self._set_mode(m),
                bg=ACCENT if is_sel else BTN_BG,
                fg="white" if is_sel else TEXT,
                font=("Segoe UI", 10, "bold"),
                relief="flat", padx=14, pady=6, cursor="hand2")
            btn.pack(side="left", padx=4)
            self.mode_btns[mode_key] = btn

        self.cancel_btn = tk.Button(
            ctrl, text=self.t("btn_cancel"),
            command=self._cancel,
            bg=RED, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=14, pady=6, cursor="hand2",
            state="disabled")
        self.cancel_btn.pack(side="right")

        self.analyze_btn = tk.Button(
            ctrl, text=self.t("btn_start"),
            command=self._start,
            bg=ACCENT, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=22, pady=6, cursor="hand2")
        self.analyze_btn.pack(side="right", padx=(0, 6))

        # ── Manuel Arama Paneli ──
        self.manual_enabled = tk.BooleanVar(value=False)
        manual_card = self._card(main, pady=8)
        manual_card.pack(fill="x", pady=(0, 10))
        self._manual_card = manual_card

        chk_row = tk.Frame(manual_card, bg=CARD)
        chk_row.pack(fill="x")
        refs["manual_chk"] = tk.Checkbutton(
            chk_row, text=self.t("manual_enable"),
            variable=self.manual_enabled,
            command=self._toggle_manual_panel,
            bg=CARD, fg=TEXT, selectcolor=BTN_BG,
            activebackground=CARD, activeforeground=TEXT,
            font=("Segoe UI", 10, "bold"), cursor="hand2")
        refs["manual_chk"].pack(side="left")
        refs["manual_desc"] = tk.Label(
            chk_row, text=self.t("manual_desc"),
            bg=CARD, fg=MUTED, font=("Segoe UI", 8))
        refs["manual_desc"].pack(side="left", padx=(10, 0))

        # İç panel (gizli başlar)
        self._manual_inner = tk.Frame(manual_card, bg=CARD)

        inp_row = tk.Frame(self._manual_inner, bg=CARD)
        inp_row.pack(fill="x", pady=(8, 0))

        refs["manual_start_lbl"] = tk.Label(
            inp_row, text=self.t("manual_start"),
            bg=CARD, fg=TEXT, font=("Segoe UI", 9))
        refs["manual_start_lbl"].pack(side="left")
        self.manual_start_var = tk.StringVar(value="0:00:00")
        tk.Entry(inp_row, textvariable=self.manual_start_var,
                 bg=BTN_BG, fg=TEXT, font=("Consolas", 10),
                 relief="flat", width=10, insertbackground=TEXT
                 ).pack(side="left", padx=(4, 14), ipady=3)

        refs["manual_end_lbl"] = tk.Label(
            inp_row, text=self.t("manual_end"),
            bg=CARD, fg=TEXT, font=("Segoe UI", 9))
        refs["manual_end_lbl"].pack(side="left")
        self.manual_end_var = tk.StringVar(value="0:00:30")
        tk.Entry(inp_row, textvariable=self.manual_end_var,
                 bg=BTN_BG, fg=TEXT, font=("Consolas", 10),
                 relief="flat", width=10, insertbackground=TEXT
                 ).pack(side="left", padx=(4, 14), ipady=3)

        refs["manual_range_lbl"] = tk.Label(
            inp_row, text=self.t("manual_range"),
            bg=CARD, fg=TEXT, font=("Segoe UI", 9))
        refs["manual_range_lbl"].pack(side="left")
        self.manual_range_var = tk.StringVar(value="10")
        tk.Entry(inp_row, textvariable=self.manual_range_var,
                 bg=BTN_BG, fg=TEXT, font=("Consolas", 10),
                 relief="flat", width=5, insertbackground=TEXT
                 ).pack(side="left", padx=(4, 14), ipady=3)

        self.manual_btn = tk.Button(
            inp_row, text=self.t("manual_btn"),
            command=self._start_manual_search,
            bg=ACCENT, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=14, pady=4, cursor="hand2")
        self.manual_btn.pack(side="right")

        # ── Sonuç Kutuları (4) ──
        res_card = self._card(main, pady=12)
        res_card.pack(fill="x", pady=(0, 10))
        refs["results_title"] = tk.Label(
            res_card, text=self.t("results_title"),
            bg=CARD, fg=TEXT, font=("Segoe UI", 11, "bold"))
        refs["results_title"].pack(anchor="w", pady=(0, 8))
        rg = tk.Frame(res_card, bg=CARD)
        rg.pack(fill="x")
        for i in range(4):
            rg.columnconfigure(i, weight=1)
        self.lbl_ms,  refs["res_delay_lbl"]  = self._result_box(rg, self.t("res_delay"),     "— ms", 0)
        self.lbl_fmt, refs["res_format_lbl"] = self._result_box(rg, self.t("res_format"),    "—",    1)
        self.lbl_dir, refs["res_dir_lbl"]    = self._result_box(rg, self.t("res_direction"),  "—",    2)
        self.lbl_eng, refs["res_eng_lbl"]    = self._result_box(rg, self.t("res_engine"),     "—",    3)

        # ── Progress ──
        self.progress = ttk.Progressbar(main, mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 8))

        # ── Log ──
        log_card = self._card(main, pady=8)
        log_card.pack(fill="both", expand=True)
        refs["log_title"] = tk.Label(
            log_card, text=self.t("log_title"),
            bg=CARD, fg=MUTED, font=("Segoe UI", 9))
        refs["log_title"].pack(anchor="w")
        self.log = scrolledtext.ScrolledText(
            log_card, height=10, bg=BG, fg=TEXT,
            font=("Consolas", 9), relief="flat",
            insertbackground=TEXT, wrap="word")
        self.log.pack(fill="both", expand=True, pady=(4, 0))
        self.log.configure(state="disabled")
        for tag, color in [("ok", GREEN), ("err", RED), ("warn", YELLOW),
                           ("accent", ACCENT), ("default", TEXT)]:
            self.log.tag_configure(tag, foreground=color)

    # ── Mod Değiştirme ───────────────────────────────────────────────────────
    def _set_mode(self, mode):
        self.mode_var.set(mode)
        for key, btn in self.mode_btns.items():
            if key == mode:
                btn.configure(bg=ACCENT, fg="white")
            else:
                btn.configure(bg=BTN_BG, fg=TEXT)

    # ── FFmpeg Durum ─────────────────────────────────────────────────────────
    def _update_ffmpeg_status_bar(self):
        fp = self.ffmpeg_path.get().strip()
        if fp and os.path.isfile(fp):
            self.ffmpeg_status_bar.config(
                text=f"{self.t('ffmpeg_set')}{fp}", fg=GREEN)
        else:
            self.ffmpeg_status_bar.config(
                text=self.t("ffmpeg_not_set"), fg=YELLOW)

    # ── Widget Yardımcıları ──────────────────────────────────────────────────
    def _card(self, parent, pady=10, padx=14):
        f = tk.Frame(parent, bg=CARD, padx=padx, pady=pady)
        f.configure(highlightbackground=BORDER, highlightthickness=1)
        return f

    def _file_card(self, parent, title_key, sub_key, var, cmd, col, card_id):
        refs = self._ui_refs
        c = self._card(parent, padx=12, pady=10)
        c.grid(row=0, column=col, sticky="nsew",
               padx=(0, 8) if col == 0 else (8, 0))
        refs[f"card{card_id}_title"] = tk.Label(
            c, text=self.t(title_key), bg=CARD, fg=TEXT,
            font=("Segoe UI", 10, "bold"))
        refs[f"card{card_id}_title"].pack(anchor="w")
        refs[f"card{card_id}_sub"] = tk.Label(
            c, text=self.t(sub_key), bg=CARD, fg=MUTED,
            font=("Segoe UI", 8))
        refs[f"card{card_id}_sub"].pack(anchor="w", pady=(0, 6))
        row = tk.Frame(c, bg=CARD)
        row.pack(fill="x")
        tk.Entry(row, textvariable=var, bg=BTN_BG, fg=TEXT,
                 font=("Segoe UI", 9), relief="flat",
                 insertbackground=TEXT).pack(side="left", fill="x",
                                            expand=True, ipady=5)
        refs[f"card{card_id}_btn"] = tk.Button(
            row, text=self.t("btn_select"), command=cmd,
            bg=BTN_BG, fg=ACCENT, font=("Segoe UI", 9, "bold"),
            relief="flat", padx=8, cursor="hand2")
        refs[f"card{card_id}_btn"].pack(side="right", padx=(6, 0))
        lbl = tk.Label(c, text=self.t("file_not_selected"), bg=CARD, fg=MUTED,
                       font=("Segoe UI", 8))
        lbl.pack(anchor="w", pady=(4, 0))
        setattr(self, f"info{col + 1}", lbl)

    def _result_box(self, parent, label, default, col):
        b = tk.Frame(parent, bg=BG, padx=8, pady=8)
        b.grid(row=0, column=col, sticky="nsew", padx=3)
        b.configure(highlightbackground=BORDER, highlightthickness=1)
        lbl_title = tk.Label(b, text=label, bg=BG, fg=MUTED,
                             font=("Segoe UI", 8))
        lbl_title.pack()
        lbl = tk.Label(b, text=default, bg=BG, fg=ACCENT,
                       font=("Segoe UI", 15, "bold"))
        lbl.pack(pady=(2, 0))
        return lbl, lbl_title

    # ── Log ──────────────────────────────────────────────────────────────────
    def _log(self, msg, tag="default"):
        self.log.configure(state="normal")
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.log.insert("end", f"[{ts}]  {msg}\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _check_deps(self):
        self._log(self.t("dep_check"), "accent")
        self._log(self.t("dep_librosa_ok") if LIBROSA_AVAILABLE
                  else self.t("dep_librosa_fail"),
                  "ok" if LIBROSA_AVAILABLE else "err")
        self._log(self.t("dep_pydub_ok") if PYDUB_AVAILABLE
                  else self.t("dep_pydub_fail"),
                  "ok" if PYDUB_AVAILABLE else "warn")
        self._log(self.t("dep_sf_ok") if SOUNDFILE_AVAILABLE
                  else self.t("dep_sf_fail"),
                  "ok" if SOUNDFILE_AVAILABLE else "warn")
        ffmp = self.ffmpeg_path.get().strip()
        if ffmp and os.path.isfile(ffmp):
            self._log(self.t("dep_ffmpeg_ok").format(ffmp), "ok")
        else:
            self._log(self.t("dep_ffmpeg_fail"), "warn")
        self._log(self.t("dep_ready"), "default")

    # ── Dosya Seçiciler ──────────────────────────────────────────────────────
    def _pick_audio1(self):
        p = filedialog.askopenfilename(
            title=self.t("pick_main"), filetypes=self._get_formats())
        if p:
            self.audio1_path.set(p)
            self.info1.config(text=f"✅  {os.path.basename(p)}", fg=GREEN)
            self._log(f"{self.t('main_selected')}{os.path.basename(p)}", "ok")

    def _pick_audio2(self):
        p = filedialog.askopenfilename(
            title=self.t("pick_dub"), filetypes=self._get_formats())
        if p:
            self.audio2_path.set(p)
            self.info2.config(text=f"✅  {os.path.basename(p)}", fg=GREEN)
            self._log(f"{self.t('dub_selected')}{os.path.basename(p)}", "ok")

    # ── FFmpeg Ayarları ──────────────────────────────────────────────────────
    def _show_ffmpeg_settings(self):
        w = tk.Toplevel(self.root)
        w.title(self.t("ffmpeg_settings_title"))
        w.geometry("620x320")
        w.configure(bg=CARD)
        w.resizable(False, False)
        w.transient(self.root)
        w.grab_set()

        tk.Label(w, text=self.t("ffmpeg_header"),
                 bg=CARD, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(pady=(18, 4))
        tk.Label(w, text=self.t("ffmpeg_desc"),
                 bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack()
        tk.Frame(w, bg=BORDER, height=1).pack(fill="x", padx=20, pady=12)

        for label_key, var, attr in [
            ("ffmpeg_path_label",  self.ffmpeg_path,  "ffmpeg"),
            ("ffprobe_path_label", self.ffprobe_path, "ffprobe"),
        ]:
            r = tk.Frame(w, bg=CARD)
            r.pack(fill="x", padx=20, pady=6)
            tk.Label(r, text=self.t(label_key), bg=CARD, fg=TEXT,
                     font=("Segoe UI", 9), width=16,
                     anchor="w").pack(side="left")
            tk.Entry(r, textvariable=var, bg=BTN_BG, fg=TEXT,
                     font=("Segoe UI", 9), relief="flat",
                     insertbackground=TEXT, width=44
                     ).pack(side="left", ipady=5, padx=(4, 6))

            def _browse(v=var, a=attr):
                p = filedialog.askopenfilename(
                    title=f"{a}.exe{self.t('pick_ffmpeg')}",
                    filetypes=[("EXE", "*.exe"),
                               (self.t("fmt_any"), "*.*")])
                if p:
                    v.set(p)

            tk.Button(r, text="📂", command=_browse,
                      bg=BTN_BG, fg=ACCENT, relief="flat",
                      padx=6, cursor="hand2").pack(side="left")

        tk.Frame(w, bg=BORDER, height=1).pack(fill="x", padx=20, pady=12)
        tk.Label(w, text=self.t("ffmpeg_tip"),
                 bg=CARD, fg=MUTED, font=("Segoe UI", 8),
                 justify="left").pack(padx=20, anchor="w")

        def _save_and_close():
            self._save_config()
            self._apply_ffmpeg_to_pydub()
            self._update_ffmpeg_status_bar()
            self._log(self.t("ffmpeg_saved"), "ok")
            w.destroy()

        tk.Button(w, text=self.t("ffmpeg_save"),
                  command=_save_and_close,
                  bg=ACCENT, fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=16, pady=7,
                  cursor="hand2").pack(pady=(0, 16))

    # ── Analiz Başlat / İptal ─────────────────────────────────────────────────
    def _start(self):
        if not self.audio1_path.get():
            messagebox.showwarning(self.t("warn_title"),
                                   self.t("warn_no_main"))
            return
        if not self.audio2_path.get():
            messagebox.showwarning(self.t("warn_title"),
                                   self.t("warn_no_dub"))
            return
        self._cancelled = False
        self.analyze_btn.configure(state="disabled",
                                   text=self.t("btn_analyzing"))
        self.cancel_btn.configure(state="normal")
        self.progress.start(10)
        for lbl, _ in [(self.lbl_ms, None), (self.lbl_fmt, None),
                        (self.lbl_dir, None), (self.lbl_eng, None)]:
            lbl.configure(text="...", fg=YELLOW)
        self._analysis_thread = threading.Thread(
            target=self._run_analysis, daemon=True)
        self._analysis_thread.start()

    def _cancel(self):
        self._cancelled = True
        self._log(self.t("cancel_msg"), "warn")
        self.cancel_btn.configure(state="disabled")

    def _check_cancel(self):
        if self._cancelled:
            raise InterruptedError("Cancelled")

    # ── Manuel Arama ─────────────────────────────────────────────────────────
    def _toggle_manual_panel(self):
        if self.manual_enabled.get():
            self._manual_inner.pack(fill="x")
        else:
            self._manual_inner.pack_forget()

    def _parse_time(self, text):
        """sa:dk:sn formatını saniyeye çevirir."""
        text = text.strip()
        parts = text.split(":")
        if len(parts) == 3:
            h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
            return h * 3600 + m * 60 + s
        elif len(parts) == 2:
            m, s = int(parts[0]), int(parts[1])
            return m * 60 + s
        else:
            return int(text)

    def _fmt_time(self, total_sec):
        """Saniyeyi sa:dk:sn formatına çevirir."""
        h = int(total_sec) // 3600
        m = (int(total_sec) % 3600) // 60
        s = int(total_sec) % 60
        return f"{h}:{m:02d}:{s:02d}"

    def _start_manual_search(self):
        if not self.audio1_path.get():
            messagebox.showwarning(self.t("warn_title"),
                                   self.t("warn_no_main"))
            return
        if not self.audio2_path.get():
            messagebox.showwarning(self.t("warn_title"),
                                   self.t("warn_no_dub"))
            return
        try:
            start_sec = self._parse_time(self.manual_start_var.get())
            end_sec = self._parse_time(self.manual_end_var.get())
        except (ValueError, IndexError):
            messagebox.showwarning(self.t("warn_title"),
                                   self.t("manual_warn_time"))
            return
        if end_sec <= start_sec:
            messagebox.showwarning(self.t("warn_title"),
                                   self.t("manual_warn_range"))
            return
        try:
            search_range = int(self.manual_range_var.get().strip())
        except ValueError:
            search_range = 10

        self._cancelled = False
        self.manual_btn.configure(state="disabled",
                                  text=self.t("manual_searching"))
        self.progress.start(10)
        threading.Thread(
            target=self._run_manual_search,
            args=(start_sec, end_sec, search_range),
            daemon=True).start()

    def _run_manual_search(self, start_sec, end_sec, range_min):
        try:
            self._log(self.t("manual_log_start"), "accent")
            self._log(self.t("manual_log_range").format(
                self._fmt_time(start_sec), self._fmt_time(end_sec)), "default")
            self._log(self.t("manual_log_search").format(range_min), "default")

            duration_main = end_sec - start_sec

            # --- UYARI KONTROLÜ ---
            if duration_main < 30:
                self._log(self.t("manual_tip_short"), "warn")

            self._log(self.t("manual_loading_main"), "default")
            excerpt, sr1 = self._load(self.audio1_path.get(), start_sec=start_sec, duration_sec=duration_main)
            self._check_cancel()

            if np.max(np.abs(excerpt)) < 0.005:
                self._log(self.t("manual_no_audio"), "err")
                self.root.after(0, self._done_manual)
                return

            window_start = max(0, start_sec - (range_min * 60))
            duration_dub = (end_sec + (range_min * 60)) - window_start
            self._log(self.t("manual_loading_dub"), "default")
            dub_window, sr2 = self._load(self.audio2_path.get(), start_sec=window_start, duration_sec=duration_dub)
            self._check_cancel()

            if sr1 != sr2:
                self._log(self.t("diff_sr").format(sr1, sr2), "warn")
                new_len = int(len(dub_window) * (sr1 / sr2))
                dub_window = np.interp(np.linspace(0, len(dub_window) - 1, new_len), np.arange(len(dub_window)), dub_window).astype(np.float32)
                sr2 = sr1
                self._log(self.t("resample_done"), "ok")

            sr = sr1
            excerpt = excerpt.astype(np.float64)
            dub_window = dub_window.astype(np.float64)

            self._log(self.t("manual_micro_rhythm"), "default")
            self._check_cancel()

            # --- KISA KESİTLER İÇİN MİKRO-RİTİM (ULTRA HASSAS) ---
            def get_micro_rhythm(sig, current_sr):
                # 1. Sadece İnsan Sesine ve Ana Efektlere Odaklan
                nyq = current_sr / 2
                b, a = signal.butter(3, [300/nyq, 3000/nyq], btype='band')
                sig_filt = signal.filtfilt(b, a, sig)

                # 2. Sinyal şiddetini al
                y_abs = np.abs(sig_filt)

                # 3. 1000 Hz (1 milisaniye) ultra yüksek çözünürlüğe düşür
                target_sr = 1000
                factor = current_sr // target_sr
                y_down = y_abs[::factor]

                # 4. Heceleri ve mikro nefesleri belirginleştir (10 Hz Lowpass)
                b2, a2 = signal.butter(3, 10 / (target_sr / 2), btype='low')
                env = signal.filtfilt(b2, a2, y_down)

                # 5. Normalizasyon
                std_val = np.std(env)
                if std_val < 1e-10:
                    return env, target_sr
                return (env - np.mean(env)) / std_val, target_sr

            exc_env, work_sr = get_micro_rhythm(excerpt, sr)
            dub_env, _ = get_micro_rhythm(dub_window, sr)

            self._log(self.t("manual_log_corr"), "default")
            self._check_cancel()

            corr = signal.fftconvolve(dub_env, exc_env[::-1], mode="full")
            peak_idx = int(np.argmax(corr))

            match_offset = peak_idx - len(exc_env) + 1
            match_sec = window_start + (match_offset / work_sr)

            delay_sec = match_sec - start_sec
            raw_delay_ms = int(round(delay_sec * 1000))

            # --- MKVToolNix / Premiere STANDART DÜZELTMESİ ---
            delay_ms = -raw_delay_ms

            self._log(self.t("manual_log_result").format(delay_ms), "ok")
            self._log(self.t("manual_log_pos").format(self._fmt_time(match_sec)), "ok")
            self._log("─" * 52, "default")

            fmt = self._fmt_delay(abs(delay_ms))
            if delay_ms < -10:
                direction = self.t("manual_dir_left")
            elif delay_ms > 10:
                direction = self.t("manual_dir_right")
            else:
                direction = self.t("manual_dir_sync")

            self.root.after(0, self._show_results, delay_ms, fmt, direction, self.t("manual_title"))

        except InterruptedError:
            self._log(self.t("cancelled"), "warn")
            self.root.after(0, self._done_manual)
        except Exception as exc:
            import traceback as tb
            self._log(f"{self.t('error')}{exc}", "err")
            self._log(tb.format_exc(), "err")
            self.root.after(0, self._done_manual)

    def _done_manual(self):
        self.progress.stop()
        self.manual_btn.configure(state="normal",
                                  text=self.t("manual_btn"))

    # ── Ana Analiz Thread ────────────────────────────────────────────────────
    def _run_analysis(self):
        try:
            self._log(self.t("analysis_start"), "accent")

            # AKILLI KESİT (SMART CHUNKING)
            start_time = 600  # 10. Dakika
            duration = 180    # 3 Dakika boyunca ara

            self._log(f"Optimizasyon: Filmin sadece 10:00 - 13:00 arası analiz ediliyor...", "default")

            self._log(self.t("loading_main"), "default")
            y1, sr1 = self._load(self.audio1_path.get(), start_sec=start_time, duration_sec=duration)
            self._check_cancel()

            self._log(self.t("loading_dub"), "default")
            y2, sr2 = self._load(self.audio2_path.get(), start_sec=start_time, duration_sec=duration)
            self._check_cancel()

            if sr1 != sr2:
                self._log(self.t("diff_sr").format(sr1, sr2), "warn")
                new_len = int(len(y2) * (sr1 / sr2))
                y2 = np.interp(np.linspace(0, len(y2) - 1, new_len), np.arange(len(y2)), y2).astype(np.float32)
                sr2 = sr1
                self._log(self.t("resample_done"), "ok")

            sr = sr1
            y1 = y1.astype(np.float64)
            y2 = y2.astype(np.float64)

            self._log(self.t("analysis_rms_extract"), "default")
            self._check_cancel()

            def get_robust_envelope(sig, current_sr):
                nyq = current_sr / 2
                b, a = signal.butter(3, [300/nyq, 3000/nyq], btype='band')
                sig_filt = signal.filtfilt(b, a, sig)

                target_sr = 100
                factor = current_sr // target_sr
                n_frames = len(sig_filt) // factor
                if n_frames == 0:
                    return np.zeros(1), target_sr

                sig_cut = sig_filt[:n_frames * factor]
                energy = np.sqrt(np.mean(sig_cut.reshape(-1, factor)**2, axis=1))

                std_val = np.std(energy)
                if std_val < 1e-10:
                    return energy, target_sr
                return (energy - np.mean(energy)) / std_val, target_sr

            env1, work_sr = get_robust_envelope(y1, sr)
            env2, _ = get_robust_envelope(y2, sr)

            self._log("Çapraz Korelasyon (Cross-Correlation) hesaplanıyor...", "default")
            self._check_cancel()

            corr = signal.fftconvolve(env2, env1[::-1], mode="full")
            peak_idx = int(np.argmax(corr))

            match_offset = peak_idx - len(env1) + 1
            delay_sec = match_offset / work_sr
            raw_delay_ms = int(round(delay_sec * 1000))

            # --- MKVToolNix / Premiere STANDART DÜZELTMESİ ---
            delay_ms = -raw_delay_ms

            fmt = self._fmt_delay(abs(delay_ms))

            if delay_ms < -10:
                direction = self.t("manual_dir_left")
            elif delay_ms > 10:
                direction = self.t("manual_dir_right")
            else:
                direction = self.t("manual_dir_sync")

            self._log("─" * 52, "default")
            self._log(self.t("analysis_done"), "ok")
            self._log(self.t("delay_label").format(delay_ms), "accent")
            self._log(self.t("format_label").format(fmt), "accent")
            self._log(self.t("dir_label").format(direction), "accent")
            self._log("─" * 52, "default")

            self.root.after(0, self._show_results, delay_ms, fmt, direction, self.t("engine_smart_rhythm"))

        except InterruptedError:
            self._log(self.t("cancelled"), "warn")
            self.root.after(0, self._done)
        except Exception as exc:
            import traceback as tb
            self._log(f"{self.t('error')}{exc}", "err")
            self._log(tb.format_exc(), "err")
            self.root.after(0, self._done)

    # ── Ses Yükleme ──────────────────────────────────────────────────────────

    VIDEO_EXTS = {".mkv", ".mp4", ".avi", ".webm", ".ts"}

    def _get_ffmpeg_bin(self):
        fp = self.ffmpeg_path.get().strip()
        if fp and os.path.isfile(fp):
            return fp
        found = shutil.which("ffmpeg")
        if found:
            return found
        return None

    def _ffmpeg_extract_wav(self, path: str, start_sec=None, duration_sec=None) -> tuple:
        ffmpeg = self._get_ffmpeg_bin()
        if not ffmpeg:
            return None
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        try:
            # -i (input) EN BAŞA ALINDI! Keyframe atlaması yapmaz, saniyesi saniyesine keser.
            cmd = [ffmpeg, "-y", "-i", path]
            if start_sec is not None:
                cmd.extend(["-ss", str(start_sec)])
            if duration_sec is not None:
                cmd.extend(["-t", str(duration_sec)])
            cmd.extend([
                "-vn", "-ac", "1", "-ar", "48000",
                "-sample_fmt", "s16", "-f", "wav",
                tmp.name,
            ])
            proc = subprocess.run(
                cmd, capture_output=True, timeout=120,
                creationflags=(subprocess.CREATE_NO_WINDOW
                               if hasattr(subprocess, "CREATE_NO_WINDOW")
                               else 0),
            )
            if proc.returncode != 0:
                return None
            if SOUNDFILE_AVAILABLE:
                y, sr = sf.read(tmp.name, always_2d=False)
                if y.ndim > 1:
                    y = y.mean(axis=1)
                return y.astype(np.float32), sr
            else:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    y, sr = librosa.load(tmp.name, sr=None, mono=True)
                return y, sr
        except Exception:
            return None
        finally:
            try:
                os.unlink(tmp.name)
            except OSError:
                pass

    def _load(self, path: str, start_sec=None, duration_sec=None):
        ext = os.path.splitext(path)[1].lower()
        file_size = 0
        try:
            file_size = os.path.getsize(path)
        except OSError:
            pass

        is_video = ext in self.VIDEO_EXTS
        is_large = file_size > 2 * 1024 * 1024 * 1024

        # Eğer start_sec veya duration_sec verilmişse (Manuel Arama), KESİNLİKLE FFmpeg kullan
        if is_video or is_large or start_sec is not None or duration_sec is not None:
            if start_sec is not None:
                reason = "hızlı kesit"
            elif is_video:
                reason = self.t("load_video_reason")
            else:
                reason = self.t("load_large_reason").format(
                    file_size / (1024**3))

            self._log(self.t("load_video").format(reason), "default")
            result = self._ffmpeg_extract_wav(path, start_sec, duration_sec)
            if result is not None:
                self._log(self.t("load_ffmpeg_ok").format(result[1]), "ok")
                return result
            self._log(self.t("load_ffmpeg_fail"), "warn")

        if PYDUB_AVAILABLE:
            try:
                seg     = AudioSegment.from_file(path)
                seg     = seg.set_channels(1)
                samples = np.array(seg.get_array_of_samples(),
                                   dtype=np.float32)
                samples /= float(2 ** (seg.sample_width * 8 - 1))
                self._log(self.t("load_pydub_ok").format(seg.frame_rate), "ok")
                return samples, seg.frame_rate
            except Exception as e:
                self._log(f"{self.t('load_pydub_fail')}{e}", "warn")
        if SOUNDFILE_AVAILABLE:
            try:
                y, sr = sf.read(path, always_2d=False)
                if y.ndim > 1:
                    y = y.mean(axis=1)
                self._log(self.t("load_sf_ok").format(sr), "ok")
                return y.astype(np.float32), sr
            except Exception as e:
                self._log(f"{self.t('load_sf_fail')}{e}", "warn")
        if LIBROSA_AVAILABLE:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                y, sr = librosa.load(path, sr=None, mono=True)
            self._log(self.t("load_librosa_ok").format(sr), "ok")
            return y, sr
        raise RuntimeError(self.t("load_none"))

    # ═══════════════════════════════════════════════════════════════════════
    #  YARDIMCI METOTLAR
    # ═══════════════════════════════════════════════════════════════════════

    def _apply_me_filter(self, data, sr):
        """İnsan sesini (300-3000Hz) SİLER. Sadece patlama, müzik ve çevre seslerini bırakır."""
        nyq = 0.5 * sr
        low = 300 / nyq
        high = 3000 / nyq
        # Bandstop filtre: Konuşma frekanslarını yok eder.
        b, a = signal.butter(4, [low, high], btype='bandstop', analog=False)
        return signal.filtfilt(b, a, data)

    @staticmethod
    def _next_pow2(n: int) -> int:
        p = 1
        while p < n:
            p <<= 1
        return p

    def _xcorr_fft(self, sig1, sig2, nfft, phat=False, phat_beta=1.0):
        F1 = np.fft.rfft(sig1, n=nfft)
        F2 = np.fft.rfft(sig2, n=nfft)
        cross = F1 * np.conj(F2)
        if phat:
            cross /= (np.abs(cross) ** phat_beta + 1e-10)
        cc = np.fft.irfft(cross, n=nfft)
        return np.fft.fftshift(cc)

    def _lag_from_cc(self, cc, nfft, sr):
        center  = nfft // 2
        max_lag = int(MAX_DELAY_MS / 1000.0 * sr)
        lo = max(0, center - max_lag)
        hi = min(len(cc), center + max_lag + 1)
        region   = cc[lo:hi]
        peak_idx = int(np.argmax(region)) + lo
        lag      = peak_idx - center
        delay_ms = (lag / sr) * 1000.0
        return delay_ms, lag

    def _feature_corr(self, o1, o2, frame_ms, name):
        o1 = (o1 - np.mean(o1)) / (np.std(o1) + 1e-10)
        o2 = (o2 - np.mean(o2)) / (np.std(o2) + 1e-10)
        corr = signal.correlate(o1, o2, mode="full", method="fft")
        lags = signal.correlation_lags(len(o1), len(o2), mode="full")
        max_lag_frames = int(MAX_DELAY_MS / frame_ms) if frame_ms > 0 else len(lags)
        center = len(lags) // 2
        lo = max(0, center - max_lag_frames)
        hi = min(len(lags), center + max_lag_frames + 1)
        region = corr[lo:hi]
        lags_r = lags[lo:hi]
        pk   = int(np.argmax(region))
        d_ms = float(lags_r[pk]) * frame_ms
        conf = float(region[pk]) / (float(np.std(corr)) + 1e-10)
        self._log(f"    {name:22s}  {d_ms:+9.1f} ms  "
                  f"conf={conf:.1f}", "default")
        return d_ms, conf

    def _fine_align(self, sig1, sig2, sr, coarse_ms, fine_range_ms):
        min_len = min(len(sig1), len(sig2))
        seg_len = min(30 * sr, min_len)
        mid     = max(0, (min_len - seg_len) // 2)
        s1 = sig1[mid:mid + seg_len]
        s2 = sig2[mid:mid + seg_len]
        n      = len(s1) + len(s2)
        nfft   = self._next_pow2(n)
        center = nfft // 2
        F1    = np.fft.rfft(s1, n=nfft)
        F2    = np.fft.rfft(s2, n=nfft)
        cross = F1 * np.conj(F2)
        cc    = np.fft.fftshift(np.fft.irfft(cross, n=nfft))
        coarse_samp = int(round(coarse_ms / 1000.0 * sr))
        # İnce ayar aralığını hata payına karşı 1.5 kat esnetiyoruz
        fine_range  = int((fine_range_ms * 1.5) / 1000.0 * sr)
        lo = max(0, center + coarse_samp - fine_range)
        hi = min(len(cc), center + coarse_samp + fine_range + 1)
        region = cc[lo:hi]
        if len(region) == 0:
            self._log(self.t("fine_empty"), "warn")
            return coarse_ms, coarse_samp
        pk       = int(np.argmax(region))
        fine_lag = (lo + pk) - center
        fine_ms  = (fine_lag / sr) * 1000.0
        self._log(self.t("fine_result").format(
            int(round(fine_ms)), coarse_ms, fine_range_ms), "ok")
        return fine_ms, fine_lag

    # ═══════════════════════════════════════════════════════════════════════
    #  MOTOR 1 — GCC-PHAT Segmented
    # ═══════════════════════════════════════════════════════════════════════
    def _eng_gcc_phat(self, sig1, sig2, sr, tune):
        self._log(self.t("eng_gcc"), "accent")
        seg_sec     = tune["seg_sec"]
        max_lag_pct = tune["max_lag_pct"]
        phat_beta   = tune.get("phat_beta", 1.0)
        seg_len     = seg_sec * sr
        min_len     = min(len(sig1), len(sig2))
        n_seg   = max(1, min_len // seg_len)
        results = []
        for i in range(n_seg):
            self._check_cancel()
            start = i * seg_len
            s1 = sig1[start:start + seg_len]
            s2 = sig2[start:start + seg_len]
            if len(s1) < sr:
                continue
            n    = len(s1) + len(s2)
            nfft = self._next_pow2(n)
            cc   = self._xcorr_fft(s1, s2, nfft, phat=True,
                                     phat_beta=phat_beta)
            center  = nfft // 2
            max_lag = int(seg_len * max_lag_pct)
            lo = max(0, center - max_lag)
            hi = min(len(cc), center + max_lag + 1)
            region = cc[lo:hi]
            pk  = int(np.argmax(region))
            lag = (lo + pk) - center
            d_ms = (lag / sr) * 1000.0
            conf = float(region[pk]) / (float(np.std(region)) + 1e-10)
            self._log(self.t("segment").format(
                i+1, n_seg, int(round(d_ms)), conf), "default")
            results.append((d_ms, conf))
        if not results:
            return 0.0, 0
        results.sort(key=lambda x: x[1], reverse=True)
        best_ms = results[0][0]
        agree = [r for r in results if abs(r[0] - best_ms) <= 500]
        if len(agree) >= 2:
            total_c  = sum(r[1] for r in agree)
            final_ms = sum(r[0]*r[1] for r in agree) / (total_c + 1e-10)
            self._log(self.t("segments_agree").format(
                len(agree), len(results), int(round(final_ms))), "ok")
        else:
            final_ms = best_ms
        final_s = int(round((final_ms / 1000.0) * sr))
        return final_ms, final_s

    # ═══════════════════════════════════════════════════════════════════════
    #  MOTOR 2 — Envelope XCorr
    # ═══════════════════════════════════════════════════════════════════════
    def _eng_envelope(self, sig1, sig2, sr, tune):
        self._log(self.t("eng_env"), "accent")
        frame_ms  = tune["frame_ms"]
        frame_len = max(1, int(frame_ms / 1000 * sr))
        min_len   = min(len(sig1), len(sig2))
        def rms_env(s):
            n   = len(s) // frame_len
            env = np.array([
                np.sqrt(np.mean(s[i*frame_len:(i+1)*frame_len] ** 2))
                for i in range(n)
            ], dtype=np.float64)
            env = env - np.mean(env)
            peak = np.max(np.abs(env))
            return env / (peak + 1e-10)
        env1 = rms_env(sig1[:min_len])
        env2 = rms_env(sig2[:min_len])
        corr = signal.correlate(env1, env2, mode="full", method="fft")
        lags = signal.correlation_lags(len(env1), len(env2), mode="full")
        max_lag_frames = int(MAX_DELAY_MS / frame_ms)
        center = len(lags) // 2
        lo = max(0, center - max_lag_frames)
        hi = min(len(lags), center + max_lag_frames + 1)
        region = corr[lo:hi]
        lags_r = lags[lo:hi]
        pk          = int(np.argmax(region))
        lag_f       = int(lags_r[pk])
        lag_samples = lag_f * frame_len
        delay_ms    = (lag_samples / sr) * 1000.0
        offset_ms   = tune.get("offset_ms", 0)
        if offset_ms:
            delay_ms   += offset_ms
            lag_samples = int(round((delay_ms / 1000.0) * sr))
            self._log(self.t("envelope_offset").format(
                int(round(delay_ms)), lag_f, frame_ms, offset_ms), "ok")
        else:
            self._log(self.t("envelope_result").format(
                int(round(delay_ms)), lag_f, frame_ms), "ok")
        return delay_ms, lag_samples

    # ═══════════════════════════════════════════════════════════════════════
    #  MOTOR 3 — NumPy FFT XCorr
    # ═══════════════════════════════════════════════════════════════════════
    def _eng_numpy(self, sig1, sig2, sr, tune):
        self._log(self.t("eng_numpy"), "accent")
        n    = len(sig1) + len(sig2)
        nfft = self._next_pow2(n)
        cc   = self._xcorr_fft(sig1, sig2, nfft, phat=False)
        delay_ms, lag = self._lag_from_cc(cc, nfft, sr)
        self._log(self.t("numpy_result").format(int(round(delay_ms))), "ok")
        return delay_ms, lag

    # ═══════════════════════════════════════════════════════════════════════
    #  MOTOR 4 — SciPy XCorr
    # ═══════════════════════════════════════════════════════════════════════
    def _eng_scipy(self, sig1, sig2, sr, tune):
        self._log(self.t("eng_scipy"), "accent")
        corr = signal.correlate(sig1, sig2, mode="full", method="fft")
        lags = signal.correlation_lags(len(sig1), len(sig2), mode="full")
        max_lag_samp = int(MAX_DELAY_MS / 1000.0 * sr)
        center = len(lags) // 2
        lo = max(0, center - max_lag_samp)
        hi = min(len(lags), center + max_lag_samp + 1)
        region = corr[lo:hi]
        lags_r = lags[lo:hi]
        pk   = int(np.argmax(region))
        lag  = int(lags_r[pk])
        delay_ms = (lag / sr) * 1000.0
        self._log(self.t("scipy_result").format(
            int(round(delay_ms)), MAX_DELAY_MS/1000), "ok")
        return delay_ms, lag

    # ═══════════════════════════════════════════════════════════════════════
    #  MOTOR 5 — Çoklu Özellik (Onset + HPSS + Chroma) + İnce Ayar
    # ═══════════════════════════════════════════════════════════════════════
    def _eng_multi(self, sig1, sig2, sr, tune, mode=None):
        self._log(self.t("eng_multi"), "accent")
        hop           = tune["hop"]
        fine_range_ms = tune["fine_range_ms"]
        min_len       = min(len(sig1), len(sig2))
        s1 = sig1[:min_len]
        s2 = sig2[:min_len]
        frame_ms = (hop / sr) * 1000.0
        results  = []
        if LIBROSA_AVAILABLE:
            s1f = s1.astype(np.float32)
            s2f = s2.astype(np.float32)
            self._log(self.t("onset_corr"), "accent")
            o1 = librosa.onset.onset_strength(y=s1f, sr=sr, hop_length=hop)
            o2 = librosa.onset.onset_strength(y=s2f, sr=sr, hop_length=hop)
            d1, c1 = self._feature_corr(o1, o2, frame_ms, "Full onset")
            results.append((d1, c1, "Full onset"))
            self._log(self.t("hpss_perc"), "accent")
            D1 = librosa.stft(s1f, n_fft=2048, hop_length=hop)
            D2 = librosa.stft(s2f, n_fft=2048, hop_length=hop)
            _, P1 = librosa.decompose.hpss(D1, margin=3.0)
            _, P2 = librosa.decompose.hpss(D2, margin=3.0)
            s1p = librosa.istft(P1, hop_length=hop,
                                length=min_len).astype(np.float32)
            s2p = librosa.istft(P2, hop_length=hop,
                                length=min_len).astype(np.float32)
            o1n = librosa.onset.onset_strength(y=s1p, sr=sr, hop_length=hop)
            o2n = librosa.onset.onset_strength(y=s2p, sr=sr, hop_length=hop)
            d2, c2 = self._feature_corr(o1n, o2n, frame_ms,
                                         "Percussive onset (HPSS)")
            results.append((d2, c2, "Percussive onset (HPSS)"))
            self._log(self.t("perc_rms"), "accent")
            try:
                p_rms_win = int(0.05 * sr)
                n_pr = min(len(s1p), len(s2p)) // p_rms_win
                if n_pr > 50:
                    pe1 = np.array([np.sqrt(np.mean(
                        s1p[j*p_rms_win:(j+1)*p_rms_win] ** 2))
                        for j in range(n_pr)])
                    pe2 = np.array([np.sqrt(np.mean(
                        s2p[j*p_rms_win:(j+1)*p_rms_win] ** 2))
                        for j in range(n_pr)])
                    p_frame_ms = p_rms_win / sr * 1000.0
                    d3, c3 = self._feature_corr(
                        pe1, pe2, p_frame_ms, "Percussive RMS")
                    results.append((d3, c3, "Percussive RMS"))
            except Exception as e:
                self._log(f"{self.t('perc_rms_fail')}{e}", "warn")
            self._log(self.t("rms_env"), "accent")
            RMS_MS  = 100
            rms_win = int(RMS_MS / 1000 * sr)
            n_rms   = min_len // rms_win
            if n_rms > 50:
                env1 = np.array([np.sqrt(np.mean(
                    s1[i*rms_win:(i+1)*rms_win] ** 2))
                    for i in range(n_rms)])
                env2 = np.array([np.sqrt(np.mean(
                    s2[i*rms_win:(i+1)*rms_win] ** 2))
                    for i in range(n_rms)])
                d4, c4 = self._feature_corr(env1, env2, float(RMS_MS),
                                             "RMS envelope")
                results.append((d4, c4, "RMS envelope"))
            self._log(self.t("chromagram"), "accent")
            ch1 = librosa.feature.chroma_stft(y=s1f, sr=sr, hop_length=hop)
            ch2 = librosa.feature.chroma_stft(y=s2f, sr=sr, hop_length=hop)
            best_ch_d, best_ch_c = 0.0, 0.0
            for pc in range(12):
                cd, cc_ = self._feature_corr(
                    ch1[pc], ch2[pc], frame_ms, f"Chroma {pc:2d}")
                if cc_ > best_ch_c:
                    best_ch_d, best_ch_c = cd, cc_
            results.append((best_ch_d, best_ch_c, "Chromagram"))
            ch_sum1 = np.sum(ch1, axis=0)
            ch_sum2 = np.sum(ch2, axis=0)
            d6, c6 = self._feature_corr(ch_sum1, ch_sum2, frame_ms,
                                         "Chroma sum")
            results.append((d6, c6, "Chroma sum"))
        else:
            self._log(self.t("no_librosa_flux"), "warn")
            frame_len = hop
            n_frames  = min_len // frame_len
            def spectral_flux(sig_in):
                frames = np.array([
                    np.abs(np.fft.rfft(
                        sig_in[i*frame_len:(i+1)*frame_len]))
                    for i in range(n_frames)])
                return np.maximum(0, np.diff(frames, axis=0)).sum(axis=1)
            o1 = spectral_flux(s1)
            o2 = spectral_flux(s2)
            d1, c1 = self._feature_corr(o1, o2, frame_ms, "Spectral flux")
            results.append((d1, c1, "Spectral flux"))
        if not results:
            return 0.0, 0
        results.sort(key=lambda x: x[1], reverse=True)
        self._log(self.t("summary"), "accent")
        for d, c, name in results:
            self._log(f"    {name:22s}  {d:+9.1f} ms  conf={c:.1f}",
                      "default")
        best = results[0]
        agree = [r for r in results if abs(r[0] - best[0]) <= 500]
        if len(agree) >= 2:
            total_c   = sum(r[1] for r in agree)
            coarse_ms = sum(r[0]*r[1] for r in agree) / (total_c+1e-10)
            self._log(self.t("methods_agree").format(
                len(agree), len(results), int(round(coarse_ms))), "ok")
        else:
            coarse_ms = best[0]
        self._log(self.t("fine_tune"), "accent")
        fine_ms, fine_lag = self._fine_align(
            sig1, sig2, sr, coarse_ms, fine_range_ms)
        if abs(fine_ms - coarse_ms) <= fine_range_ms:
            final_ms = fine_ms
            final_s  = fine_lag
        else:
            final_ms = coarse_ms
            final_s  = int(round(coarse_ms / 1000.0 * sr))
            self._log(self.t("fine_drift").format(
                int(round(final_ms))), "warn")
        return final_ms, final_s

    # ═══════════════════════════════════════════════════════════════════════
    #  MOTOR 6 — 2 Aşamalı (RMS Kaba + FFT İnce)
    # ═══════════════════════════════════════════════════════════════════════
    def _eng_two_pass(self, sig1, sig2, sr, tune):
        self._log(self.t("eng_two"), "accent")
        frame_ms      = tune["frame_ms"]
        fine_range_ms = tune["fine_range_ms"]
        self._log(self.t("coarse_label"), "accent")
        frame_len = max(1, int(frame_ms / 1000 * sr))
        min_len   = min(len(sig1), len(sig2))
        def rms_env(s):
            n   = len(s) // frame_len
            env = np.array([
                np.sqrt(np.mean(s[i*frame_len:(i+1)*frame_len] ** 2))
                for i in range(n)
            ], dtype=np.float64)
            env = (env - np.mean(env)) / (np.std(env) + 1e-10)
            return env
        env1 = rms_env(sig1[:min_len])
        env2 = rms_env(sig2[:min_len])
        corr = signal.correlate(env1, env2, mode="full", method="fft")
        lags = signal.correlation_lags(len(env1), len(env2), mode="full")
        max_lag_frames = int(MAX_DELAY_MS / frame_ms)
        center = len(lags) // 2
        lo = max(0, center - max_lag_frames)
        hi = min(len(lags), center + max_lag_frames + 1)
        region = corr[lo:hi]
        lags_r = lags[lo:hi]
        pk        = int(np.argmax(region))
        lag_f     = int(lags_r[pk])
        coarse_ms = (lag_f * frame_len / sr) * 1000.0
        self._log(self.t("coarse_result").format(
            int(round(coarse_ms)), lag_f, frame_ms), "ok")
        self._log(self.t("fine_phase2"), "accent")
        fine_ms, fine_lag = self._fine_align(
            sig1, sig2, sr, coarse_ms, fine_range_ms)
        if abs(fine_ms - coarse_ms) <= fine_range_ms:
            final_ms = fine_ms
            final_s  = fine_lag
            self._log(self.t("fine_ok").format(int(round(final_ms))), "ok")
        else:
            final_ms = coarse_ms
            final_s  = int(round(coarse_ms / 1000.0 * sr))
            self._log(self.t("fine_drift").format(
                int(round(final_ms))), "warn")
        return final_ms, final_s

    # ═══════════════════════════════════════════════════════════════════════
    #  MOTOR 7 — Otomatik (Akıllı Analiz)
    # ═══════════════════════════════════════════════════════════════════════

    def _vad_binary_mask(self, sig, sr, frame_ms=30):
        frame_len = max(1, int(frame_ms / 1000.0 * sr))
        n_frames  = len(sig) // frame_len
        if n_frames < 10:
            return np.array([])
        energy = np.array([
            np.sqrt(np.mean(sig[i*frame_len:(i+1)*frame_len] ** 2))
            for i in range(n_frames)
        ], dtype=np.float64)
        threshold = np.median(energy) + 0.5 * np.std(energy)
        mask = (energy > threshold).astype(np.float64)
        return mask

    def _env_macro(self, sig, sr, frame_ms=200):
        frame_len = max(1, int(frame_ms / 1000.0 * sr))
        n_frames  = len(sig) // frame_len
        if n_frames < 10:
            return np.array([])
        env = np.array([
            np.sqrt(np.mean(sig[i*frame_len:(i+1)*frame_len] ** 2))
            for i in range(n_frames)
        ], dtype=np.float64)
        env = env - np.mean(env)
        peak = np.max(np.abs(env))
        if peak > 1e-10:
            env /= peak
        return env

    def _correlate_with_limit(self, a, b, frame_ms):
        if len(a) == 0 or len(b) == 0:
            return 0.0, 0.0
        a = (a - np.mean(a)) / (np.std(a) + 1e-10)
        b = (b - np.mean(b)) / (np.std(b) + 1e-10)
        corr = signal.correlate(a, b, mode="full", method="fft")
        lags = signal.correlation_lags(len(a), len(b), mode="full")
        max_lag = int(MAX_DELAY_MS / frame_ms) if frame_ms > 0 else len(lags)
        center  = len(lags) // 2
        lo = max(0, center - max_lag)
        hi = min(len(lags), center + max_lag + 1)
        region = corr[lo:hi]
        lags_r = lags[lo:hi]
        pk = int(np.argmax(region))
        d_ms = float(lags_r[pk]) * frame_ms
        conf = float(region[pk]) / (float(np.std(corr)) + 1e-10)
        return d_ms, conf

    def _eng_auto(self, y1, y2, sr, tune):
        self._log("═" * 52, "accent")
        self._log(self.t("eng_auto_title"), "accent")
        self._log(self.t("eng_auto_raw"), "ok")
        self._log("═" * 52, "accent")

        vad_frame_ms = tune["vad_frame_ms"]
        env_frame_ms = tune["env_frame_ms"]
        drift_check  = tune.get("drift_check", True)
        min_len      = min(len(y1), len(y2))
        results      = []

        # ── Yöntem 1: VAD ──
        self._log(self.t("vad_title"), "accent")
        self._log(self.t("vad_desc"), "default")
        self._check_cancel()
        mask1 = self._vad_binary_mask(y1[:min_len], sr, vad_frame_ms)
        mask2 = self._vad_binary_mask(y2[:min_len], sr, vad_frame_ms)
        if len(mask1) > 10 and len(mask2) > 10:
            d_vad, c_vad = self._correlate_with_limit(
                mask1, mask2, vad_frame_ms)
            self._log(self.t("vad_result").format(
                int(round(d_vad)), c_vad), "ok")
            results.append((d_vad, c_vad, "VAD"))

        # ── Yöntem 2: Enerji Zarfı ──
        self._log(self.t("env_title"), "accent")
        self._check_cancel()
        env1 = self._env_macro(y1[:min_len], sr, env_frame_ms)
        env2 = self._env_macro(y2[:min_len], sr, env_frame_ms)
        if len(env1) > 10 and len(env2) > 10:
            d_env, c_env = self._correlate_with_limit(
                env1, env2, env_frame_ms)
            self._log(self.t("env_result").format(
                int(round(d_env)), c_env), "ok")
            results.append((d_env, c_env, "Energy Envelope"))

        # ── Yöntem 3: HPSS ──
        self._log(self.t("hpss_title"), "accent")
        self._check_cancel()
        if LIBROSA_AVAILABLE:
            try:
                s1f = y1[:min_len].astype(np.float32)
                s2f = y2[:min_len].astype(np.float32)
                D1 = librosa.stft(s1f, n_fft=2048, hop_length=512)
                D2 = librosa.stft(s2f, n_fft=2048, hop_length=512)
                _, P1 = librosa.decompose.hpss(D1, margin=3.0)
                _, P2 = librosa.decompose.hpss(D2, margin=3.0)
                self._check_cancel()
                p1 = librosa.istft(P1, hop_length=512, length=min_len)
                p2 = librosa.istft(P2, hop_length=512, length=min_len)
                p_env1 = self._env_macro(p1, sr, 50)
                p_env2 = self._env_macro(p2, sr, 50)
                if len(p_env1) > 10 and len(p_env2) > 10:
                    d_hpss, c_hpss = self._correlate_with_limit(
                        p_env1, p_env2, 50.0)
                    self._log(self.t("hpss_result").format(
                        int(round(d_hpss)), c_hpss), "ok")
                    results.append((d_hpss, c_hpss, "HPSS"))
            except Exception as e:
                self._log(f"{self.t('hpss_fail')}{e}", "warn")
        else:
            self._log(self.t("hpss_no_librosa"), "warn")

        # ── Yöntem 4: Onset ──
        if LIBROSA_AVAILABLE:
            self._log(self.t("onset_title"), "accent")
            self._check_cancel()
            try:
                hop = 512
                o1 = librosa.onset.onset_strength(
                    y=s1f, sr=sr, hop_length=hop)
                o2 = librosa.onset.onset_strength(
                    y=s2f, sr=sr, hop_length=hop)
                o_frame_ms = (hop / sr) * 1000.0
                d_onset, c_onset = self._correlate_with_limit(
                    o1, o2, o_frame_ms)
                self._log(self.t("onset_result").format(
                    int(round(d_onset)), c_onset), "ok")
                results.append((d_onset, c_onset, "Onset"))
            except Exception as e:
                self._log(f"{self.t('onset_fail')}{e}", "warn")

        # ═══ KONSENSÜS ═══
        self._log("═" * 52, "accent")
        self._log(self.t("consensus"), "accent")
        self._check_cancel()

        if not results:
            self._log(self.t("no_results"), "err")
            return 0.0, 0

        results.sort(key=lambda x: x[1], reverse=True)
        for d, c, name in results:
            marker = "✅" if c > 5 else "⚠️" if c > 2 else "❌"
            self._log(f"  {marker} {name:20s}  {d:+9.1f} ms  "
                      f"conf={c:.1f}", "default")

        best = results[0]
        agree = [r for r in results if abs(r[0] - best[0]) <= 200]
        disagree = [r for r in results if abs(r[0] - best[0]) > 200]

        if len(agree) >= 2:
            total_c = sum(r[1] for r in agree)
            final_ms = sum(r[0] * r[1] for r in agree) / (total_c + 1e-10)
            self._log(self.t("methods_agree").format(
                len(agree), len(results), int(round(final_ms))), "ok")
        elif len(results) >= 2 and len(disagree) == len(results) - 1:
            self._log(self.t("methods_disagree"), "warn")
            final_ms = best[0]
        else:
            final_ms = best[0]

        # ═══ DRIFT ═══
        drift_warning = False
        if drift_check and min_len > sr * 180:
            self._log(self.t("drift_title"), "accent")
            self._check_cancel()
            seg_dur = min(60 * sr, min_len // 3)
            seg_positions = [
                (self.t("drift_start"), 0),
                (self.t("drift_mid"),   (min_len - seg_dur) // 2),
                (self.t("drift_end"),   min_len - seg_dur),
            ]
            drift_results = []
            for seg_name, start in seg_positions:
                e1 = self._env_macro(
                    y1[start:start + seg_dur], sr, env_frame_ms)
                e2 = self._env_macro(
                    y2[start:start + seg_dur], sr, env_frame_ms)
                if len(e1) > 10 and len(e2) > 10:
                    d_seg, c_seg = self._correlate_with_limit(
                        e1, e2, env_frame_ms)
                    self._log(f"  {seg_name:10s}: {int(round(d_seg)):+d} ms  "
                              f"(conf: {c_seg:.1f})", "default")
                    if c_seg > 3:
                        drift_results.append(d_seg)

            if len(drift_results) >= 2:
                drift = abs(max(drift_results) - min(drift_results))
                self._log(self.t("drift_max").format(drift), "default")
                if drift > 500:
                    drift_warning = True
                    self._log("", "default")
                    self._log("⚠️" * 20, "err")
                    self._log(self.t("drift_detected"), "err")
                    self._log(self.t("drift_amount").format(drift), "err")
                    self._log(self.t("drift_cause"), "err")
                    self._log(self.t("drift_fix"), "err")
                    self._log(self.t("drift_solution"), "err")
                    self._log("⚠️" * 20, "err")
                else:
                    self._log(self.t("drift_none").format(drift), "ok")

        # ═══ SYNC UYARISI ═══
        if len(results) >= 3 and len(agree) <= 1:
            self._log("", "default")
            self._log("⚠️" * 20, "warn")
            self._log(self.t("sync_warn_title"), "warn")
            self._log(self.t("sync_warn_desc"), "warn")
            self._log(self.t("sync_warn_hint"), "warn")
            self._log(self.t("sync_warn_reasons"), "warn")
            self._log(self.t("sync_warn_r1"), "warn")
            self._log(self.t("sync_warn_r2"), "warn")
            self._log(self.t("sync_warn_r3"), "warn")
            self._log("⚠️" * 20, "warn")

        final_s = int(round(final_ms / 1000.0 * sr))
        self._log("═" * 52, "accent")
        self._log(self.t("final_result").format(int(round(final_ms))),
                  "accent")
        if drift_warning:
            self._log(self.t("drift_active"), "warn")
        return final_ms, final_s

    # ── Zaman Formatlama ─────────────────────────────────────────────────────
    @staticmethod
    def _fmt_delay(ms: float) -> str:
        total = int(abs(ms))
        h     = total // 3_600_000;  r    = total % 3_600_000
        m     = r    //    60_000;   r    = r     %    60_000
        s     = r    //     1_000;   ms_r = r     %     1_000
        if h:
            return f"{h:02d}:{m:02d}:{s:02d}.{ms_r:03d}"
        if m:
            return f"{m:02d}:{s:02d}.{ms_r:03d}"
        return f"{s:02d}.{ms_r:03d} sn"

    # ── Sonuç Göster ─────────────────────────────────────────────────────────
    def _show_results(self, delay_ms, fmt, direction, eng_label):
        abs_ms = abs(delay_ms)
        color  = (GREEN if abs_ms < 100
                  else YELLOW if abs_ms < 1000
                  else RED)
        if abs_ms == 0:
            color = GREEN

        self.lbl_ms.configure(text=f"{int(round(delay_ms)):+d} ms", fg=color)
        self.lbl_fmt.configure(text=fmt, fg=color)

        if delay_ms > 10:
            dir_short = self.t("dir_short_a2")
        elif delay_ms < -10:
            dir_short = self.t("dir_short_a1")
        else:
            dir_short = self.t("dir_short_sync")
        self.lbl_dir.configure(
            text=dir_short,
            fg=ACCENT if abs(delay_ms) > 10 else GREEN)

        short_eng = eng_label.split("(")[0].strip()
        if len(short_eng) > 18:
            short_eng = short_eng[:16] + "…"
        self.lbl_eng.configure(text=short_eng, fg=MUTED)
        self._done()

    def _done(self):
        self.progress.stop()
        self._cancelled = False
        self.analyze_btn.configure(state="normal",
                                   text=self.t("btn_start"))
        self.cancel_btn.configure(state="disabled")
        self.manual_btn.configure(state="normal",
                                  text=self.t("manual_btn"))

    # ── Hakkında (Butonlu — resme benzer) ─────────────────────────────────
    def _show_about(self):
        w = tk.Toplevel(self.root)
        w.title(self.t("about_title"))
        w.geometry("500x740")
        w.configure(bg=CARD)
        w.resizable(False, False)
        w.transient(self.root)
        w.grab_set()

        # Başlık
        tk.Label(w, text="🎵  Audio Delay Detector",
                 bg=CARD, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(pady=(22, 4))
        tk.Label(w, text=self.t("about_version"),
                 bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack()
        tk.Frame(w, bg=BORDER, height=1).pack(fill="x", padx=24, pady=14)

        # ── Geliştirici ──
        tk.Label(w, text=f"👨‍💻  {self.t('about_dev')}:  {self.t('about_dev_val')}",
                 bg=CARD, fg=TEXT, font=("Segoe UI", 11)).pack(pady=(0, 10))

        # ── Butonlar (Web / GitHub / E-Posta) ──
        btn_frame = tk.Frame(w, bg=CARD)
        btn_frame.pack(fill="x", padx=36, pady=(0, 4))

        tk.Button(btn_frame, text=self.t("about_web_btn"),
                  command=lambda: webbrowser.open("https://www.mrtogras.com"),
                  bg=BTN_BG, fg=ACCENT, font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=16, pady=7,
                  cursor="hand2").pack(fill="x", pady=(0, 5))

        tk.Button(btn_frame, text=self.t("about_github_btn"),
                  command=lambda: webbrowser.open("https://github.com/MrTOgRaS"),
                  bg=BTN_BG, fg=ACCENT, font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=16, pady=7,
                  cursor="hand2").pack(fill="x", pady=(0, 5))

        tk.Button(btn_frame, text=self.t("about_mail_btn"),
                  command=lambda: webbrowser.open("mailto:destek@mrtogras.com"),
                  bg=BTN_BG, fg=ACCENT, font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=16, pady=7,
                  cursor="hand2").pack(fill="x", pady=(0, 5))

        tk.Frame(w, bg=BORDER, height=1).pack(fill="x", padx=24, pady=10)

        # ── MIT Lisansı / Program Bilgileri / Bağış ──
        btn_frame2 = tk.Frame(w, bg=CARD)
        btn_frame2.pack(fill="x", padx=36, pady=(0, 4))

        tk.Button(btn_frame2, text=self.t("about_mit"),
                  command=lambda: self._show_mit_license(w),
                  bg=BTN_BG, fg=ACCENT, font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=16, pady=7,
                  cursor="hand2").pack(fill="x", pady=(0, 5))

        tk.Button(btn_frame2, text=self.t("about_info"),
                  command=lambda: self._show_program_info(w),
                  bg=BTN_BG, fg=ACCENT, font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=16, pady=7,
                  cursor="hand2").pack(fill="x", pady=(0, 5))

        tk.Button(btn_frame2, text=self.t("about_donate"),
                  command=lambda: webbrowser.open("https://mrtogras.com/support/"),
                  bg="#e94560", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=16, pady=7,
                  cursor="hand2").pack(fill="x", pady=(0, 5))

        tk.Frame(w, bg=BORDER, height=1).pack(fill="x", padx=24, pady=10)

        # ── Kütüphaneler (basit etiketler, link yok) ──
        tk.Label(w, text=self.t("about_libs"),
                 bg=CARD, fg=MUTED, font=("Segoe UI", 9, "bold")).pack()
        libs_frame = tk.Frame(w, bg=CARD)
        libs_frame.pack(pady=(4, 0))
        libs_row1 = ["NumPy", "SciPy", "pydub"]
        libs_row2 = ["soundfile", "librosa", "FFmpeg"]
        for row_libs in [libs_row1, libs_row2]:
            row = tk.Frame(libs_frame, bg=CARD)
            row.pack(pady=2)
            for lib in row_libs:
                tk.Label(row, text=lib, bg=BTN_BG, fg=TEXT,
                         font=("Consolas", 8, "bold"),
                         padx=8, pady=2).pack(side="left", padx=2)

        tk.Frame(w, bg=BORDER, height=1).pack(fill="x", padx=24, pady=10)

        # ── Desteklenen Formatlar ──
        tk.Label(w, text=self.t("about_formats"),
                 bg=CARD, fg=MUTED, font=("Segoe UI", 9, "bold")).pack()
        fmt_frame = tk.Frame(w, bg=CARD)
        fmt_frame.pack(pady=(4, 0))
        formats_row1 = ["MKV", "MP4", "AVI", "MOV", "WMV"]
        formats_row2 = ["MP3", "FLAC", "AAC", "AC3", "EAC3", "DTS", "WAV"]
        for row_formats in [formats_row1, formats_row2]:
            row = tk.Frame(fmt_frame, bg=CARD)
            row.pack(pady=2)
            for fmt in row_formats:
                tk.Label(row, text=fmt, bg=BTN_BG, fg=TEXT,
                         font=("Consolas", 8, "bold"),
                         padx=8, pady=2).pack(side="left", padx=2)

        # ── Kapat ──
        tk.Frame(w, bg=BORDER, height=1).pack(fill="x", padx=24, pady=8)
        tk.Button(w, text=self.t("about_close"),
                  command=w.destroy,
                  bg=BTN_BG, fg=TEXT, relief="flat",
                  padx=16, pady=6, cursor="hand2").pack(pady=(0, 10))

    # ── Program Bilgileri penceresi ────────────────────────────────────────
    def _show_program_info(self, parent):
        w = tk.Toplevel(parent)
        w.title(self.t("about_info_title"))
        w.geometry("480x400")
        w.configure(bg=CARD)
        w.resizable(False, False)
        w.transient(parent)
        w.grab_set()

        tk.Label(w, text=f"ℹ️  {self.t('about_info_title')}",
                 bg=CARD, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(pady=(16, 8))

        # Kombine bilgi
        tk.Label(w, text=self.t("about_combo"),
                 bg=CARD, fg=ACCENT,
                 font=("Segoe UI", 11, "bold")).pack(pady=(4, 10))

        tk.Frame(w, bg=BORDER, height=1).pack(fill="x", padx=24, pady=4)

        # Motorlar
        tk.Label(w, text=self.t("about_engines"),
                 bg=CARD, fg=MUTED, font=("Segoe UI", 10, "bold")).pack(pady=(8, 4))
        engines_frame = tk.Frame(w, bg=CARD)
        engines_frame.pack(pady=(0, 6))
        engines = ["GCC-PHAT", "Envelope", "NumPy FFT", "SciPy", "Multi Feature", "2-Pass"]
        eng_row = tk.Frame(engines_frame, bg=CARD)
        eng_row.pack()
        for eng in engines[:3]:
            tk.Label(eng_row, text=eng, bg=BTN_BG, fg=ACCENT,
                     font=("Consolas", 9), padx=8, pady=3).pack(side="left", padx=3)
        eng_row2 = tk.Frame(engines_frame, bg=CARD)
        eng_row2.pack(pady=(4, 0))
        for eng in engines[3:]:
            tk.Label(eng_row2, text=eng, bg=BTN_BG, fg=ACCENT,
                     font=("Consolas", 9), padx=8, pady=3).pack(side="left", padx=3)

        tk.Frame(w, bg=BORDER, height=1).pack(fill="x", padx=24, pady=8)

        # Modlar
        tk.Label(w, text=self.t("about_modes"),
                 bg=CARD, fg=MUTED, font=("Segoe UI", 10, "bold")).pack(pady=(4, 4))
        for mode_key in ["about_modes_old", "about_modes_anim", "about_modes_new"]:
            tk.Label(w, text=self.t(mode_key), bg=CARD, fg=TEXT,
                     font=("Segoe UI", 10)).pack(pady=2)

        tk.Frame(w, bg=BORDER, height=1).pack(fill="x", padx=24, pady=10)

        tk.Button(w, text=self.t("about_close"),
                  command=w.destroy,
                  bg=BTN_BG, fg=TEXT, relief="flat",
                  padx=16, pady=6, cursor="hand2").pack(pady=(0, 12))

    # ── MIT Lisansı penceresi ─────────────────────────────────────────────
    def _show_mit_license(self, parent):
        w = tk.Toplevel(parent)
        w.title(self.t("mit_title"))
        w.geometry("560x440")
        w.configure(bg=CARD)
        w.resizable(False, False)
        w.transient(parent)
        w.grab_set()

        tk.Label(w, text=f"📜  {self.t('mit_title')}",
                 bg=CARD, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(pady=(16, 8))

        txt = scrolledtext.ScrolledText(
            w, bg=BG, fg=TEXT, font=("Consolas", 9),
            relief="flat", wrap="word", insertbackground=TEXT)
        txt.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        txt.insert("1.0", MIT_LICENSE_TEXT)
        txt.configure(state="disabled")

        tk.Button(w, text=self.t("about_close"),
                  command=w.destroy,
                  bg=BTN_BG, fg=TEXT, relief="flat",
                  padx=16, pady=6, cursor="hand2").pack(pady=(0, 12))


# ── Başlangıç ────────────────────────────────────────────────────────────────
def main():
    root = tk.Tk()
    try:
        import sys, os
        if getattr(sys, 'frozen', False):
            base = sys._MEIPASS
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        ico = os.path.join(base, "icon.ico")
        if os.path.exists(ico):
            root.iconbitmap(default=ico)
    except Exception:
        pass
    AudioDelayApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
