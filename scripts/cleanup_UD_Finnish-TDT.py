from pathlib import Path


def main():
    inpath = Path('data/blogit/UD_Finnish-TDT/fi_tdt-ud-train.conllu')
    outpath = Path('data/blogit/text')
    lines = []
    start = False
    for line in inpath.open().read().splitlines():
        if line.startswith('# sent_id'):
            if line.startswith('# sent_id = b') or line.startswith('# sent_id = f'):
                start = True
                continue
        elif start and line.startswith('# text = '):
            text = line[len('# text = '):]
            if text and text[-1] not in '.!?':
                text = text + '.'
            lines.append(text)
        else:
            assert not start

        start = False

    outpath.mkdir(parents=True, exist_ok=True)
    with open(outpath / 'sentences.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':
    main()
