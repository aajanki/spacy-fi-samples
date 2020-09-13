import spacy
from collections import Counter
from pathlib import Path


def main():
    nlp = spacy.load('spacy_fi_experimental_web_md')

    atl_path = Path('data/asiantuntijalausunnot/text')
    print()
    print('Asiantuntijalausunnot:')
    print()
    print_stats(atl_path, nlp)

    blogit_path = Path('data/blogit/text')
    print()
    print('Blogit:')
    print()
    print_stats(blogit_path, nlp)


def print_stats(path, nlp):
    pos_counter = Counter()
    adj_counter = Counter()
    noun_counter = Counter()
    verb_counter = Counter()
    texts_iter = (x.open().read() for x in path.glob('*.txt'))
    for doc in nlp.pipe(texts_iter, disable=['parser', 'ner']):
        pos_counter.update([t.pos_ for t in doc if t.pos_ != 'SPACE'])

        adj_counter.update([
            t.lemma_ for t in doc if t.pos_ == 'ADJ'
        ])

        noun_counter.update([
            t.lemma_ for t in doc if t.pos_ == 'NOUN'
        ])

        verb_counter.update([
            t.lemma_ for t in doc
            if (t.pos_ in ('VERB', 'AUX') and t.lemma_ != 'ei')
        ])

    print('POS frequencies:')
    total_tokens = sum(pos_counter.values())
    for (pos, freq) in pos_counter.most_common():
        print(f'{freq/total_tokens*100:2.0f}% {pos}')

    print()
    print('The most common adjectives:')
    for (term, freq) in adj_counter.most_common(10):
        print(f'{freq:>6} {term}')

    print()
    print('The most common nouns:')
    for (term, freq) in noun_counter.most_common(10):
        print(f'{freq:>6} {term}')

    print()
    print('The most common verbs:')
    for (term, freq) in verb_counter.most_common(10):
        print(f'{freq:>6} {term}')


if __name__ == '__main__':
    main()
