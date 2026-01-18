import streamlit as st
from openai import OpenAI
import json
from html2image import Html2Image
import os

# 1. Konfigurasi OpenAI dari Secrets Streamlit
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 2. Konfigurasi Renderer Gambar (PENTING untuk Streamlit Cloud)
hti = Html2Image(browser='chromium', custom_flags=['--no-sandbox', '--disable-dev-shm-usage', '--headless'])

# 3. Fungsi AI Analisa
def analyze_recipe(raw_text):
    prompt = f"""
    Kamu adalah Chef Profesional. Rapikan resep ini ke JSON.
    Lengkapi yang kurang, perbaiki bahasa, beri trik memasak.
    Resep: {raw_text}
    Format JSON:
    {{
        "judul": "...",
        "deskripsi": "...",
        "bahan": ["..."],
        "langkah": ["..."],
        "trik": ["..."]
    }}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    return json.loads(response.choices[0].message.content)

# 4. Tampilan Web Streamlit
st.set_page_config(page_title="AI Poster Resep", layout="wide")
st.title("🍳 Generator Poster Resep AI")

user_input = st.text_area("Masukkan resep kasar di sini (Contoh: cara buat mie goreng instan pake telor):")

if st.button("Generate Poster!"):
    if user_input:
        with st.spinner("Sedang meracik desain..."):
            # Analisa AI
            data = analyze_recipe(user_input)
            
            # Template HTML (Bisa dikustomisasi nanti)
            html_content = f"""
            <div id="poster" style="width: 500px; padding: 30px; background: #fff; border: 10px solid #f39c12; font-family: sans-serif;">
                <h1 style="color: #e67e22; text-align: center;">{data['judul']}</h1>
                <p style="text-align: center; color: #7f8c8d;"><i>{data['deskripsi']}</i></p>
                <hr>
                <h3 style="color: #d35400;">Bahan Utama:</h3>
                <ul>{"".join([f"<li>{b}</li>" for b in data['bahan']])}</ul>
                <h3 style="color: #2980b9;">Langkah Memasak:</h3>
                <ol>{"".join([f"<li>{l}</li>" for l in data['langkah']])}</ol>
                <div style="background: #ecf0f1; padding: 10px; border-radius: 5px;">
                    <h4 style="margin-top:0;">💡 Trik Chef:</h4>
                    <ul>{"".join([f"<li>{t}</li>" for t in data['trik']])}</ul>
                </div>
            </div>
            """
            
            # Tampilkan Preview
            st.components.v1.html(html_content, height=800, scrolling=True)
            
            # Simpan jadi gambar
            hti.screenshot(html_str=html_content, save_as='poster.png')
            
            # Tombol Download
            with open("poster.png", "rb") as file:
                st.download_button("Download Poster (PNG)", file, "poster_resep.png", "image/png")
    else:
        st.error("Isi dulu resepnya ya!")
