from functools import lru_cache
from pathlib import Path

import amrlib
import click
import stanza
import torch
from tqdm import tqdm

from frank_set import FrankDataset

tqdm.pandas()
stanza.download('en')
device = 'cuda' if torch.cuda.is_available() else 'cpu'


@lru_cache(maxsize=None)
def sentence_tokenize(text, segmenter):
    return [sent.text for sent in segmenter(text).sentences]


@lru_cache(maxsize=None)
def generate_amr_graphs_sents(sentences: tuple[str, ...], stog):
    return stog.parse_sents(list(sentences))


def create_amr_graphs(frank_df, stog_model_dir):
    stanza_tokenizer = stanza.Pipeline(lang='en', processors='tokenize')
    stog = amrlib.load_stog_model(model_dir=stog_model_dir, device=device)

    frank_df['article_sentences'] = frank_df['article'].progress_apply(
        lambda x: sentence_tokenize(x, stanza_tokenizer)
    )

    frank_df['summary_graph'] = frank_df['summary_sentence'].progress_apply(
        lambda x: stog.parse_sents([x])[0]
    )

    frank_df['article_graphs'] = frank_df['article_sentences'].progress_apply(
        lambda x: generate_amr_graphs_sents(tuple(x), stog)
    )

    return frank_df.explode('article_graphs')


@click.command()
@click.argument('frank_path', type=str)
@click.argument('stog_model_dir', type=str)
@click.argument('output_path', type=str, default='../data')
def main(frank_path, stog_model_dir, output_path):
    out_path = Path(output_path)

    dataset = FrankDataset(frank_path)
    dataset = create_amr_graphs(dataset.data, stog_model_dir)


    with open(out_path/'fsrc.amr', 'w') as f:
        for graph in dataset['summary_graph']:
            f.write(graph + '\n\n')

    with open(out_path/'ftgt.amr', 'w') as f:
        for graph in dataset['article_graphs']:
            f.write(graph + '\n\n')


if __name__ == '__main__':
    main()
