import os
import subprocess
import tempfile
import re
from pathlib import Path
from tqdm import tqdm


def main():
    docdir = Path('data/asiantuntijalausunnot/pdf/')
    outdir = Path('data/asiantuntijalausunnot/text_orig/')

    outdir.mkdir(parents=True, exist_ok=True)

    print('Extracting text from the PDFs')
    for input_path in tqdm(list(docdir.glob('*.pdf'))):
        doc_id = input_path.stem
        output_path = outdir / f'{doc_id}.txt'

        try:
            ocr_pdf(input_path, output_path)
        except subprocess.CalledProcessError as ex:
            print(ex)


def ocr_pdf(pdffile, outputfile):
    page_type = detect_page_type(pdffile)

    if page_type == 'unknwon':
        # Most likely not a text document. Maybe slides?
        return

    f = tempfile.NamedTemporaryFile(suffix='.tiff', delete=False)
    try:
        f.close()

        # The bottom 7% is commonly a footer. Very rarely it cuts body text.
        subprocess.run(
            ['montage', '-crop', '100%x93%+0+0', '-density', '150', str(pdffile),
             '-mode', 'Concatenate', '-tile', '1x1', '-depth', '8',
             '-colorspace', 'RGB', f.name],
            check=True)

        subprocess.run(
            ['tesseract', f.name, str(outputfile.parent / outputfile.stem),
             '-l', 'fin', 'quiet'],
            check=True)
    finally:
        os.remove(f.name)


def detect_page_type(pdffile):
    width, height = pdf_page_size(pdffile)

    if not width or not height:
        return 'unknown'
    elif 592 < width < 598 and 839 < height < 845: # A4: 595x842
        return 'A4'
    elif 839 < width < 845 and 592 < height < 598:
        return 'A4-rotated'
    elif 609 < width < 615 and 789 < height < 795: # Letter: 612x792
        return 'letter'
    elif 789 < width < 795 and 609 < height < 615 :
        return 'letter-rotated'
    else:
        return 'unknown'


def pdf_page_size(pdffile):
    page_size_pattern = re.compile(r'Page size: +(\d+(?:\.\d+)?) *x *(\d+(?:\.\d+)?) pts')
    p = subprocess.run(['pdfinfo', str(pdffile)],
                       capture_output=True, text=True, check=True)
    lines = p.stdout.split('\n')
    for line in lines:
        m = page_size_pattern.match(line)
        if m:
            width = float(m.group(1))
            height = float(m.group(2))
            return width, height

    return None, None


if __name__ == '__main__':
    main()
