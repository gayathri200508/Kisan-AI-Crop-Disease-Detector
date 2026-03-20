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

PLANT_CATEGORIES = {
    "🌾 Crops": ["Rice", "Wheat", "Maize", "Sorghum", "Bajra", "Barley"],
    "🥦 Vegetables": ["Tomato", "Potato", "Onion", "Brinjal", "Okra", "Cauliflower", "Cabbage", "Spinach", "Bitter Gourd", "Pumpkin", "Cucumber", "Carrot"],
    "🍎 Fruits": ["Mango", "Banana", "Guava", "Papaya", "Pomegranate", "Grapes", "Watermelon", "Pineapple", "Lemon", "Orange", "Coconut", "Jackfruit"],
    "🌶️ Spices": ["Chilli", "Turmeric", "Ginger", "Garlic", "Coriander", "Cumin", "Cardamom", "Pepper", "Clove"],
    "🌿 Medicinal": ["Tulsi", "Neem", "Aloe Vera", "Ashwagandha", "Brahmi", "Giloy", "Amla", "Moringa"],
    "🌸 Flowers": ["Rose", "Jasmine", "Marigold", "Lotus", "Hibiscus", "Sunflower", "Lily", "Orchid"],
    "🌳 Trees": ["Coconut", "Teak", "Sandalwood", "Bamboo", "Neem Tree", "Peepal", "Banyan", "Tamarind"],
    "☕ Plantation": ["Tea", "Coffee", "Rubber", "Sugarcane", "Cotton", "Jute", "Arecanut"],
    "🫘 Pulses": ["Chickpea", "Lentil", "Black Gram", "Green Gram", "Pigeon Pea", "Soybean", "Groundnut"],
    "🌻 Oilseeds": ["Sunflower", "Mustard", "Sesame", "Castor", "Safflower"],
}

UI_LABELS = {
    "en": {
        "title": "Kisan AI", "subtitle": "AI-Powered Plant & Crop Disease Detector for Every Indian",
        "badge": "🏆 India Innovates 2026 · Team BRIGHT · AITS Tirupati",
        "plants": "Plant Species", "languages": "Indian Languages", "categories": "Plant Categories", "free": "For Everyone",
        "upload": "📸 Upload Plant / Leaf Image", "supported": "JPG, JPEG, PNG supported",
        "analyze_btn": "🔍 Diagnose Plant Now", "result_title": "📋 Diagnosis Result",
        "upload_prompt": "Upload any plant or leaf image", "upload_sub": "AI identifies plant, detects disease & gives treatment in seconds",
        "plant_label": "Plant", "severity_label": "Severity", "urgency_label": "Urgency", "confidence_label": "Confidence",
        "symptoms_label": "🔬 Symptoms Observed", "cause_label": "🧫 Why This Disease Forms",
        "treatment_label": "💊 Recommended Treatment", "fertilizer_label": "🧪 Fertilizers & Sprays",
        "prevention_label": "🛡️ Prevention Tips", "healthy_msg": "✅ Your Plant is Healthy!",
        "categories_title": "🌿 Supported Plant Categories", "analyzing": "🤖 AI is diagnosing your plant...",
        "footer": "Team BRIGHT | AITS Tirupati, Andhra Pradesh | India Innovates 2026 | Bharat Mandapam, New Delhi",
        "any_plant": "Works with ANY plant found in India — 45,000+ species supported!",
    },
    "te": {
        "title": "కిసాన్ AI", "subtitle": "ప్రతి భారతీయునికి AI ఆధారిత మొక్క & పంట వ్యాధి డిటెక్టర్",
        "badge": "🏆 ఇండియా ఇన్నోవేట్స్ 2026 · టీమ్ BRIGHT · AITS తిరుపతి",
        "plants": "మొక్కల జాతులు", "languages": "భారతీయ భాషలు", "categories": "మొక్కల వర్గాలు", "free": "అందరికీ ఉచితం",
        "upload": "📸 మొక్క / ఆకు చిత్రం అప్‌లోడ్ చేయండి", "supported": "JPG, JPEG, PNG మద్దతు ఉంది",
        "analyze_btn": "🔍 మొక్కను పరీక్షించండి", "result_title": "📋 పరీక్ష ఫలితం",
        "upload_prompt": "ఏదైనా మొక్క లేదా ఆకు చిత్రాన్ని అప్‌లోడ్ చేయండి", "upload_sub": "AI మొక్కను గుర్తించి వ్యాధి & చికిత్స సెకన్లలో చెప్తుంది",
        "plant_label": "మొక్క", "severity_label": "తీవ్రత", "urgency_label": "అత్యవసరం", "confidence_label": "విశ్వసనీయత",
        "symptoms_label": "🔬 గమనించిన లక్షణాలు", "cause_label": "🧫 ఈ వ్యాధి ఎందుకు వస్తుంది",
        "treatment_label": "💊 సిఫార్సు చేసిన చికిత్స", "fertilizer_label": "🧪 ఎరువులు & స్ప్రేలు",
        "prevention_label": "🛡️ నివారణ చిట్కాలు", "healthy_msg": "✅ మీ మొక్క ఆరోగ్యంగా ఉంది!",
        "categories_title": "🌿 మద్దతు ఉన్న మొక్కల వర్గాలు", "analyzing": "🤖 AI మీ మొక్కను పరీక్షిస్తోంది...",
        "footer": "టీమ్ BRIGHT | AITS తిరుపతి, ఆంధ్రప్రదేశ్ | ఇండియా ఇన్నోవేట్స్ 2026 | భారత్ మండపం, న్యూఢిల్లీ",
        "any_plant": "భారతదేశంలో దొరికే ఏ మొక్కకైనా పని చేస్తుంది — 45,000+ జాతులు!",
    },
    "hi": {
        "title": "किसान AI", "subtitle": "हर भारतीय के लिए AI आधारित पौधे और फसल रोग पहचानकर्ता",
        "badge": "🏆 इंडिया इनोवेट्स 2026 · टीम BRIGHT · AITS तिरुपति",
        "plants": "पौधों की प्रजातियाँ", "languages": "भारतीय भाषाएँ", "categories": "पौधों की श्रेणियाँ", "free": "सभी के लिए मुफ़्त",
        "upload": "📸 पौधे / पत्ती की छवि अपलोड करें", "supported": "JPG, JPEG, PNG समर्थित",
        "analyze_btn": "🔍 पौधे की जाँच करें", "result_title": "📋 निदान परिणाम",
        "upload_prompt": "कोई भी पौधे या पत्ती की छवि अपलोड करें", "upload_sub": "AI पौधे की पहचान करके रोग व उपचार सेकंडों में बताएगा",
        "plant_label": "पौधा", "severity_label": "गंभीरता", "urgency_label": "तत्कालता", "confidence_label": "विश्वसनीयता",
        "symptoms_label": "🔬 देखे गए लक्षण", "cause_label": "🧫 यह रोग क्यों होता है",
        "treatment_label": "💊 अनुशंसित उपचार", "fertilizer_label": "🧪 उर्वरक और स्प्रे",
        "prevention_label": "🛡️ रोकथाम के उपाय", "healthy_msg": "✅ आपका पौधा स्वस्थ है!",
        "categories_title": "🌿 समर्थित पौधों की श्रेणियाँ", "analyzing": "🤖 AI आपके पौधे का निदान कर रहा है...",
        "footer": "टीम BRIGHT | AITS तिरुपति, आंध्र प्रदेश | इंडिया इनोवेट्स 2026 | भारत मंडपम, नई दिल्ली",
        "any_plant": "भारत में पाए जाने वाले किसी भी पौधे के लिए काम करता है — 45,000+ प्रजातियाँ!",
    },
}

