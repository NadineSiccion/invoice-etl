import fitz  # PyMuPDF
from pathlib import Path
import os

def redact_data_and_save(input_path:Path) -> None:
    doc = fitz.open(input_path)
    page = doc[0]

    # Draw rectangle
    rect_top = fitz.Rect(20, 15, 570, 225)
    rect_mid = fitz.Rect(20, 600, 345, 700)
    rect_bottom = fitz.Rect(20, 750, 570, 820)
    # page.draw_rect(rect, color=(0, 0, 0), fill=(0, 0, 0), width=2)

    page.add_redact_annot(rect_top, fill=(0, 0, 0))
    page.add_redact_annot(rect_mid, fill=(0, 0, 0))
    page.add_redact_annot(rect_bottom, fill=(0, 0, 0))
    page.apply_redactions()

    doc.save(BASE_DIR / "anon_invoices" / input_path.name)
    print(f"✅ Saved {input_path.name} to anon_invoices directory.")


# Main logic
BASE_DIR = Path(__file__).resolve().parent.parent
# ORIG_PDFS_PATH = BASE_DIR / "sample-invoices"

# orig_pdfs = os.listdir(".\\sample-invoices")
# for pdf in orig_pdfs:
#     target_path = ORIG_PDFS_PATH / pdf
#     redact_data_and_save(target_path)

# print("🙌 Reached the end of the script.")