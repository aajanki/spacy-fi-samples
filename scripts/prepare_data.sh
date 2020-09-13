#!/bin/sh

echo "Downloading asiantuntijalausunnot"
python scripts/get_asiantuntijalausunnot.py
python scripts/pdf2txt_asiantuntijalausunnot.py
python scripts/cleanup_asiantuntijalausunnut.py

echo "Downloading UD_Finnish-TDT"
git clone --branch r2.4 --single-branch --depth 1 https://github.com/UniversalDependencies/UD_Finnish-TDT data/blogit/UD_Finnish-TDT
python scripts/cleanup_UD_Finnish-TDT.py
