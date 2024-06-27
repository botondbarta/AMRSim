# AMRSim

This repository contains the code for our ACL-2023
paper: [Evaluate AMR Graph Similarity via Self-supervised Learning](https://aclanthology.org/2023.acl-long.892/).
AMRSim collects silver AMR graphs and utilizes self-supervised learning methods to evaluate the similarity of AMR
graphs. 
AMRSim calculates the cosine of contextualized token embeddings, making it alignment-free.

## Requirements

Run the following script to install the dependencies:

```
conda create --name my-env python=3.10.10

pip install -e .
```
Install [amr-utils](https://github.com/ablodge/amr-utils):
```
git clone https://github.com//ablodge/amr-utils
pip install penman
pip install ./amr-utils
```

## Computing AMR Similarity

### Returning Similarity with pre-trained model

Download the model from [Google drive](https://drive.google.com/file/d/1klTrvv3hpIPxaCoMbRI7IJDme-Vq3UPS/view?usp=share_link) and
unzip to a directory (/path/to/model/).

Modify the modules.json in /path/to/model/ct-wiki-bert/modules.json to use the modified_sentence_transformer package from amrsim.

```json
[
  {
    "idx": 0,
    "name": "0",
    "path": "0_ExtendTransformer",
    "type": "amrsim.modified_sentence_transformers.models.ExtendTransformer"
  },
  {
    "idx": 1,
    "name": "1",
    "path": "1_Pooling",
    "type": "amrsim.modified_sentence_transformers.models.Pooling"
  }
]
```

```python
from amrsim import amrsimscore_for_snt
from amrsim.modified_sentence_transformers import ExtendSentenceTransformer
import amrlib


stog_model_dir = 'path/to/amrlib/data/model_parse_xfm_bart_large-v0_1_0'
amrsim_model_path = "path/to/model/ct-wiki-bert"

model = ExtendSentenceTransformer(amrsim_model_path)
stog_model = amrlib.load_stog_model(model_dir=stog_model_dir)

snt1 = "The cat is on the mat."
snt2 = "The cat is on the carpet."
amrsimscore_for_snt(snt1, snt2, model, stog_model)
```


## Citation
```
@inproceedings{shou-lin-2023-evaluate,
    title = "Evaluate {AMR} Graph Similarity via Self-supervised Learning",
    author = "Shou, Ziyi  and
      Lin, Fangzhen",
    booktitle = "Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)",
    month = jul,
    year = "2023",
    address = "Toronto, Canada",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2023.acl-long.892",
    pages = "16112--16123",
}
```


## Acknowledgments
This project uses code from the following open source projects:
- [AMR-DA](https://github.com/zzshou/amr-data-augmentation)
- [FactGraph](https://github.com/amazon-science/fact-graph)
- [Sentence-Transformers](https://www.sbert.net)

Thank you to the contributors of these projects for their valuable contributions to the open source community.

