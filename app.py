import streamlit as st
from openai import OpenAI
import json
from html2image import Html2Image
import base64

# 1. Inisialisasi API & Renderer
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
hti = Html2Image(browser='chromium', custom_flags=['--no-sandbox', '--disable-dev-shm-usage', '--headless'])

# 2. Fungsi Generate Gambar dengan DALL-E 3
def generate_food_image(prompt):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Professional food photography of {prompt}, top view, aesthetic plating, soft natural lighting, high resolution",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except:
        # Jika DALL-E gagal/limit, pakai placeholder estetik
        return "https://images.unsplash.com/photo-1495147466023-ac5c588e2e94?q=80&w=1000"

# 3. Fungsi AI Refinement
def refine_recipe_ai(judul, bahan, langkah, trik):
    prompt = f"""
    Kamu adalah Chef Bintang Michelin. Tugasmu merapikan resep ini agar terlihat profesional.
    Judul: {judul}
    Bahan: {bahan}
    Langkah: {langkah}
    Trik: {trik}
    
    Lengkapi bahan yang kurang, buat langkah lebih sistematis, dan poles bahasanya.
    Berikan output JSON:
    {{
        "judul": "...",
        "deskripsi": "...",
        "bahan": ["..."],
        "langkah": ["..."],
        "trik": ["..."],
        "image_prompt": "deskripsi visual singkat masakan ini untuk foto"
    }}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    return json.loads(response.choices[0].message.content)

# --- UI STREAMLIT ---
st.set_page_config(page_title="ChefArt AI", layout="wide")

# Custom CSS untuk Streamlit UI
st.markdown("""
    <style>
    .stTextArea textarea { font-size: 14px; }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎨 ChefArt AI: Recipe Poster Designer")
st.write("Isi detail resep di bawah. Biarkan AI menyempurnakan dan mendesainnya untukmu.")

# Sidebar untuk Pengaturan Tema
with st.sidebar:
    st.header("🎨 Pengaturan Desain")
    theme_color = st.color_picker("Warna Utama", "#D35400")
    font_style = st.selectbox("Gaya Font", ["Serif (Elegan)", "Sans-Serif (Modern)"])
    generate_img = st.checkbox("Gunakan AI Image (DALL-E 3)", value=True)

# Input Terbagi 2 Kolom
col_in1, col_in2 = st.columns(2)
with col_in1:
    in_judul = st.text_input("Judul Masakan", placeholder="Contoh: Telur Dadar Crispy")
    in_bahan = st.text_area("Bahan-bahan", height=150, placeholder="2 telur, garam, daun bawang...")
with col_in2:
    in_langkah = st.text_area("Cara Memasak", height=150, placeholder="Kocok telur, goreng di minyak panas...")
    in_trik = st.text_area("Trik Rahasia (Opsional)", placeholder="Gunakan api kecil agar rata...")

if st.button("🚀 Generate Aesthetic Poster", use_container_width=True):
    if not in_judul or not in_bahan:
        st.error("Minimal isi Judul dan Bahan ya!")
    else:
        with st.spinner("👨‍🍳 Chef AI sedang bekerja..."):
            # 1. Refine dengan AI
            data = refine_recipe_ai(in_judul, in_bahan, in_langkah, in_trik)
            
            # 2. Generate Image
            if generate_img:
                img_url = generate_food_image(data['image_prompt'])
            else:
                img_url = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=1000"

            # 3. Desain HTML & CSS Estetik
            font_family = "'Playfair Display', serif" if "Serif" in font_style else "'Poppins', sans-serif"
            google_font = "Playfair+Display:wght@700" if "Serif" in font_style else "Poppins:wght@400;700"
            
            html_content = f"""
            <link href="https://fonts.googleapis.com/css2?family={google_font}&display=swap" rel="stylesheet">
            <div id="poster" style="width: 600px; background: #fff; font-family: {font_family}; color: #2d3436; border-radius: 0; box-shadow: 0 20px 40px rgba(0,0,0,0.1); margin: auto;">
                <div style="height: 350px; background: url('{img_url}') no-repeat center; background-size: cover; position: relative;">
                    <div style="position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(transparent, rgba(0,0,0,0.7)); padding: 40px 20px 20px;">
                        <h1 style="color: white; margin: 0; font-size: 36px; text-transform: uppercase; letter-spacing: 2px;">{data['judul']}</h1>
                    </div>
                </div>
                
                <div style="padding: 40px; display: flex; gap: 30px;">
                    <div style="flex: 1;">
                        <h3 style="color: {theme_color}; border-bottom: 2px solid {theme_color}; padding-bottom: 5px; font-size: 18px;">BAHAN</h3>
                        <ul style="padding-left: 18px; line-height: 1.6; font-size: 13px;">
                            {"".join([f"<li style='margin-bottom:5px;'>{b}</li>" for b in data['bahan']])}
                        </ul>
                    </div>
                    <div style="flex: 1.5;">
                        <h3 style="color: {theme_color}; border-bottom: 2px solid {theme_color}; padding-bottom: 5px; font-size: 18px;">LANGKAH</h3>
                        <ol style="padding-left: 18px; line-height: 1.6; font-size: 13px;">
                            {"".join([f"<li style='margin-bottom:8px;'>{l}</li>" for l in data['langkah']])}
                        </ol>
                    </div>
                </div>

                <div style="margin: 0 40px 40px; padding: 20px; background: #fdf2f0; border-left: 5px solid {theme_color};">
                    <h4 style="margin: 0 0 5px 0; color: {theme_color}; font-size: 14px;">💡 PRO TIP</h4>
                    <p style="margin: 0; font-size: 12px; font-style: italic;">{data['trik'][0] if data['trik'] else "Masak dengan kasih sayang."}</p>
                </div>
                
                <div style="background: {theme_color}; color: white; text-align: center; padding: 10px; font-size: 10px; letter-spacing: 1px;">
                    GENERATED BY CHEFART AI • 2024
                </div>
            </div>
            """
            
            # Tampilkan di Streamlit
            st.divider()
            st.subheader("🖼️ Hasil Poster Estetik")
            st.components.v1.html(html_content, height=900)
            
            # Convert to Image
            try:
                hti.screenshot(html_str=html_content, save_as='poster_aesthetic.png')
                with open("poster_aesthetic.png", "rb") as file:
                    st.download_button("📥 Download Poster High-Res", file, "poster_resep.png", "image/png")
            except Exception as e:
                st.info("Tombol download sedang disiapkan (Server rendering)...")
