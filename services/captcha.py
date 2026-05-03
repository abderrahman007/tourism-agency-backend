import random
import io
import uuid
import time
from PIL import Image, ImageDraw, ImageFont, ImageFilter

CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

# In-memory store: token → (code, expiry_timestamp)
captcha_store: dict[str, tuple[str, float]] = {}

CAPTCHA_TTL = 300  # 5 minutes


def generate_code(length=5) -> str:
    return "".join(random.choices(CHARS, k=length))


def draw_captcha(code: str) -> bytes:
    W, H = 200, 70
    img = Image.new("RGB", (W, H), color=(240, 238, 232))
    draw = ImageDraw.Draw(img)

    for _ in range(6):
        x1, y1 = random.randint(0, W), random.randint(0, H)
        x2, y2 = random.randint(0, W), random.randint(0, H)
        draw.line([(x1, y1), (x2, y2)], fill=(180, 178, 169), width=1)

    for _ in range(60):
        draw.point((random.randint(0, W), random.randint(0, H)), fill=(160, 158, 150))

    colors = ["#0F6E56", "#3C3489", "#854F0B", "#993556", "#0C447C"]
    char_w = W // (len(code) + 1)

    for i, ch in enumerate(code):
        x = char_w * (i + 1) + random.randint(-4, 4)
        y = H // 2 + random.randint(-8, 8)
        size = random.randint(24, 32)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        except:
            font = ImageFont.load_default()
        draw.text((x, y), ch, font=font, fill=colors[i % len(colors)], anchor="mm")

    img = img.filter(ImageFilter.GaussianBlur(radius=0.6))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def create_captcha() -> tuple[str, bytes]:
    token = str(uuid.uuid4())
    code = generate_code()
    captcha_store[token] = (code, time.time() + CAPTCHA_TTL)
    return token, draw_captcha(code)


def verify_captcha(token: str, answer: str) -> bool:
    entry = captcha_store.pop(token, None)
    if not entry:
        return False
    code, expiry = entry
    if time.time() > expiry:
        return False
    return answer.strip().upper() == code
