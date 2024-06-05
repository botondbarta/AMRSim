import json
from pathlib import Path

import amrlib
import pandas as pd
import stanza
from torch.utils.data import Dataset
from tqdm import tqdm

tqdm.pandas()
stanza.download('en')


class FrankDataset(Dataset):
    def __init__(self, root_dir, stog_model_dir=None):
        self.root_dir = Path(root_dir)

        self.segmenter = stanza.Pipeline(lang='en', processors='tokenize')
        self.stog = amrlib.load_stog_model(model_dir=stog_model_dir)

        self.data = self._load_data()
        self.data = self._create_graphs()

    def __getitem__(self, index):
        x = self.data[index]
        return x

    def __len__(self):
        return len(self.data)

    def _load_data(self):
        annotated_data = self.root_dir / "human_annotations_sentence.json"
        annotated_data = json.loads(annotated_data.read_text())

        data = []

        for row in annotated_data:
            for sentence, annotations in zip(row['summary_sentences'], row['summary_sentences_annotations']):
                sentence_annotation = {'article': row['article'], 'summary_sentence': sentence, 'split': row['split']}
                sentence_annotation['concatenated'] = sentence + '[SEP]' + row['article']

                label_count = {label: 0 for label in
                               ['RelE', 'EntE', 'CircE', 'OutE', 'GramE', 'CorefE', 'LinkE', 'NoE', 'OtherE']}
                for annotator in annotations:
                    for annotation in annotations[annotator]:
                        label_count[annotation] += 1

                for label in label_count:
                    sentence_annotation[label] = 1 if label_count[label] >= 2 else 0

                if any([sentence_annotation[label] for label in
                        ['RelE', 'EntE', 'CircE', 'OutE', 'GramE', 'CorefE', 'LinkE', 'OtherE']]):
                    sentence_annotation['factuality'] = 0
                else:
                    sentence_annotation['factuality'] = 1

                data.append(sentence_annotation)

        return pd.DataFrame(data)

    def _create_graphs(self):
        self.data['article_sentences'] = self.data['article'].progress_apply(
            lambda x: [sent.text for sent in self.segmenter(x).sentences]
        )

        self.data['graphs'] = self.data['article_sentences'].progress_apply(lambda x: self.stog.parse_sents(x))

        return self.data.explode('graphs')
