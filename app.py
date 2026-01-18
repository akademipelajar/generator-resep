import streamlit as st
from openai import OpenAI
import json
from html2image import Html2Image

# 1. SETUP
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
hti = Html2Image(browser='chromium', custom_flags=['--no-sandbox', '--disable-dev-shm-usage', '--headless'])

# 2. PROMPT AI (Refinement + Icons + Nutrition)
def get_ai_data(judul, bahan, langkah, trik):
    prompt = f"""
    Jadilah Food Scientist & Senior Designer. Analisa resep ini:
    Judul: {judul}, Bahan: {bahan}, Langkah: {langkah}, Trik: {trik}
    
    Tugas:
    1. Lengkapi resep & perbaiki bahasa.
    2. Estimasi Nutrisi (Kalori, Protein, Karbo, Lemak).
    3. Cari ikon FontAwesome 6 yang cocok untuk setiap bahan (misal: 'fa-egg', 'fa-fire-burner').
    4. Berikan output JSON:
    {{
        "judul": "...", "deskripsi": "...",
        "bahan_detail": [ {{"nama": "...", "icon": "..."}}, ... ],
        "langkah": ["..."], "trik": "...",
        "nutrisi": {{"kalori": "...", "protein": "...", "karbo": "...", "lemak": "..."}},
        "image_prompt": "..."
    }}
    """
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    return json.loads(res.choices[0].message.content)

# 3. CSS STYLE PACKAGES
def get_style(preset, format_size):
    sizes = {
        "Instagram Story (9:16)": "width: 400px; height: 711px;",
        "Square Post (1:1)": "width: 500px; height: 500px;",
        "Cetak A4": "width: 595px; height: 842px;"
    }
    base_style = sizes.get(format_size, sizes["Square Post (1:1)"])
    
    styles = {
        "Minimalist Luxury": {
            "bg": "#ffffff", "text": "#1a1a1a", "accent": "#af9164", 
            "font": "'Playfair Display', serif",
            "card": "border: 1px solid #eee; background: #fff;"
        },
        "Retro Chalkboard": {
            "bg": "#1e1e1e", "text": "#ffffff", "accent": "#feb236", 
            "font": "'Indie Flower', cursive",
            "card": "border: 2px dashed #fff; background: #262626;"
        },
        "Neon Pop Art": {
            "bg": "#0f0c29", "text": "#00f2fe", "accent": "#ff0080", 
            "font": "'Orbitron', sans-serif",
            "card": "border: none; background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); box-shadow: 0 0 15px #ff0080;"
        },
        "Homey Handwritten": {
            "bg": "#fdf5e6", "text": "#5d4037", "accent": "#8bc34a", 
            "font": "'Caveat', cursive",
            "card": "border-radius: 20px; background: #fff; box-shadow: 5px 5px 0px #8bc34a;"
        },
        "Modern Bento": {
            "bg": "#f0f2f5", "text": "#1c1e21", "accent": "#007bff", 
            "font": "'Inter', sans-serif",
            "card": "border-radius: 12px; background: #fff; border: 1px solid #e1e4e8;"
        }
    }
    return base_style, styles[preset]

# 4. HTML GENERATOR
def render_poster(data, preset, format_size, variant_id, img_url):
    dim, s = get_style(preset, format_size)
    bahan_html = "".join([f"<div style='font-size:11px; margin-bottom:5px;'><i class='fa-solid {b['icon']}' style='color:{s['accent']}; width:20px;'></i> {b['nama']}</div>" for b in data['bahan_detail']])
    langkah_html = "".join([f"<div style='font-size:11px; margin-bottom:8px;'><b>{i+1}.</b> {l}</div>" for i, l in enumerate(data['langkah'])])
    
    qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://chefart.ai/recipe/{variant_id}"

    html = f"""
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;700&family=Indie+Flower&family=Orbitron:wght@700&family=Caveat:wght@700&display=swap" rel="stylesheet">
    
    <div id="poster_{variant_id}" style="{dim} background:{s['bg']}; color:{s['text']}; font-family:{s['font']}; padding:20px; box-sizing:border-box; overflow:hidden; position:relative; border: 1px solid #ddd;">
        <div style="height:40%; background: url('{img_url}') center/cover; border-radius:10px; margin-bottom:15px; position:relative;">
            <div style="position:absolute; bottom:0; background:linear-gradient(transparent, {s['bg']}); width:100%; height:50%;"></div>
        </div>
        
        <h2 style="margin:0 0 10px 0; font-size:24px; color:{s['accent']}; text-transform:uppercase;">{data['judul']}</h2>
        
        <div style="display:flex; gap:15px; height:45%;">
            <div style="flex:1; {s['card']} padding:10px; border-radius:8px;">
                <span style="font-size:12px; font-weight:bold; color:{s['accent']};">BAHAN</span><br><br>
                {bahan_html}
            </div>
            <div style="flex:1.5; {s['card']} padding:10px; border-radius:8px;">
                <span style="font-size:12px; font-weight:bold; color:{s['accent']};">LANGKAH</span><br><br>
                {langkah_html}
            </div>
        </div>

        <div style="position:absolute; bottom:15px; left:20px; right:20px; display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:9px; opacity:0.8;">
                🔥 {data['nutrisi']['kalori']} kkal | 💪 P: {data['nutrisi']['protein']} | 🍞 K: {data['nutrisi']['karbo']}
            </div>
            <img src="{qr_api}" style="width:40px; height:40px; border:2px solid {s['accent']}; background:white;">
        </div>
    </div>
    """
    return html

