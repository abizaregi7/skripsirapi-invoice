import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os
from datetime import datetime

# ─── Register Poppins for PDF ──────────────────────────────────────────────────
FONT_DIR = os.path.dirname(os.path.abspath(__file__))

def register_fonts():
    variants = [
        ("Poppins",        "Poppins-Regular.ttf"),
        ("Poppins-Bold",   "Poppins-Bold.ttf"),
        ("Poppins-Medium", "Poppins-Medium.ttf"),
    ]
    for name, fname in variants:
        path = os.path.join(FONT_DIR, fname)
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
            except Exception:
                pass

register_fonts()

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SkripsiRapi Invoice Generator",
    page_icon="📄",
    layout="centered",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"], .stMarkdown, .stTextInput input,
    .stNumberInput input, .stTextArea textarea, .stRadio label,
    button, label, p, div { font-family: 'Poppins', sans-serif !important; }
    .main { background-color: #FAF8F5; }
    .section-label {
        font-size: 0.68rem; font-weight: 600; letter-spacing: 0.12em;
        text-transform: uppercase; color: #1A2B4A; margin-bottom: 0.75rem;
        padding-bottom: 0.5rem; border-bottom: 2px solid #D4AF6A; display: inline-block;
    }
    .stButton > button {
        background: linear-gradient(135deg, #D4AF6A, #c9a55a) !important;
        color: #1A2B4A !important; font-weight: 600 !important; font-size: 1rem !important;
        border: none !important; border-radius: 10px !important;
        padding: 0.7rem 2rem !important; width: 100% !important;
        font-family: 'Poppins', sans-serif !important;
    }
    .footer { text-align:center; color:#aaa; font-size:0.75rem; margin-top:3rem;
               padding-top:1rem; border-top:1px solid #eee; }
    .footer a { color:#D4AF6A; text-decoration:none; }
    hr { border-color:#E8E2D9; }
</style>
""", unsafe_allow_html=True)

# ─── Header ────────────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 4])
with col_logo:
    logo_path = os.path.join(FONT_DIR, "logo.jpg")
    if os.path.exists(logo_path):
        st.image(logo_path, width=80)
with col_title:
    st.markdown("""
    <div style="padding-top:0.5rem;">
        <div style="font-size:1.5rem;font-weight:700;color:#1A2B4A;">SkripsiRapi</div>
        <div style="font-size:0.82rem;color:#888;margin-top:2px;">Invoice PDF Generator · Format Skripsi Profesional</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ─── Client Info ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">📋 Informasi Klien</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    nama_klien = st.text_input("Nama Klien", placeholder="Nama lengkap / institusi")
    no_invoice = st.text_input("Nomor Invoice", value=f"INV-{datetime.now().strftime('%Y%m%d%H%M')}")
with c2:
    email_klien = st.text_input("Email / WhatsApp", placeholder="email@domain.com / 08xx")
    tanggal = st.date_input("Tanggal Invoice", value=datetime.today())
catatan = st.text_area("Catatan / Keterangan", placeholder="Judul skripsi, universitas, atau instruksi khusus...", height=80)
st.markdown("---")

# ─── Layanan ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">⚙️ Rincian Layanan</div>', unsafe_allow_html=True)

with st.expander("📄 Jumlah Halaman", expanded=True):
    jumlah_halaman = st.number_input("Jumlah halaman total", min_value=0, value=0, step=1)
    harga_halaman = st.radio("Harga per halaman", options=[1000, 2000],
        format_func=lambda x: f"Rp {x:,}/halaman {'(Standard)' if x==1000 else '(Premium)'}", horizontal=True)
    subtotal_halaman = jumlah_halaman * harga_halaman

with st.expander("🖼️ Gambar (termasuk Daftar Gambar)"):
    jumlah_gambar = st.number_input("Jumlah gambar", min_value=0, value=0, step=1)
    subtotal_gambar = jumlah_gambar * 1000

with st.expander("📊 Tabel (termasuk Daftar Tabel)"):
    jumlah_tabel = st.number_input("Jumlah tabel", min_value=0, value=0, step=1)
    subtotal_tabel = jumlah_tabel * 1000

with st.expander("📎 Lampiran (termasuk Daftar Lampiran)"):
    jumlah_lampiran = st.number_input("Jumlah lampiran", min_value=0, value=0, step=1)
    subtotal_lampiran = jumlah_lampiran * 1000

with st.expander("🔢 Numbering per Section"):
    jumlah_section = st.number_input("Jumlah section", min_value=0, value=0, step=1)
    subtotal_numbering = jumlah_section * 1000

with st.expander("📑 Daftar Isi"):
    ada_daftar_isi = st.radio("Perlu pembuatan Daftar Isi?", ["Tidak", "Ya"], horizontal=True)
    subtotal_daftar_isi = 0
    jml_bab = jml_sub_bab = jml_sub_sub_bab = 0
    if ada_daftar_isi == "Ya":
        col_b, col_sb, col_ssb = st.columns(3)
        with col_b: jml_bab = st.number_input("Jumlah Bab", min_value=0, value=0, step=1)
        with col_sb: jml_sub_bab = st.number_input("Jumlah Sub Bab", min_value=0, value=0, step=1)
        with col_ssb: jml_sub_sub_bab = st.number_input("Jumlah Sub Sub Bab", min_value=0, value=0, step=1)
        total_entri_doi = jml_bab + jml_sub_bab + jml_sub_sub_bab
        subtotal_daftar_isi = total_entri_doi * 500
        st.caption(f"Total entri: {total_entri_doi} × Rp 500 = **Rp {subtotal_daftar_isi:,}**")

grand_total = subtotal_halaman + subtotal_gambar + subtotal_tabel + subtotal_lampiran + subtotal_numbering + subtotal_daftar_isi

# ─── Summary ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-label">💰 Ringkasan Biaya</div>', unsafe_allow_html=True)

for label, qty, price, sub in [
    ("Halaman", jumlah_halaman, harga_halaman, subtotal_halaman),
    ("Gambar & Daftar Gambar", jumlah_gambar, 1000, subtotal_gambar),
    ("Tabel & Daftar Tabel", jumlah_tabel, 1000, subtotal_tabel),
    ("Lampiran & Daftar Lampiran", jumlah_lampiran, 1000, subtotal_lampiran),
    ("Numbering Section", jumlah_section, 1000, subtotal_numbering),
    ("Daftar Isi", None, None, subtotal_daftar_isi),
]:
    if sub > 0 or (qty is not None and qty > 0):
        detail = f"{qty} × Rp {price:,}" if qty is not None else f"Rp {sub:,}"
        ca, cb = st.columns([3, 1])
        ca.markdown(f"<span style='color:#555'>{label}</span> <small style='color:#aaa'>({detail})</small>", unsafe_allow_html=True)
        cb.markdown(f"<div style='text-align:right;font-weight:500'>Rp {sub:,}</div>", unsafe_allow_html=True)

st.markdown(f"""
<div style="background:#1A2B4A;border-radius:10px;padding:1rem 1.5rem;margin-top:1rem;
            display:flex;justify-content:space-between;align-items:center;">
    <span style="color:#c8d0df;font-size:0.9rem;">TOTAL BIAYA</span>
    <span style="color:#D4AF6A;font-size:1.4rem;font-weight:700;">Rp {grand_total:,}</span>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)


# ─── PDF Generator ─────────────────────────────────────────────────────────────
def generate_pdf(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    NAVY  = colors.HexColor("#1A2B4A")
    GOLD  = colors.HexColor("#D4AF6A")
    LGRAY = colors.HexColor("#E8E2D9")
    GRAY  = colors.HexColor("#888888")
    DARK  = colors.HexColor("#222222")
    WHITE = colors.white

    P  = "Poppins"
    PB = "Poppins-Bold"
    PM = "Poppins-Medium"

    def ps(name, font=P, size=9, color=DARK, align=TA_LEFT):
        return ParagraphStyle(name, fontName=font, fontSize=size,
                              textColor=color, alignment=align,
                              leading=size * 1.5, spaceAfter=0, spaceBefore=0)

    story = []
    fmt = lambda n: f"Rp {n:,}"

    # ── HEADER: two separate column groups, no nested tables for logo ─────────
    logo_path = os.path.join(FONT_DIR, "logo.jpg")

    # Build left content as list of paragraphs
    left_items = []
    if os.path.exists(logo_path):
        left_items.append(Image(logo_path, width=1.6*cm, height=1.6*cm))
    left_items.append(Spacer(1, 4))
    left_items.append(Paragraph("SkripsiRapi", ps("brand", font=PB, size=14, color=NAVY)))
    left_items.append(Paragraph("Format Skripsi Profesional", ps("sub", font=P, size=8, color=GRAY)))
    left_items.append(Paragraph("instagram.com/skripsirapi", ps("ig", font=P, size=8, color=GRAY)))

    right_items = [
        Paragraph("INVOICE", ps("inv_h", font=PB, size=22, color=NAVY, align=TA_RIGHT)),
        Spacer(1, 4),
        Paragraph(data["no_invoice"], ps("inv_no", font=P, size=8, color=GRAY, align=TA_RIGHT)),
        Paragraph(f"Tanggal: {data['tanggal']}", ps("inv_dt", font=P, size=8, color=GRAY, align=TA_RIGHT)),
    ]

    hdr = Table([[left_items, right_items]], colWidths=[10*cm, 7*cm])
    hdr.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=0.4*cm))

    # ── Client info ──────────────────────────────────────────────────────────
    client_tbl = Table([
        [Paragraph("DITAGIHKAN KEPADA", ps("ch", font=PB, size=8, color=NAVY)),
         Paragraph("KETERANGAN", ps("ch2", font=PB, size=8, color=NAVY))],
        [Paragraph(data["nama_klien"] or "—", ps("cn", font=PM, size=10, color=DARK)),
         Paragraph(data["catatan"] or "—", ps("cc", font=P, size=8.5, color=colors.HexColor("#555555")))],
        [Paragraph(data["email_klien"] or "", ps("ce", font=P, size=8, color=GRAY)),
         Paragraph("", ps("ce2"))],
    ], colWidths=[8.5*cm, 8.5*cm])
    client_tbl.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ]))
    story.append(client_tbl)
    story.append(Spacer(1, 0.5*cm))

    # ── Items table ──────────────────────────────────────────────────────────
    def th(text, align=TA_LEFT):
        return Paragraph(text, ps(f"th_{text[:6]}", font=PB, size=8.5, color=WHITE, align=align))

    tdata = [[th("LAYANAN"), th("QTY", TA_CENTER), th("HARGA SATUAN", TA_RIGHT), th("SUBTOTAL", TA_RIGHT)]]

    def make_row(label, qty, price, sub, note=""):
        lp = [Paragraph(label, ps(f"rl{id(label)}", font=PM, size=9, color=DARK))]
        if note:
            lp.append(Paragraph(note, ps(f"rn{id(label)}", font=P, size=7.5, color=GRAY)))
        return [
            lp,
            Paragraph(str(qty) if qty is not None else "—", ps(f"rq{id(label)}", font=P, size=9, color=DARK, align=TA_CENTER)),
            Paragraph(fmt(price) if price is not None else "—", ps(f"rp{id(label)}", font=P, size=9, color=DARK, align=TA_RIGHT)),
            Paragraph(fmt(sub), ps(f"rs{id(label)}", font=PM, size=9, color=DARK, align=TA_RIGHT)),
        ]

    if data["jumlah_halaman"] > 0:
        tdata.append(make_row("Format Halaman", data["jumlah_halaman"], data["harga_halaman"], data["subtotal_halaman"]))
    if data["jumlah_gambar"] > 0:
        tdata.append(make_row("Captioning Gambar & Daftar Gambar", data["jumlah_gambar"], 1000, data["subtotal_gambar"]))
    if data["jumlah_tabel"] > 0:
        tdata.append(make_row("Captioning Tabel & Daftar Tabel", data["jumlah_tabel"], 1000, data["subtotal_tabel"]))
    if data["jumlah_lampiran"] > 0:
        tdata.append(make_row("Captioning Lampiran & Daftar Lampiran", data["jumlah_lampiran"], 1000, data["subtotal_lampiran"]))
    if data["jumlah_section"] > 0:
        tdata.append(make_row("Numbering Section", data["jumlah_section"], 1000, data["subtotal_numbering"]))
    if data["subtotal_daftar_isi"] > 0:
        note = f"Bab: {data.get('jml_bab',0)}, Sub Bab: {data.get('jml_sub_bab',0)}, Sub Sub Bab: {data.get('jml_sub_sub_bab',0)}"
        tdata.append(make_row("Pembuatan Daftar Isi", data.get("total_entri_doi", 0), 500, data["subtotal_daftar_isi"], note))

    if len(tdata) == 1:
        tdata.append([Paragraph("— Tidak ada layanan —", ps("empty", font=P, size=9, color=GRAY)), "", "", ""])

    items_tbl = Table(tdata, colWidths=[8.5*cm, 2*cm, 3.25*cm, 3.25*cm], repeatRows=1)
    items_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  NAVY),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, colors.HexColor("#F7F4EF")]),
        ("GRID",          (0, 0), (-1, -1), 0.4, LGRAY),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(items_tbl)

    # ── Total ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.15*cm))
    total_tbl = Table([[
        Paragraph("", ps("tg")),
        Paragraph("TOTAL BIAYA", ps("tl", font=PB, size=9, color=WHITE, align=TA_RIGHT)),
        Paragraph(fmt(data["grand_total"]), ps("tv", font=PB, size=12, color=GOLD, align=TA_RIGHT)),
    ]], colWidths=[8.5*cm, 3.5*cm, 5*cm])
    total_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(total_tbl)

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LGRAY, spaceAfter=0.3*cm))
    story.append(Paragraph(
        "Terima kasih telah mempercayakan formatting skripsi Anda kepada SkripsiRapi. "
        "Invoice ini diterbitkan secara otomatis. Hubungi kami di instagram.com/skripsirapi.",
        ps("fn", font=P, size=7.5, color=GRAY, align=TA_CENTER)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ─── Generate Button ───────────────────────────────────────────────────────────
if st.button("⬇️  Generate & Download Invoice PDF"):
    if not nama_klien:
        st.warning("Mohon isi nama klien terlebih dahulu.")
    elif grand_total == 0:
        st.warning("Belum ada layanan yang dipilih / diisi.")
    else:
        doi_data = {}
        if ada_daftar_isi == "Ya":
            doi_data = {
                "jml_bab": jml_bab, "jml_sub_bab": jml_sub_bab,
                "jml_sub_sub_bab": jml_sub_sub_bab,
                "total_entri_doi": jml_bab + jml_sub_bab + jml_sub_sub_bab,
            }
        pdf_data = {
            "nama_klien": nama_klien, "email_klien": email_klien,
            "no_invoice": no_invoice, "tanggal": tanggal.strftime("%d %B %Y"),
            "catatan": catatan,
            "jumlah_halaman": jumlah_halaman, "harga_halaman": harga_halaman, "subtotal_halaman": subtotal_halaman,
            "jumlah_gambar": jumlah_gambar, "subtotal_gambar": subtotal_gambar,
            "jumlah_tabel": jumlah_tabel, "subtotal_tabel": subtotal_tabel,
            "jumlah_lampiran": jumlah_lampiran, "subtotal_lampiran": subtotal_lampiran,
            "jumlah_section": jumlah_section, "subtotal_numbering": subtotal_numbering,
            "subtotal_daftar_isi": subtotal_daftar_isi, "grand_total": grand_total,
            **doi_data,
        }
        with st.spinner("Membuat PDF..."):
            pdf_buffer = generate_pdf(pdf_data)

        fname = f"Invoice_SkripsiRapi_{no_invoice}.pdf"
        st.success("✅ Invoice berhasil dibuat!")
        st.download_button(label="📥 Download Invoice PDF", data=pdf_buffer,
                           file_name=fname, mime="application/pdf")

st.markdown("""
<div class="footer">
    Dibuat oleh <a href="https://instagram.com/skripsirapi" target="_blank">@skripsirapi</a> · 
    Format Skripsi Profesional · Indonesia
</div>
""", unsafe_allow_html=True)
