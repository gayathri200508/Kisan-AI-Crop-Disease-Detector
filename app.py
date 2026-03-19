import streamlit as st
from PIL import Image
from groq import Groq
from deep_translator import GoogleTranslator
import base64
import json
import re

API_KEY = st.secrets["GROQ_API_KEY"]

LANGUAGES = {
    "🇬🇧 English": "en",
    "🌾 తెలుగు": "te",
    "🇮🇳 हिंदी": "hi",
    "🟠 मराठी": "mr",
    "🌴 தமிழ்": "ta",
    "⭐ ಕನ್ನಡ": "kn",
    "🐟 বাংলা": "bn",
    "🌊 ଓଡ଼ିଆ": "or",
    "🦁 ਪੰਜਾਬੀ": "pa",
    "💎 ગુજરાતી": "gu",
}

UI_LABELS = {
    "en": {
        "title": "Kisan AI", "subtitle": "AI-Powered Crop Disease Detector for Every Indian Farmer",
        "badge": "🏆 India Innovates 2026 · Team BRIGHT · AITS Tirupati",
        "diseases": "Diseases Detected", "languages": "Indian Languages",
        "crops_count": "Crop Varieties", "free": "For All Farmers",
        "select_lang": "🌐 Select Your Language", "upload": "📸 Upload Crop / Leaf Image",
        "supported": "JPG, JPEG, PNG supported", "analyze_btn": "🔍 Analyze Disease Now",
        "result_title": "📋 Analysis Result", "upload_prompt": "Upload a crop image and click",
        "upload_sub": "AI detects disease, severity, treatment & prevention in seconds",
        "crop_label": "Crop", "disease_label": "Disease", "severity_label": "Severity",
        "urgency_label": "Urgency", "confidence_label": "Confidence",
        "symptoms_label": "🔬 Symptoms Observed", "cause_label": "🧫 Why This Disease Forms",
        "treatment_label": "💊 Recommended Treatment", "fertilizer_label": "🧪 Fertilizers & Sprays",
        "prevention_label": "🛡️ Prevention Tips", "healthy_msg": "✅ Your Crop is Healthy!",
        "supported_crops": "🌾 Supported Crops", "analyzing": "🤖 AI is analyzing your crop...",
        "footer": "Team BRIGHT | AITS Tirupati, Andhra Pradesh | India Innovates 2026 | Bharat Mandapam, New Delhi",
    },
    "te": {
        "title": "కిసాన్ AI", "subtitle": "ప్రతి భారతీయ రైతుకు AI ఆధారిత పంట వ్యాధి డిటెక్టర్",
        "badge": "🏆 ఇండియా ఇన్నోవేట్స్ 2026 · టీమ్ BRIGHT · AITS తిరుపతి",
        "diseases": "వ్యాధులు గుర్తించబడ్డాయి", "languages": "భారతీయ భాషలు",
        "crops_count": "పంట రకాలు", "free": "రైతులందరికీ ఉచితం",
        "select_lang": "🌐 మీ భాష ఎంచుకోండి", "upload": "📸 పంట / ఆకు చిత్రం అప్‌లోడ్ చేయండి",
        "supported": "JPG, JPEG, PNG మద్దతు ఉంది", "analyze_btn": "🔍 వ్యాధిని విశ్లేషించండి",
        "result_title": "📋 విశ్లేషణ ఫలితం", "upload_prompt": "పంట చిత్రాన్ని అప్‌లోడ్ చేసి క్లిక్ చేయండి",
        "upload_sub": "AI వ్యాధి, తీవ్రత, చికిత్స సెకన్లలో చెప్తుంది",
        "crop_label": "పంట", "disease_label": "వ్యాధి", "severity_label": "తీవ్రత",
        "urgency_label": "అత్యవసరం", "confidence_label": "విశ్వసనీయత",
        "symptoms_label": "🔬 గమనించిన లక్షణాలు", "cause_label": "🧫 ఈ వ్యాధి ఎందుకు వస్తుంది",
        "treatment_label": "💊 సిఫార్సు చేసిన చికిత్స", "fertilizer_label": "🧪 ఎరువులు & స్ప్రేలు",
        "prevention_label": "🛡️ నివారణ చిట్కాలు", "healthy_msg": "✅ మీ పంట ఆరోగ్యంగా ఉంది!",
        "supported_crops": "🌾 మద్దతు ఉన్న పంటలు", "analyzing": "🤖 AI మీ పంటను విశ్లేషిస్తోంది...",
        "footer": "టీమ్ BRIGHT | AITS తిరుపతి, ఆంధ్రప్రదేశ్ | ఇండియా ఇన్నోవేట్స్ 2026 | భారత్ మండపం, న్యూఢిల్లీ",
    },
    "hi": {
        "title": "किसान AI", "subtitle": "हर भारतीय किसान के लिए AI आधारित फसल रोग पहचानकर्ता",
        "badge": "🏆 इंडिया इनोवेट्स 2026 · टीम BRIGHT · AITS तिरुपति",
        "diseases": "बीमारियाँ पहचानी गईं", "languages": "भारतीय भाषाएँ",
        "crops_count": "फसल किस्में", "free": "सभी किसानों के लिए मुफ़्त",
        "select_lang": "🌐 अपनी भाषा चुनें", "upload": "📸 फसल / पत्ती की छवि अपलोड करें",
        "supported": "JPG, JPEG, PNG समर्थित", "analyze_btn": "🔍 रोग विश्लेषण करें",
        "result_title": "📋 विश्लेषण परिणाम", "upload_prompt": "फसल की छवि अपलोड करें और क्लिक करें",
        "upload_sub": "AI रोग, गंभीरता और उपचार सेकंडों में बताएगा",
        "crop_label": "फसल", "disease_label": "बीमारी", "severity_label": "गंभीरता",
        "urgency_label": "तत्कालता", "confidence_label": "विश्वसनीयता",
        "symptoms_label": "🔬 देखे गए लक्षण", "cause_label": "🧫 यह रोग क्यों होता है",
        "treatment_label": "💊 अनुशंसित उपचार", "fertilizer_label": "🧪 उर्वरक और स्प्रे",
        "prevention_label": "🛡️ रोकथाम के उपाय", "healthy_msg": "✅ आपकी फसल स्वस्थ है!",
        "supported_crops": "🌾 समर्थित फसलें", "analyzing": "🤖 AI आपकी फसल का विश्लेषण कर रहा है...",
        "footer": "टीम BRIGHT | AITS तिरुपति, आंध्र प्रदेश | इंडिया इनोवेट्स 2026 | भारत मंडपम, नई दिल्ली",
    },
}

