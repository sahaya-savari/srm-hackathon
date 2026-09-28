"""
Measures how far plain Tesseract OCR gets on these scans, to justify the
visual-verification approach and to produce per-file OCR confidence.

For each page: mean word confidence, and recall of the verified subject codes
(exact and after common-substitution repair) in the raw OCR text.
"""
import re, sys, subprocess
from pathlib import Path
import pandas as pd
import pytesseract
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data_raw"))
import transcription as T  # noqa

RAW = ROOT.parent / "data" / "raw"
IMG = ROOT / "data_raw" / "pages"
IMG.mkdir(exist_ok=True)

def page_image(pdf, page):
    stem = IMG / f"{Path(pdf).stem.replace(' ', '_')}-p{page}"
    png = Path(str(stem) + ".png")
    if not png.exists():
        subprocess.run(["pdftoppm", "-r", "200", "-png", "-f", str(page), "-l", str(page),
                        "-singlefile", str(RAW / pdf), str(stem)], check=True)
    return png

def repair(s):  # typical OCR substitutions seen on these scans
    return (s.replace("]", "J").replace(")", "J").replace("|", "I")
             .replace("O", "0") if False else s.replace("]", "J").replace(")", "J"))

rows = []
for sid, sec in T.SECTIONS.items():
    png = page_image(sec["source_file"], sec["page"])
    txt = pytesseract.image_to_string(Image.open(png), config="--psm 6")
    data = pytesseract.image_to_data(Image.open(png), output_type=pytesseract.Output.DATAFRAME)
    conf = data[(data.conf >= 0) & data.text.notna()].conf
    codes = sorted({v[0] for v in sec["subjects"].values()})
    norm = re.sub(r"\s+", "", txt).upper()
    exact = sum(c in norm for c in codes)
    fixed = sum(c in repair(norm).replace("0", "O").replace("O", "0") or c in repair(norm) for c in codes)
    # grid: count single slot letters OCR found in weekday rows vs verified cell count
    n_cells = len(sec["cells"])
    rows.append(dict(section_id=sid, file=sec["source_file"], page=sec["page"],
                     text_layer_bytes=0, ocr_mean_word_conf=round(conf.mean(), 1),
                     subject_codes=len(codes), codes_found_exact=exact, codes_found_after_repair=fixed,
                     code_recall_exact=round(exact / len(codes), 2),
                     verified_grid_cells=n_cells))
df = pd.DataFrame(rows)
df.to_csv(ROOT / "data_clean" / "ocr_crosscheck.csv", index=False)
print(df.to_string())
