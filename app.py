import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
import io
import os
from datetime import datetime
import base64

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SkripsiRapi Invoice Generator",
    page_icon="📄",
    layout="centered",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .main {
        background-color: #FAF8F5;
    }

    /* Header */
    .header-block {
        background: linear-gradient(135deg, #1A2B4A 0%, #243960 100%);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        color: #FAF8F5;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }

    .header-title {
        font-size: 1.6rem;
        font-weight: 600;
        letter-spacing: -0.02em;
        color: #D4AF6A;
        margin: 0;
    }

    .header-sub {
        font-size: 0.85rem;
        color: #c8d0df;
        margin: 0.25rem 0 0 0;
    }

    /* Section cards */
    .section-card {
        background: white;
        border: 1px solid #E8E2D9;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
    }

    .section-label {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #1A2B4A;
        margin-bottom: 0.75rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #D4AF6A;
        display: inline-block;
    }

    /* Summary box */
    .summary-box {
        background: #1A2B4A;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        color: #FAF8F5;
        margin-top: 1.5rem;
    }

    .summary-row {
        display: flex;
        justify-content: space-between;
        padding: 0.3rem 0;
        font-size: 0.9rem;
        color: #c8d0df;
    }

    .summary-total {
        display: flex;
        justify-content: space-between;
        padding: 0.75rem 0 0 0;
        margin-top: 0.5rem;
        border-top: 1px solid #D4AF6A;
        font-size: 1.15rem;
        font-weight: 600;
        color: #D4AF6A;
    }

    /* Generate button */
    .stButton > button {
        background: linear-gradient(135deg, #D4AF6A, #c9a55a) !important;
        color: #1A2B4A !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 2rem !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: opacity 0.2s !important;
    }

    .stButton > button:hover {
        opacity: 0.9 !important;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #aaa;
        font-size: 0.75rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
    }

    .footer a {
        color: #D4AF6A;
        text-decoration: none;
    }

    /* Divider */
    hr {
        border-color: #E8E2D9;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ────────────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 4])
with col_logo:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=80)
with col_title:
    st.markdown("""
    <div style="padding-top: 0.5rem;">
        <div style="font-size:1.5rem; font-weight:700; color:#1A2B4A; letter-spacing:-0.02em;">SkripsiRapi</div>
        <div style="font-size:0.82rem; color:#888; margin-top:2px;">Invoice PDF Generator · Format Skripsi Profesional</div>
    </div>
    """, unsafe_allow_html=True)

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

# 1. Halaman
with st.expander("📄 Jumlah Halaman", expanded=True):
    jumlah_halaman = st.number_input("Jumlah halaman total", min_value=0, value=0, step=1)
    harga_halaman = st.radio(
        "Harga per halaman",
        options=[1000, 2000],
        format_func=lambda x: f"Rp {x:,}/halaman {'(Standard)' if x==1000 else '(Premium)'}",
        horizontal=True
    )
    subtotal_halaman = jumlah_halaman * harga_halaman

# 2. Gambar
with st.expander("🖼️ Gambar (termasuk Daftar Gambar)"):
    jumlah_gambar = st.number_input("Jumlah gambar", min_value=0, value=0, step=1)
    subtotal_gambar = jumlah_gambar * 1000

# 3. Tabel
with st.expander("📊 Tabel (termasuk Daftar Tabel)"):
    jumlah_tabel = st.number_input("Jumlah tabel", min_value=0, value=0, step=1)
    subtotal_tabel = jumlah_tabel * 1000

# 4. Lampiran
with st.expander("📎 Lampiran (termasuk Daftar Lampiran)"):
    jumlah_lampiran = st.number_input("Jumlah lampiran", min_value=0, value=0, step=1)
    subtotal_lampiran = jumlah_lampiran * 1000

# 5. Numbering
with st.expander("🔢 Numbering per Section"):
    jumlah_section = st.number_input("Jumlah section", min_value=0, value=0, step=1)
    subtotal_numbering = jumlah_section * 1000

# 6. Daftar Isi
with st.expander("📑 Daftar Isi"):
    ada_daftar_isi = st.radio("Perlu pembuatan Daftar Isi?", ["Tidak", "Ya"], horizontal=True)
    subtotal_daftar_isi = 0
    if ada_daftar_isi == "Ya":
        col_b, col_sb, col_ssb = st.columns(3)
        with col_b:
            jml_bab = st.number_input("Jumlah Bab", min_value=0, value=0, step=1)
        with col_sb:
            jml_sub_bab = st.number_input("Jumlah Sub Bab", min_value=0, value=0, step=1)
        with col_ssb:
            jml_sub_sub_bab = st.number_input("Jumlah Sub Sub Bab", min_value=0, value=0, step=1)
        total_entri_doi = jml_bab + jml_sub_bab + jml_sub_sub_bab
        subtotal_daftar_isi = total_entri_doi * 500
        st.caption(f"Total entri: {total_entri_doi} × Rp 500 = **Rp {subtotal_daftar_isi:,}**")

# ─── Summary ───────────────────────────────────────────────────────────────────
grand_total = (
    subtotal_halaman + subtotal_gambar + subtotal_tabel +
    subtotal_lampiran + subtotal_numbering + subtotal_daftar_isi
)

st.markdown("---")
st.markdown('<div class="section-label">💰 Ringkasan Biaya</div>', unsafe_allow_html=True)

items_summary = [
    ("Halaman", jumlah_halaman, harga_halaman, subtotal_halaman),
    ("Gambar & Daftar Gambar", jumlah_gambar, 1000, subtotal_gambar),
    ("Tabel & Daftar Tabel", jumlah_tabel, 1000, subtotal_tabel),
    ("Lampiran & Daftar Lampiran", jumlah_lampiran, 1000, subtotal_lampiran),
    ("Numbering Section", jumlah_section, 1000, subtotal_numbering),
    ("Daftar Isi", None, None, subtotal_daftar_isi),
]

for label, qty, price, sub in items_summary:
    if sub > 0 or (qty is not None and qty > 0):
        if qty is not None:
            detail = f"{qty} × Rp {price:,}"
        else:
            detail = f"Rp {sub:,}" if sub > 0 else "—"
        col_a, col_b = st.columns([3, 1])
        col_a.markdown(f"<span style='color:#555'>{label}</span> <small style='color:#aaa'>({detail})</small>", unsafe_allow_html=True)
        col_b.markdown(f"<div style='text-align:right; font-weight:500'>Rp {sub:,}</div>", unsafe_allow_html=True)

st.markdown(f"""
<div style="background:#1A2B4A; border-radius:10px; padding:1rem 1.5rem; margin-top:1rem; display:flex; justify-content:space-between; align-items:center;">
    <span style="color:#c8d0df; font-size:0.9rem;">TOTAL BIAYA</span>
    <span style="color:#D4AF6A; font-size:1.4rem; font-weight:700;">Rp {grand_total:,}</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Generate PDF ──────────────────────────────────────────────────────────────
def generate_pdf(data):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    NAVY = colors.HexColor("#1A2B4A")
    GOLD = colors.HexColor("#D4AF6A")
    CREAM = colors.HexColor("#FAF8F5")
    GRAY = colors.HexColor("#888888")
    LIGHT_GRAY = colors.HexColor("#E8E2D9")
    WHITE = colors.white

    styles = getSampleStyleSheet()
    story = []

    # ── Header ──
    # Logo + company info side by side via table
    logo_cell = ""
    logo_path = "logo.jpg"

    if os.path.exists(logo_path):
        logo_img = Image(logo_path, width=2.2*cm, height=2.2*cm)
        logo_cell = logo_img

    company_text = [
        Paragraph("<b><font size=16 color='#1A2B4A'>SkripsiRapi</font></b>", styles["Normal"]),
        Paragraph("<font size=9 color='#888888'>Format Skripsi Profesional</font>", styles["Normal"]),
        Spacer(1, 4),
        Paragraph("<font size=8 color='#888888'>instagram.com/skripsirapi</font>", styles["Normal"]),
    ]

    invoice_text = [
        Paragraph("<b><font size=18 color='#1A2B4A'>INVOICE</font></b>",
                  ParagraphStyle("r", alignment=TA_RIGHT, fontSize=18, fontName="Helvetica-Bold")),
        Paragraph(f"<font size=9 color='#888888'>{data['no_invoice']}</font>",
                  ParagraphStyle("r", alignment=TA_RIGHT, fontSize=9)),
        Paragraph(f"<font size=9 color='#888888'>Tanggal: {data['tanggal']}</font>",
                  ParagraphStyle("r", alignment=TA_RIGHT, fontSize=9)),
    ]

    header_table = Table(
        [[logo_cell, company_text, invoice_text]],
        colWidths=[2.5*cm, 9*cm, 5.5*cm]
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=0.4*cm))

    # ── Client info ──
    client_data = [
        [Paragraph("<b><font size=9 color='#1A2B4A'>DITAGIHKAN KEPADA</font></b>", styles["Normal"]),
         Paragraph("<b><font size=9 color='#1A2B4A'>KETERANGAN</font></b>", styles["Normal"])],
        [Paragraph(f"<font size=10>{data['nama_klien'] or '—'}</font>", styles["Normal"]),
         Paragraph(f"<font size=9 color='#555555'>{data['catatan'] or '—'}</font>", styles["Normal"])],
        [Paragraph(f"<font size=9 color='#888888'>{data['email_klien'] or ''}</font>", styles["Normal"]),
         ""],
    ]

    client_table = Table(client_data, colWidths=[8.5*cm, 8.5*cm])
    client_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Items table ──
    header_row = [
        Paragraph("<b><font size=9 color='white'>LAYANAN</font></b>", ParagraphStyle("th", fontName="Helvetica-Bold")),
        Paragraph("<b><font size=9 color='white'>QTY</font></b>", ParagraphStyle("th", alignment=TA_CENTER, fontName="Helvetica-Bold")),
        Paragraph("<b><font size=9 color='white'>HARGA SATUAN</font></b>", ParagraphStyle("th", alignment=TA_RIGHT, fontName="Helvetica-Bold")),
        Paragraph("<b><font size=9 color='white'>SUBTOTAL</font></b>", ParagraphStyle("th", alignment=TA_RIGHT, fontName="Helvetica-Bold")),
    ]

    table_data = [header_row]

    def fmt(n): return f"Rp {n:,}"

    def row(label, qty, price, sub, note=""):
        label_text = label + (f"\n<font size=8 color='#888888'>{note}</font>" if note else "")
        qty_str = str(qty) if qty is not None else "—"
        price_str = fmt(price) if price is not None else "—"
        return [
            Paragraph(f"<font size=9>{label_text}</font>", styles["Normal"]),
            Paragraph(f"<font size=9>{qty_str}</font>", ParagraphStyle("c", alignment=TA_CENTER, fontSize=9)),
            Paragraph(f"<font size=9>{price_str}</font>", ParagraphStyle("r", alignment=TA_RIGHT, fontSize=9)),
            Paragraph(f"<font size=9>{fmt(sub)}</font>", ParagraphStyle("r", alignment=TA_RIGHT, fontSize=9)),
        ]

    rows_to_add = []

    if data["jumlah_halaman"] > 0:
        rows_to_add.append(row(
            "Format Halaman",
            data["jumlah_halaman"],
            data["harga_halaman"],
            data["subtotal_halaman"]
        ))

    if data["jumlah_gambar"] > 0:
        rows_to_add.append(row(
            "Captioning Gambar & Daftar Gambar",
            data["jumlah_gambar"],
            1000,
            data["subtotal_gambar"]
        ))

    if data["jumlah_tabel"] > 0:
        rows_to_add.append(row(
            "Captioning Tabel & Daftar Tabel",
            data["jumlah_tabel"],
            1000,
            data["subtotal_tabel"]
        ))

    if data["jumlah_lampiran"] > 0:
        rows_to_add.append(row(
            "Captioning Lampiran & Daftar Lampiran",
            data["jumlah_lampiran"],
            1000,
            data["subtotal_lampiran"]
        ))

    if data["jumlah_section"] > 0:
        rows_to_add.append(row(
            "Numbering Section",
            data["jumlah_section"],
            1000,
            data["subtotal_numbering"]
        ))

    if data["subtotal_daftar_isi"] > 0:
        rows_to_add.append(row(
            "Pembuatan Daftar Isi",
            data.get("total_entri_doi", 0),
            500,
            data["subtotal_daftar_isi"],
            f"Bab: {data.get('jml_bab',0)}, Sub Bab: {data.get('jml_sub_bab',0)}, Sub Sub Bab: {data.get('jml_sub_sub_bab',0)}"
        ))

    if not rows_to_add:
        rows_to_add.append([
            Paragraph("<font size=9 color='#888888'>— Tidak ada layanan yang dipilih —</font>", styles["Normal"]),
            "", "", ""
        ])

    table_data.extend(rows_to_add)

    col_widths = [9*cm, 2*cm, 3*cm, 3*cm]
    items_table = Table(table_data, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#F7F4EF")]),
        ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
        ("LINEABOVE", (0, 0), (-1, 0), 0, WHITE),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]

    items_table.setStyle(TableStyle(style_cmds))
    story.append(items_table)

    # ── Total ──
    story.append(Spacer(1, 0.2*cm))

    total_table = Table(
        [
            ["", Paragraph("<b><font size=9>TOTAL BIAYA</font></b>",
                           ParagraphStyle("r", alignment=TA_RIGHT, fontSize=9)),
             Paragraph(f"<b><font size=13 color='#D4AF6A'>{fmt(data['grand_total'])}</font></b>",
                       ParagraphStyle("r", alignment=TA_RIGHT, fontSize=13))]
        ],
        colWidths=[9*cm, 4*cm, 4*cm]
    )
    total_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(total_table)

    # ── Footer note ──
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GRAY, spaceAfter=0.3*cm))
    story.append(Paragraph(
        "<font size=8 color='#888888'>Terima kasih telah mempercayakan formatting skripsi Anda kepada SkripsiRapi. "
        "Invoice ini diterbitkan secara otomatis. Hubungi kami di <b>instagram.com/skripsirapi</b> untuk pertanyaan lebih lanjut.</font>",
        ParagraphStyle("footer", alignment=TA_CENTER, fontSize=8)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


if st.button("⬇️  Generate & Download Invoice PDF"):
    if not nama_klien:
        st.warning("Mohon isi nama klien terlebih dahulu.")
    elif grand_total == 0:
        st.warning("Belum ada layanan yang dipilih / diisi.")
    else:
        doi_data = {}
        if ada_daftar_isi == "Ya":
            doi_data = {
                "jml_bab": jml_bab,
                "jml_sub_bab": jml_sub_bab,
                "jml_sub_sub_bab": jml_sub_sub_bab,
                "total_entri_doi": jml_bab + jml_sub_bab + jml_sub_sub_bab,
            }

        pdf_data = {
            "nama_klien": nama_klien,
            "email_klien": email_klien,
            "no_invoice": no_invoice,
            "tanggal": tanggal.strftime("%d %B %Y"),
            "catatan": catatan,
            "jumlah_halaman": jumlah_halaman,
            "harga_halaman": harga_halaman,
            "subtotal_halaman": subtotal_halaman,
            "jumlah_gambar": jumlah_gambar,
            "subtotal_gambar": subtotal_gambar,
            "jumlah_tabel": jumlah_tabel,
            "subtotal_tabel": subtotal_tabel,
            "jumlah_lampiran": jumlah_lampiran,
            "subtotal_lampiran": subtotal_lampiran,
            "jumlah_section": jumlah_section,
            "subtotal_numbering": subtotal_numbering,
            "subtotal_daftar_isi": subtotal_daftar_isi,
            "grand_total": grand_total,
            **doi_data,
        }

        with st.spinner("Membuat PDF..."):
            pdf_buffer = generate_pdf(pdf_data)

        fname = f"Invoice_SkripsiRapi_{no_invoice}.pdf"
        st.success("✅ Invoice berhasil dibuat!")
        st.download_button(
            label="📥 Download Invoice PDF",
            data=pdf_buffer,
            file_name=fname,
            mime="application/pdf",
        )

# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Dibuat oleh <a href="https://instagram.com/skripsirapi" target="_blank">@skripsirapi</a> · 
    Format Skripsi Profesional · Indonesia
</div>
""", unsafe_allow_html=True)
