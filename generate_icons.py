from PIL import Image
import os

# Use absolute path to avoid OneDrive issues
base = r"C:\Users\mrran\OneDrive\Desktop\actor_scanner"
logo_path = os.path.join(base, "static", "logo.png")
icons_dir = os.path.join(base, "static", "icons")

os.makedirs(icons_dir, exist_ok=True)

print(f"Loading logo from: {logo_path}")
logo = Image.open(logo_path).convert("RGBA")
print(f"Logo size: {logo.size}")

sizes = [72, 96, 128, 144, 152, 192, 384, 512]

for size in sizes:
    img = logo.resize((size, size), Image.LANCZOS)
    save_path = os.path.join(icons_dir, f"icon-{size}x{size}.png")
    img.save(save_path)
    print(f"Saved: {save_path}")

print("All icons generated successfully.")