from sklearn.metrics.pairwise import paired_cosine_distances

from amrsim.modified_sentence_transformers import ExtendSentenceTransformer, InputExample
from amrsim.preprocess.preprocess import generate_ref_edge
from amrsim.preprocess.utils import simplify_amr_nopar, load_single_amr_from_string, combine, create_amr_graph


__all__ = ['amrsimscore_for_amr',
           'amrsimscore_for_snt',
           'ExtendSentenceTransformer']


def return_simscore(model, example):
    model.training = False
    sentences1 = example.texts[0]
    sentences2 = example.texts[1]
    ref1_graphs_index = example.edge_index[0]
    ref1_graphs_type = example.edge_type[0]
    ref1_pos_ids = example.pos_ids[0]
    embeddings1 = model.encode([sentences1], graph_index=[ref1_graphs_index],
                               graph_type=[ref1_graphs_type], batch_size=1,
                               convert_to_numpy=True,
                               pos_ids=[ref1_pos_ids])

    ref2_graphs_index = example.edge_index[1]
    ref2_graphs_type = example.edge_type[1]
    ref2_pos_ids = example.pos_ids[1]
    embeddings2 = model.encode([sentences2], graph_index=[ref2_graphs_index],
                               graph_type=[ref2_graphs_type], batch_size=1,
                               convert_to_numpy=True,
                               pos_ids=[ref2_pos_ids])
    cosine_scores = 1 - (paired_cosine_distances(embeddings1, embeddings2))

    return cosine_scores[0]


def amrsimscore_for_amr(amr1, amr2, model):
    src = load_single_amr_from_string(amr1, remove_wiki=True)
    tgt = load_single_amr_from_string(amr2, remove_wiki=True)
    tokenizer = model.tokenizer
    combined = combine(src, tgt)
    max_seq_length = model.max_seq_length
    edge_index, edge_type, pos_ids = generate_ref_edge(combined, tokenizer, max_seq_length)
    test_sample = InputExample(texts=[combined['graph_ref1']['amr_simple'], combined['graph_ref2']['amr_simple']],
                               edge_index=edge_index, edge_type=edge_type, pos_ids=pos_ids)

    return return_simscore(model, test_sample)


def amrsimscore_for_snt(snt1, snt2, stog, model):
    amr1 = create_amr_graph(snt1, stog)
    amr2 = create_amr_graph(snt2, stog)

    return amrsimscore_for_amr(amr1, amr2, model)
