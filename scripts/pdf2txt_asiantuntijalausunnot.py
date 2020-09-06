import os
import subprocess
import tempfile
from pathlib import Path
from tqdm import tqdm


def main():
    docdir = Path('data/asiantuntijalausunnot/pdf/')
    outdir = Path('data/asiantuntijalausunnot/text/')

    outdir.mkdir(parents=True, exist_ok=True)

    print('Extracting text from the PDFs')
    for input_path in tqdm(list(docdir.glob('*.pdf'))):
        doc_id = input_path.stem
        output_path = outdir / f'{doc_id}.txt'

        try:
            extract_text(input_path, output_path)

            if output_path.stat().st_size < 100:
                ocr_pdf(input_path, output_path)
        except subprocess.CalledProcessError as ex:
            print(ex)


def extract_text(pdffile, outputfile):
    subprocess.run(['pdftotext', str(pdffile), str(outputfile)], check=True)


def ocr_pdf(pdffile, outputfile):
    f = tempfile.NamedTemporaryFile(suffix='.tiff', delete=False)
    try:
        f.close()

        subprocess.run(
            ['montage', '-density', '150', str(pdffile), '-mode', 'Concatenate',
             '-tile', '1x8', '-depth', '8', f.name],
            check=True)

        subprocess.run(
            ['tesseract', f.name, str(outputfile.parent / outputfile.stem),
             '-l', 'fin', 'quiet'],
            check=True)
    finally:
        os.remove(f.name)


if __name__ == '__main__':
    main()