# 5. STREAMLIT UI
st.set_page_config(page_title="ChefArt AI 2026", layout="wide")

with st.sidebar:
    st.header("🎨 Design Workspace")
    sel_style = st.selectbox("Style Pack", ["Minimalist Luxury", "Retro Chalkboard", "Neon Pop Art", "Homey Handwritten", "Modern Bento"])
    sel_format = st.radio("Layout Format", ["Instagram Story (9:16)", "Square Post (1:1)", "Cetak A4"])
    st.divider()
    use_ai_img = st.toggle("Generate AI Image (DALL-E 3)", True)

st.title("👨‍🍳 ChefArt AI v3.0")
st.write("Visualisasikan resepmu dengan trend desain 2026.")

c1, c2 = st.columns(2)
with c1:
    in_judul = st.text_input("Nama Menu", "Telur Dadar Crispy")
    in_bahan = st.text_area("Bahan", "Telur, tepung beras, bawang merah, garam", height=100)
with c2:
    in_langkah = st.text_area("Cara Masak", "Kocok telur dengan bumbu, goreng kering.", height=100)
    in_trik = st.text_input("Trik Rahasia", "Gunakan minyak yang benar-benar panas")

if st.button("🪄 GENERATE 2 VARIATIONS", use_container_width=True):
    with st.spinner("AI sedang merancang 2 opsi desain terbaik..."):
        # 1. Get Data
        recipe_data = get_ai_data(in_judul, in_bahan, in_langkah, in_trik)
        
        # 2. Get Image
        img_url = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=1000"
        if use_ai_img:
            img_res = client.images.generate(model="dall-e-3", prompt=recipe_data['image_prompt'], size="1024x1024", n=1)
            img_url = img_res.data[0].url
        
        # 3. Render 2 Options
        col_res1, col_res2 = st.columns(2)
        
        # Opsi A: Sesuai Pilihan User
        with col_res1:
            st.subheader("Opsi A: Pilihanmu")
            html_a = render_poster(recipe_data, sel_style, sel_format, "A", img_url)
            st.components.v1.html(html_a, height=850, scrolling=True)
            hti.screenshot(html_str=html_a, save_as='opsi_a.png')
            with open("opsi_a.png", "rb") as f:
                st.download_button("Download Opsi A", f, "Opsi_A.png", "image/png")

        # Opsi B: AI Recommendation (Selalu Modern Bento atau Pop Art sebagai pembanding)
        with col_res2:
            st.subheader("Opsi B: Rekomendasi AI")
            alt_style = "Modern Bento" if sel_style != "Modern Bento" else "Neon Pop Art"
            html_b = render_poster(recipe_data, alt_style, sel_format, "B", img_url)
            st.components.v1.html(html_b, height=850, scrolling=True)
            hti.screenshot(html_str=html_b, save_as='opsi_b.png')
            with open("opsi_b.png", "rb") as f:
                st.download_button("Download Opsi B", f, "Opsi_B.png", "image/png")

                # Tambahkan flags lebih lengkap untuk mematikan fitur desktop yang tidak perlu di server
hti = Html2Image(
    browser='chromium', 
    custom_flags=[
        '--no-sandbox', 
        '--disable-dev-shm-usage', 
        '--headless', 
        '--disable-gpu', 
        '--hide-scrollbars',
        '--disable-software-rasterizer'
    ]
)
