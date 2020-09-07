import re
from pathlib import Path
from tqdm import tqdm


def main():
    indir = Path('data/asiantuntijalausunnot/text_orig')
    outdir = Path('data/asiantuntijalausunnot/text')

    outdir.mkdir(parents=True, exist_ok=True)

    print('Cleaning up text')
    for p in tqdm(list(indir.glob('*.txt'))):
        with p.open() as inf:
            text = dehyphenate(inf.read())

        with open(outdir / p.name, 'w') as outf:
            outf.write(text)


def dehyphenate(text):
    return re.sub(r'([a-zåäöA-ZÅÄÖ0-9])-\n\n?([a-zåäöA-ZÅÄÖ])', merge_hyphenated, text)


def merge_hyphenated(matchobj):
    a = matchobj.group(1)
    b = matchobj.group(2)

    if a.isdigit():
        atype = 'digit'
    elif a.islower():
        atype = 'lower'
    else:
        atype = 'upper'

    if b.isdigit():
        btype = 'digit'
    elif b.islower():
        btype = 'lower'
    else:
        btype = 'upper'
    
    if a.lower() == b.lower() and (is_vowel(a) or atype != btype):
        return f'{a}-{b}'
    else:
        return f'{a}{b}'


def is_vowel(c):
    return c.lower() in 'aeiouyåäö'


if __name__ == '__main__':
    main()