def get_ui(lang, key):
    d = UI_LABELS.get(lang, UI_LABELS["en"])
    return d.get(key, UI_LABELS["en"].get(key, key))

st.set_page_config(page_title="Kisan AI", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
    * { font-family: 'Poppins', sans-serif; }
    .stApp { background: linear-gradient(135deg, #071a07 0%, #0d2e0d 50%, #071a0f 100%); }
    .hero { background: linear-gradient(135deg, #00c853, #1b5e20, #004d00); border-radius: 24px; padding: 45px 40px; text-align: center; margin-bottom: 30px; box-shadow: 0 20px 60px rgba(0,200,83,0.25); position: relative; overflow: hidden; }
    .hero::before { content: "🌾🌿🍅🌳🌸🌶️🍎🌻🫘☕"; position: absolute; top: 8px; left: 0; right: 0; font-size: 1.4rem; opacity: 0.15; letter-spacing: 14px; }
    .hero::after { content: "🥦🌴🌱🎋🌺🍇🥜🌼🍃🌵"; position: absolute; bottom: 8px; left: 0; right: 0; font-size: 1.4rem; opacity: 0.15; letter-spacing: 14px; }
    .hero-title { font-size: 3.8rem; font-weight: 800; color: white; margin: 0; text-shadow: 0 4px 15px rgba(0,0,0,0.4); }
    .hero-sub { font-size: 1.1rem; color: rgba(255,255,255,0.85); margin-top: 8px; }
    .hero-badge { display: inline-block; background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.35); border-radius: 50px; padding: 6px 20px; font-size: 0.85rem; color: white; margin-top: 12px; }
    .hero-note { font-size: 0.82rem; color: rgba(255,255,255,0.6); margin-top: 10px; }
    .stat-card { background: rgba(255,255,255,0.07); border: 1px solid rgba(0,200,83,0.25); border-radius: 16px; padding: 22px; text-align: center; }
    .stat-number { font-size: 2.2rem; font-weight: 800; color: #00e676; line-height: 1; }
    .stat-label { font-size: 0.75rem; color: rgba(255,255,255,0.65); margin-top: 6px; text-transform: uppercase; letter-spacing: 1px; }
    .section-title { font-size: 1.25rem; font-weight: 700; color: #00e676; margin-bottom: 12px; margin-top: 22px; }
    .info-row { background: rgba(255,255,255,0.06); border-left: 4px solid #00e676; border-radius: 0 12px 12px 0; padding: 12px 18px; margin: 8px 0; color: white; }
    .info-warn { background: rgba(255,193,7,0.1); border-left: 4px solid #ffc107; border-radius: 0 12px 12px 0; padding: 12px 18px; margin: 8px 0; color: white; }
    .info-danger { background: rgba(255,82,82,0.1); border-left: 4px solid #ff5252; border-radius: 0 12px 12px 0; padding: 12px 18px; margin: 8px 0; color: white; }
    .detail-box { border-radius: 16px; padding: 18px; margin: 8px 0; color: white; line-height: 1.9; font-size: 0.95rem; }
    .green-box { background: linear-gradient(135deg, rgba(0,200,83,0.12), rgba(0,100,41,0.08)); border: 1px solid rgba(0,200,83,0.25); }
    .blue-box { background: linear-gradient(135deg, rgba(33,150,243,0.12), rgba(13,71,161,0.08)); border: 1px solid rgba(33,150,243,0.25); }
    .yellow-box { background: linear-gradient(135deg, rgba(255,193,7,0.12), rgba(230,120,0,0.08)); border: 1px solid rgba(255,193,7,0.25); }
    .orange-box { background: linear-gradient(135deg, rgba(255,152,0,0.12), rgba(230,81,0,0.08)); border: 1px solid rgba(255,152,0,0.25); }
    .disease-badge { background: linear-gradient(135deg, #ff5252, #b71c1c); color: white; padding: 8px 20px; border-radius: 50px; font-weight: 700; font-size: 1rem; display: inline-block; box-shadow: 0 4px 15px rgba(255,82,82,0.35); }
    .healthy-badge { background: linear-gradient(135deg, #00c853, #1b5e20); color: white; padding: 8px 20px; border-radius: 50px; font-weight: 700; font-size: 1rem; display: inline-block; box-shadow: 0 4px 15px rgba(0,200,83,0.35); }
    .category-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(0,200,83,0.18); border-radius: 14px; padding: 12px 16px; margin: 5px 0; }
    .category-title { color: #00e676; font-weight: 700; font-size: 0.88rem; margin-bottom: 6px; }
    .plant-chip { background: rgba(0,200,83,0.08); border: 1px solid rgba(0,200,83,0.18); border-radius: 50px; padding: 3px 10px; font-size: 0.72rem; color: rgba(255,255,255,0.7); display: inline-block; margin: 2px; }
    .placeholder-box { background: rgba(0,0,0,0.3); border-radius: 20px; padding: 60px 25px; text-align: center; border: 1px solid rgba(0,200,83,0.12); }
    .footer { text-align: center; padding: 30px; color: rgba(255,255,255,0.3); font-size: 0.82rem; margin-top: 40px; border-top: 1px solid rgba(255,255,255,0.07); }
    .stButton > button { background: linear-gradient(135deg, #00c853, #1b5e20) !important; color: white !important; border: none !important; border-radius: 12px !important; font-weight: 700 !important; font-size: 1.1rem !important; padding: 14px !important; box-shadow: 0 8px 25px rgba(0,200,83,0.35) !important; }
    .stSelectbox > div > div { background: rgba(255,255,255,0.07) !important; border: 1px solid rgba(0,200,83,0.25) !important; border-radius: 12px !important; color: white !important; }
    label { color: rgba(255,255,255,0.75) !important; }
    [data-testid="stImage"] img { border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.5); }
</style>
""", unsafe_allow_html=True)

def img_to_b64(data):
    return base64.b64encode(data).decode()

def analyze(img_bytes, lang_code):
    client = Groq(api_key=API_KEY)
    b64 = img_to_b64(img_bytes)
    prompt = """You are an expert botanist and agricultural scientist specializing in Indian plants.
Analyze this plant/leaf image. Return ONLY valid JSON, no markdown, no extra text:
{
  "plant": "exact plant name",
  "category": "Crop or Vegetable or Fruit or Spice or Medicinal or Flower or Tree or Plantation or Pulse or Oilseed or Other",
  "disease": "disease name or Healthy Plant",
  "severity": "Healthy or Mild or Moderate or Severe",
  "symptoms": "describe visible symptoms in 2-3 sentences",
  "cause": "explain why this disease forms in 2 sentences",
  "treatment": "Step 1: action. Step 2: action. Step 3: action.",
  "fertilizers": "Fertilizer 1: name and dosage. Spray: chemical and frequency.",
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
        max_tokens=900, temperature=0.2
    )

    raw = resp.choices[0].message.content
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match:
        return {"error": raw}

    result = json.loads(match.group())

    if lang_code != "en":
        for f in ["plant","category","disease","severity","symptoms","cause","treatment","fertilizers","prevention","urgency"]:
            if f in result:
                try:
                    result[f] = GoogleTranslator(source="en", target=lang_code).translate(str(result[f]))
                except:
                    pass
    return result

def sev_style(s):
    s = (s or "").lower()
    if any(w in s for w in ["healthy","ఆరోగ్య","स्वस्थ","ஆரோக்கிய"]):
        return "info-row", "🟢"
    elif any(w in s for w in ["mild","low","మిత","తక్కువ","हल्क"]):
        return "info-warn", "🟡"
    elif any(w in s for w in ["moderate","medium","మధ్య","मध्यम"]):
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
    <div class="hero-title">🌿 {get_ui(lang,'title')}</div>
    <div class="hero-sub">{get_ui(lang,'subtitle')}</div>
    <div class="hero-badge">{get_ui(lang,'badge')}</div>
    <div class="hero-note">✨ {get_ui(lang,'any_plant')}</div>
</div>
""", unsafe_allow_html=True)

c1,c2,c3,c4 = st.columns(4)
for col,num,key in zip([c1,c2,c3,c4],["45,000+","10","10+","FREE"],["plants","languages","categories","free"]):
    with col:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{num}</div><div class="stat-label">{get_ui(lang,key)}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
left, right = st.columns([1,1], gap="large")

with left:
    st.markdown(f'<div class="section-title">{get_ui(lang,"upload")}</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(get_ui(lang,"supported"), type=["jpg","jpeg","png"])

    if uploaded:
        st.image(Image.open(uploaded), use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button(get_ui(lang,"analyze_btn"), use_container_width=True)
    else:
        st.markdown(f'<div style="background:rgba(255,255,255,0.03);border:2px dashed rgba(0,200,83,0.3);border-radius:16px;padding:50px;text-align:center;color:rgba(255,255,255,0.4);"><div style="font-size:3rem">🌿</div><div style="margin-top:10px">{get_ui(lang,"upload_prompt")}</div></div>', unsafe_allow_html=True)
        analyze_btn = False

    st.markdown(f'<div class="section-title">{get_ui(lang,"categories_title")}</div>', unsafe_allow_html=True)
    for cat, plants in PLANT_CATEGORIES.items():
        chips = "".join([f'<span class="plant-chip">{p}</span>' for p in plants])
        st.markdown(f'<div class="category-card"><div class="category-title">{cat}</div>{chips}</div>', unsafe_allow_html=True)

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
            sev_class, sev_emoji = sev_style(result.get("severity",""))
            urg_class, urg_emoji = sev_style(result.get("urgency",""))

            st.markdown(f'<div class="info-row">🌿 <b>{get_ui(lang,"plant_label")}:</b> {result.get("plant","N/A")} &nbsp;·&nbsp; 📂 {result.get("category","")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="{sev_class}">{sev_emoji} <b>{get_ui(lang,"severity_label")}:</b> {result.get("severity","N/A")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="{urg_class}">{urg_emoji} <b>{get_ui(lang,"urgency_label")}:</b> {result.get("urgency","N/A")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-row">🎯 <b>{get_ui(lang,"confidence_label")}:</b> {result.get("confidence","N/A")}%</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            for label_key, field, box_class in [
                ("symptoms_label","symptoms","green-box"),
                ("cause_label","cause","yellow-box"),
                ("treatment_label","treatment","green-box"),
                ("fertilizer_label","fertilizers","orange-box"),
                ("prevention_label","prevention","blue-box"),
            ]:
                with st.expander(get_ui(lang,label_key), expanded=True):
                    st.markdown(f'<div class="detail-box {box_class}">{result.get(field,"N/A")}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="placeholder-box"><div style="font-size:4rem">🌿</div><div style="color:rgba(255,255,255,0.55);font-size:1.05rem;margin-top:15px;">{get_ui(lang,"upload_prompt")}<br><b style="color:#00e676">{get_ui(lang,"analyze_btn")}</b></div><div style="margin-top:15px;color:rgba(255,255,255,0.3);font-size:0.85rem;">{get_ui(lang,"upload_sub")}</div></div>', unsafe_allow_html=True)

st.markdown(f'<div class="footer">{get_ui(lang,"footer")}<br><span style="color:rgba(255,255,255,0.15)">Powered by Groq AI · Llama 4 · Built with ❤️ for India · 45,000+ Plant Species</span></div>', unsafe_allow_html=True)