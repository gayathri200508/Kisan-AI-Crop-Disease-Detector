# 🌿 Kisan AI — Crop Disease Detector

**AI-Powered Crop Disease Detection for Every Indian Farmer**

🏆 India Innovates 2026 | Team BRIGHT | AITS Tirupati, Andhra Pradesh

---

## About

Kisan AI is a real-time AI-powered crop disease detection app built for Indian farmers. Upload a photo of your crop or leaf — the app instantly detects the disease, explains why it formed, and gives treatment and fertilizer recommendations in your own regional language.

India has 140 crore people and over 60% depend on agriculture. Crop diseases cause ₹50,000+ crore losses every year. Kisan AI brings AI-powered diagnosis directly to farmers — free, fast, and in their language.

---

## Features

- AI Disease Detection powered by Llama 4 Vision via Groq API
- 10 Indian Languages — Telugu, Hindi, Marathi, Tamil, Kannada, Bengali, Odia, Punjabi, Gujarati, English
- Detailed Analysis — symptoms, cause, treatment, fertilizers, prevention tips
- Specific fertilizer and spray recommendations with dosage
- Supports 15+ crops — Tomato, Rice, Wheat, Maize, Potato, Chilli, Cotton, Soybean and more
- Real-time results in seconds
- 100% Free for all farmers

---

## Tech Stack

- Frontend: Streamlit
- AI Model: Llama 4 Scout 17B Vision via Groq API
- Translation: Deep Translator
- Image Processing: Pillow
- Language: Python 3.10+

---

## Installation

```bash
git clone https://github.com/gayathri200508/Kisan-AI-Crop-Disease-Detector.git
cd Kisan-AI-Crop-Disease-Detector
pip install streamlit groq deep-translator Pillow
```

Get a free Groq API key from https://console.groq.com, add it to line 4 of `app.py`, then run:

```bash
streamlit run app.py
```

---

## How It Works

1. Farmer uploads a crop or leaf image
2. Image is analyzed by Groq AI (Llama 4 Vision)
3. AI detects disease, severity, symptoms, and cause
4. Results are translated into the farmer's language
5. Treatment, fertilizers, and prevention tips are displayed

---

## Team BRIGHT

- Gollapolu Gayathri
- Gomitra
- Bhargavi

Annamacharya Institute of Technology and Sciences (AITS), Tirupati
B.Tech — Artificial Intelligence and Data Science

---

Built with ❤️ for 140 Crore Indian Farmers | India Innovates 2026 | Bharat Mandapam, New Delhi