def get_ui(lang, key):
    d = UI_LABELS.get(lang, UI_LABELS["en"])
    return d.get(key, UI_LABELS["en"].get(key, key))

CROP_EMOJIS = {
    "tomato": "🍅", "rice": "🌾", "wheat": "🌿", "maize": "🌽",
    "potato": "🥔", "chilli": "🌶️", "cotton": "🪴", "soybean": "🫘",
    "onion": "🧅", "grapes": "🍇", "sugarcane": "🎋", "groundnut": "🥜",
}

st.set_page_config(page_title="Kisan AI", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
    * { font-family: 'Poppins', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0a2e0a 0%, #1a4a1a 50%, #0d3d1a 100%); }
    .hero { background: linear-gradient(135deg, #00c853, #1b5e20); border-radius: 24px; padding: 40px; text-align: center; margin-bottom: 30px; box-shadow: 0 20px 60px rgba(0,200,83,0.3); position: relative; overflow: hidden; }
    .hero::before { content: "🌾🌿🍅🌽🥔🌾🌿"; position: absolute; top: 10px; left: 0; right: 0; font-size: 1.5rem; opacity: 0.2; letter-spacing: 20px; }
    .hero-title { font-size: 3.5rem; font-weight: 800; color: white; margin: 0; text-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .hero-sub { font-size: 1.1rem; color: rgba(255,255,255,0.85); margin-top: 8px; }
    .hero-badge { display: inline-block; background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.4); border-radius: 50px; padding: 6px 20px; font-size: 0.85rem; color: white; margin-top: 15px; }
    .stat-card { background: rgba(255,255,255,0.08); border: 1px solid rgba(0,200,83,0.3); border-radius: 16px; padding: 20px; text-align: center; }
    .stat-number { font-size: 2.2rem; font-weight: 800; color: #00e676; line-height: 1; }
    .stat-label { font-size: 0.78rem; color: rgba(255,255,255,0.7); margin-top: 5px; text-transform: uppercase; letter-spacing: 1px; }
    .section-title { font-size: 1.3rem; font-weight: 700; color: #00e676; margin-bottom: 12px; margin-top: 20px; }
    .info-row { background: rgba(255,255,255,0.06); border-left: 4px solid #00e676; border-radius: 0 12px 12px 0; padding: 12px 18px; margin: 8px 0; color: white; }
    .info-warn { background: rgba(255,193,7,0.1); border-left: 4px solid #ffc107; border-radius: 0 12px 12px 0; padding: 12px 18px; margin: 8px 0; color: white; }
    .info-danger { background: rgba(255,82,82,0.1); border-left: 4px solid #ff5252; border-radius: 0 12px 12px 0; padding: 12px 18px; margin: 8px 0; color: white; }
    .detail-box { border-radius: 16px; padding: 18px; margin: 8px 0; color: white; line-height: 1.9; font-size: 0.95rem; }
    .green-box { background: linear-gradient(135deg, rgba(0,200,83,0.15), rgba(0,100,41,0.1)); border: 1px solid rgba(0,200,83,0.3); }
    .blue-box { background: linear-gradient(135deg, rgba(33,150,243,0.15), rgba(13,71,161,0.1)); border: 1px solid rgba(33,150,243,0.3); }
    .yellow-box { background: linear-gradient(135deg, rgba(255,193,7,0.15), rgba(230,120,0,0.1)); border: 1px solid rgba(255,193,7,0.3); }
    .orange-box { background: linear-gradient(135deg, rgba(255,152,0,0.15), rgba(230,81,0,0.1)); border: 1px solid rgba(255,152,0,0.3); }
    .disease-badge { background: linear-gradient(135deg, #ff5252, #b71c1c); color: white; padding: 8px 20px; border-radius: 50px; font-weight: 700; font-size: 1rem; display: inline-block; box-shadow: 0 4px 15px rgba(255,82,82,0.4); }
    .healthy-badge { background: linear-gradient(135deg, #00c853, #1b5e20); color: white; padding: 8px 20px; border-radius: 50px; font-weight: 700; font-size: 1rem; display: inline-block; box-shadow: 0 4px 15px rgba(0,200,83,0.4); }
    .crop-chip { background: rgba(0,200,83,0.15); border: 1px solid rgba(0,200,83,0.3); border-radius: 50px; padding: 4px 14px; font-size: 0.8rem; color: #00e676; display: inline-block; margin: 3px; }
    .placeholder-box { background: rgba(0,0,0,0.3); border-radius: 20px; padding: 60px 25px; text-align: center; border: 1px solid rgba(0,200,83,0.15); }
    .footer { text-align: center; padding: 30px; color: rgba(255,255,255,0.35); font-size: 0.82rem; margin-top: 40px; border-top: 1px solid rgba(255,255,255,0.08); }
    .stButton > button { background: linear-gradient(135deg, #00c853, #1b5e20) !important; color: white !important; border: none !important; border-radius: 12px !important; font-weight: 700 !important; font-size: 1.1rem !important; padding: 14px !important; box-shadow: 0 8px 25px rgba(0,200,83,0.4) !important; }
    .stSelectbox > div > div { background: rgba(255,255,255,0.08) !important; border: 1px solid rgba(0,200,83,0.3) !important; border-radius: 12px !important; color: white !important; }
    label { color: rgba(255,255,255,0.8) !important; }
    [data-testid="stImage"] img { border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.5); }
</style>
""", unsafe_allow_html=True)

def img_to_b64(data):
    return base64.b64encode(data).decode()

def translate(text, lang):
    if lang == "en" or not text:
        return text
    try:
        return GoogleTranslator(source="en", target=lang).translate(str(text))
    except:
        return text

def analyze(img_bytes, lang_code):
    client = Groq(api_key=API_KEY)
    b64 = img_to_b64(img_bytes)
    prompt = """You are an expert agricultural scientist helping Indian farmers.
Analyze this crop/leaf image. Return ONLY valid JSON, no markdown, no extra text:
{
  "crop": "crop name",
  "disease": "disease name or Healthy Plant",
  "severity": "Healthy or Mild or Moderate or Severe",
  "symptoms": "describe visible symptoms in 2-3 clear sentences",
  "cause": "explain why this disease forms - mention soil conditions, weather, fungus/bacteria/pest cause in 2 sentences",
  "treatment": "Step 1: action here. Step 2: action here. Step 3: action here.",
  "fertilizers": "Fertilizer 1: name and dosage. Fertilizer 2: name and dosage. Spray: chemical name and frequency.",
  "prevention": "Tip 1: advice. Tip 2: advice. Tip 3: advice.",
  "urgency": "Low or Medium or High",
  "confidence": "87"
}"""

    resp = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
            {"type": "text", "text": prompt}
        ]}],
        max_tokens=900,
        temperature=0.2
    )

    raw = resp.choices[0].message.content
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match:
        return {"error": raw}

    result = json.loads(match.group())

    if lang_code != "en":
        for f in ["crop", "disease", "severity", "symptoms", "cause", "treatment", "fertilizers", "prevention", "urgency"]:
            if f in result:
                try:
                    result[f] = GoogleTranslator(source="en", target=lang_code).translate(str(result[f]))
                except:
                    pass
    return result

def sev_style(s):
    s = (s or "").lower()
    if any(w in s for w in ["healthy", "ఆరోగ్య", "स्वस्थ", "ஆரோக்கிய"]):
        return "info-row", "🟢"
    elif any(w in s for w in ["mild", "మిత", "हल्क", "low", "తక్కువ"]):
        return "info-warn", "🟡"
    elif any(w in s for w in ["moderate", "మధ్య", "मध्यम", "medium", "మధ్యస్థం"]):
        return "info-warn", "🟠"
    else:
        return "info-danger", "🔴"

if "lang" not in st.session_state:
    st.session_state.lang = "en"

top_l, top_r = st.columns([4, 1])
with top_r:
    lang_sel = st.selectbox("", list(LANGUAGES.keys()), label_visibility="collapsed")
    st.session_state.lang = LANGUAGES[lang_sel]

lang = st.session_state.lang

st.markdown(f"""
<div class="hero">
    <div class="hero-title">🌿 {get_ui(lang, 'title')}</div>
    <div class="hero-sub">{get_ui(lang, 'subtitle')}</div>
    <div class="hero-badge">{get_ui(lang, 'badge')}</div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
for col, num, key in zip([c1,c2,c3,c4], ["50+","10","15+","FREE"], ["diseases","languages","crops_count","free"]):
    with col:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{num}</div><div class="stat-label">{get_ui(lang,key)}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
left, right = st.columns([1, 1], gap="large")

with left:
    st.markdown(f'<div class="section-title">{get_ui(lang,"upload")}</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(get_ui(lang, "supported"), type=["jpg","jpeg","png"])

    if uploaded:
        st.image(Image.open(uploaded), use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button(get_ui(lang,"analyze_btn"), use_container_width=True)
    else:
        st.markdown(f'<div style="background:rgba(255,255,255,0.03);border:2px dashed rgba(0,200,83,0.3);border-radius:16px;padding:50px;text-align:center;color:rgba(255,255,255,0.4);"><div style="font-size:3rem">📷</div><div style="margin-top:10px">{get_ui(lang,"upload_prompt")}</div></div>', unsafe_allow_html=True)
        analyze_btn = False

    st.markdown(f'<div class="section-title">{get_ui(lang,"supported_crops")}</div>', unsafe_allow_html=True)
    crops = ["🍅 Tomato","🌾 Rice","🌿 Wheat","🌽 Maize","🥔 Potato","🌶️ Chilli","🪴 Cotton","🫘 Soybean","🧅 Onion","🍇 Grapes","🎋 Sugarcane","🥜 Groundnut","🌻 Sunflower","🫑 Capsicum"]
    st.markdown("".join([f'<span class="crop-chip">{c}</span>' for c in crops]), unsafe_allow_html=True)

with right:
    st.markdown(f'<div class="section-title">{get_ui(lang,"result_title")}</div>', unsafe_allow_html=True)

    if uploaded and analyze_btn:
        with st.spinner(get_ui(lang,"analyzing")):
            result = analyze(uploaded.getvalue(), lang)

        if "error" in result:
            st.error(f"Error: {result['error']}")
        else:
            is_healthy = "healthy" in result.get("disease","").lower()
            if is_healthy:
                st.markdown(f'<div class="healthy-badge">{get_ui(lang,"healthy_msg")}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="disease-badge">⚠️ {result.get("disease","")}</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            crop_emoji = next((v for k,v in CROP_EMOJIS.items() if k in result.get("crop","").lower()), "🌿")
            sev_class, sev_emoji = sev_style(result.get("severity",""))
            urg_class, urg_emoji = sev_style(result.get("urgency",""))

            st.markdown(f'<div class="info-row">{crop_emoji} <b>{get_ui(lang,"crop_label")}:</b> {result.get("crop","N/A")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="{sev_class}">{sev_emoji} <b>{get_ui(lang,"severity_label")}:</b> {result.get("severity","N/A")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="{urg_class}">{urg_emoji} <b>{get_ui(lang,"urgency_label")}:</b> {result.get("urgency","N/A")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-row">🎯 <b>{get_ui(lang,"confidence_label")}:</b> {result.get("confidence","N/A")}%</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            for label_key, field, box_class in [
                ("symptoms_label", "symptoms", "green-box"),
                ("cause_label", "cause", "yellow-box"),
                ("treatment_label", "treatment", "green-box"),
                ("fertilizer_label", "fertilizers", "orange-box"),
                ("prevention_label", "prevention", "blue-box"),
            ]:
                with st.expander(get_ui(lang, label_key), expanded=True):
                    st.markdown(f'<div class="detail-box {box_class}">{result.get(field,"N/A")}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="placeholder-box"><div style="font-size:4rem">🌿</div><div style="color:rgba(255,255,255,0.55);font-size:1.05rem;margin-top:15px;">{get_ui(lang,"upload_prompt")}<br><b style="color:#00e676">{get_ui(lang,"analyze_btn")}</b></div><div style="margin-top:15px;color:rgba(255,255,255,0.3);font-size:0.85rem;">{get_ui(lang,"upload_sub")}</div></div>', unsafe_allow_html=True)

st.markdown(f'<div class="footer">{get_ui(lang,"footer")}<br><span style="color:rgba(255,255,255,0.18)">Powered by Groq AI · Llama 4 · Built with ❤️ for 140 Crore Indian Farmers</span></div>', unsafe_allow_html=True)