import pymupdf
from PIL import Image as PILImage
from io import BytesIO

def generate_png(pdf_bytes: bytes, dpi: int = 200) -> bytes:
    doc = pymupdf.open(stream=pdf_bytes, filetype='pdf')
    
    if len(doc) == 1:
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=dpi)
        return pix.tobytes("png")
        
    images = []
    for i in range(len(doc)):
        p = doc.load_page(i)
        px = p.get_pixmap(dpi=dpi)
        img = PILImage.frombytes("RGB", [px.width, px.height], px.samples)
        images.append(img)
        
    widths, heights = zip(*(i.size for i in images))
    total_height = sum(heights)
    max_width = max(widths)
    
    combined_img = PILImage.new('RGB', (max_width, total_height))
    y_offset = 0
    for img in images:
        combined_img.paste(img, (0, y_offset))
        y_offset += img.size[1]
        
    img_byte_arr = BytesIO()
    combined_img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def generate_jpeg(pdf_bytes: bytes, dpi: int = 200, quality: int = 90) -> bytes:
    png_bytes = generate_png(pdf_bytes, dpi=dpi)
    
    img = PILImage.open(BytesIO(png_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
        
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=quality, optimize=True)
    return img_byte_arr.getvalue()
