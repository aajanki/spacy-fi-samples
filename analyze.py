import pandas as pd
import seaborn as sns
import spacy
from collections import Counter
from pathlib import Path


def main():
    nlp = spacy.load('spacy_fi_experimental_web_md')

    atl_counts = counts(Path('data/asiantuntijalausunnot/text'), nlp)
    print()
    print('Asiantuntijalausunnot:')
    print()
    print_counts(atl_counts)

    blogs_counts = counts(Path('data/blogit/text'), nlp)
    print()
    print('Blogit:')
    print()
    print_counts(blogs_counts)

    plot_pos_frequencies(atl_counts['pos'], blogs_counts['pos'])
    print('Plots saved in the images directory')


def counts(path, nlp):
    pos_counter = Counter()
    adj_counter = Counter()
    noun_counter = Counter()
    verb_counter = Counter()
    texts_iter = (x.open().read() for x in path.glob('*.txt'))
    for doc in nlp.pipe(texts_iter, disable=['parser', 'ner']):
        tokens = [t for t in doc if t.pos_ not in ('SPACE', 'PUNCT')]

        pos_counter.update([t.pos_ for t in tokens])

        adj_counter.update([
            t.lemma_ for t in tokens if t.pos_ == 'ADJ'
        ])

        noun_counter.update([
            t.lemma_ for t in tokens if t.pos_ == 'NOUN'
        ])

        verb_counter.update([
            t.lemma_ for t in tokens
            if (t.pos_ in ('VERB', 'AUX') and t.lemma_ != 'ei')
        ])

    return {
        'adj': adj_counter,
        'noun': noun_counter,
        'verb': verb_counter,
        'pos': pos_counter,
    }


def print_counts(counts):
    print('POS frequencies:')
    total_tokens = sum(counts['pos'].values())
    for (pos, freq) in counts['pos'].most_common():
        print(f'{freq/total_tokens*100:2.0f}% {pos}')

    print()
    print('The most common adjectives:')
    for (term, freq) in counts['adj'].most_common(10):
        print(f'{freq:>6} {term}')

    print()
    print('The most common nouns:')
    for (term, freq) in counts['noun'].most_common(10):
        print(f'{freq:>6} {term}')

    print()
    print('The most common verbs:')
    for (term, freq) in counts['verb'].most_common(10):
        print(f'{freq:>6} {term}')


def pos_freq_df(pos):
    tags = ['NOUN', 'VERB', 'ADJ', 'ADV', 'PRON']
    tag_names = {
        'NOUN': 'Noun',
        'VERB': 'Verb',
        'ADJ': 'Adjective',
        'ADV': 'Adverb',
        'PRON': 'Pronoun',
    }

    total = sum(pos.values())
    if total <= 0:
        return pd.DataFrame([], columns=['POS', 'frequency (%)'])

    data = []
    for t in tags:
        data.append((tag_names[t], 100.0*pos[t]/total))

    other = 100.0 - sum(x[1] for x in data)
    data.append(('Other', other))

    return pd.DataFrame(data, columns=['POS', 'frequency (%)'])


def plot_pos_frequencies(pos_atl, pos_blogs):
    freq_atl = pos_freq_df(pos_atl)
    freq_atl['dataset'] = 'Expert statements'

    freq_blogs = pos_freq_df(pos_blogs)
    freq_blogs['dataset'] = 'Blogs'

    df = pd.concat([freq_atl, freq_blogs], ignore_index=True)

    Path('images').mkdir(exist_ok=True)
    p = sns.barplot(x='POS', y='frequency (%)', hue='dataset', data=df)
    p.get_figure().savefig('images/posfreq.png')


if __name__ == '__main__':
    main()
