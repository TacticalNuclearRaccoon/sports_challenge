import hashlib
from io import BytesIO

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

PALETTE = [
    "#E07A5F", "#3D405B", "#81B29A", "#F2CC8F", "#577590",
    "#F94144", "#43AA8B", "#277DA1", "#9C6644", "#6A4C93",
]


def _seed_to_color(seed: str) -> str:
    digest = hashlib.sha256(seed.encode()).hexdigest()
    return PALETTE[int(digest, 16) % len(PALETTE)]


def _initials(display_name: str) -> str:
    parts = [p for p in display_name.strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


@st.cache_data(show_spinner=False)
def generate_avatar(seed: str, display_name: str, size: int = 96) -> bytes:
    """Deterministic initials/color avatar as PNG bytes. `seed` should be
    the stable user_id, not display_name (which a user could change)."""
    color = _seed_to_color(seed)
    img = Image.new("RGB", (size, size), color)
    draw = ImageDraw.Draw(img)
    text = _initials(display_name)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", size // 2)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((size - text_w) / 2 - bbox[0], (size - text_h) / 2 - bbox[1]),
        text,
        fill="white",
        font=font,
    )

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
