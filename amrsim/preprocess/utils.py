import json

import penman
import re
from amr_utils.amr_readers import AMR_Reader, PENMAN_Wrapper, Matedata_Parser

TYPES_AMR = ['person', 'family', 'animal', 'language', 'nationality', 'ethnic-group', 'regional-group',
             'political-movement', 'religious-group', 'organization', 'company', 'government-organization',
             'military', 'criminal-organization', 'political-party', 'market-sector',
             'school', 'university', 'research-institute', 'team', 'league', 'location', 'city', 'city-district',
             'county', 'state', 'province', 'territory', 'country', 'local-region',
             'country-region', 'world-region', 'continent', 'ocean', 'sea', 'lake', 'river', 'gulf', 'bay',
             'strait', 'canal', 'peninsula', 'mountain', 'volcano', 'valley',
             'facility', 'airport', 'station', 'port', 'tunnel', 'bridge', 'road', 'railway-line', 'canal', 'building',
             'theater', 'museum', 'palace', 'hotel', 'worship-place', 'market', 'sports-facility', 'park', 'zoo',
             'amusement-park',
             'event', 'incident', 'natural-disaster', 'earthquake', 'war', 'conference', 'game', 'festival',
             'product', 'vehicle', 'ship', 'aircraft', 'aircraft-type', 'spaceship', 'car-make', 'work-of-art',
             'picture',
             'music', 'show', 'broadcast-program', 'have-org-role-91',
             'publication', 'book', 'newspaper', 'magazine', 'journal', 'natural-object',
             'canyon', 'island', 'desert', 'forest moon', 'planet', 'star', 'constellation',
             'award', 'law', 'court-decision', 'treaty', 'music-key', 'musical-note', 'food-dish', 'writing-script',
             'variable', 'program']


def simplify_nopar(tokens, v2c):
    # SENSE_PATTERN = re.compile('-[0-9][0-9]$')
    mapping = {}
    new_tokens = []
    for idx, tok in enumerate(tokens):
        # ignore instance-of
        if tok.startswith('('):
            # new_tokens.append('(')
            last_map = tok.replace("(", "")
            continue
        elif tok == '/':
            save_map = True
            continue
        # predicates, we remove any alignment information and parenthesis
        elif tok.startswith(':'):

            new_tok = tok.strip(')')
            new_tok = new_tok.split('~')[0]
            new_tokens.append(new_tok)

            count_ = tok.count(')')
            # for _ in range(count_):
            #     new_tokens.append(')')

        # concepts/reentrancies, treated similar as above
        else:
            new_tok = tok.strip(')')
            new_tok = new_tok.split('~')[0]

            if new_tok == "":
                continue

            # now we check if it is a concept or a variable (reentrancy)
            if new_tok in v2c:
                # reentrancy: replace with concept
                if new_tok not in mapping:
                    mapping[new_tok] = set()
                mapping[new_tok].add(len(new_tokens))

                if v2c[new_tok] is not None:
                    new_tok = v2c[new_tok]


            # check number
            elif new_tok.isnumeric():
                new_tok = new_tok

            # remove quotes
            elif new_tok[0] == '"' and new_tok[-1] == '"':
                new_tok = new_tok[1:-1]

            if new_tok != "":
                new_tokens.append(new_tok)

            if save_map:
                if last_map not in mapping:
                    mapping[last_map] = set()

                mapping[last_map].add(len(new_tokens) - 1)
                save_map = False

            count_ = tok.count(')')
    return new_tokens, mapping


def get_positions(new_tokens, src):
    pos = []
    for idx, n in enumerate(new_tokens):
        if n == src:
            pos.append(idx)
    return pos


def get_line_amr_graph(graph, new_tokens, mapping, roles_in_order, amr):
    triples = []
    nodes_to_print = new_tokens

    graph_triples = graph.triples

    edge_id = -1
    triples_set = set()
    count_roles = 0
    for triple in graph_triples:
        src, edge, tgt = triple
        if edge == ':instance' or edge == ':instance-of':
            continue

        # if penman.layout.appears_inverted(graph_penman, v):
        if "-of" in roles_in_order[count_roles] and "-off" not in roles_in_order[count_roles]:
            if edge != ':consist-of':
                edge = edge + "-of"
                old_tgt = tgt
                tgt = src
                src = old_tgt

        try:
            assert roles_in_order[count_roles] == edge
        except:
            print(roles_in_order)
            print(count_roles)
            print(edge)

        count_roles += 1

        if edge == ':wiki':
            continue

        src = str(src).replace("\"", "")
        tgt = str(tgt).replace("\"", "")

        try:
            if src not in mapping:
                src_id = get_positions(new_tokens, src)
            else:
                src_id = sorted(list(mapping[src]))
            # check edge to verify
            edge_id = get_edge(new_tokens, edge, edge_id, triple, mapping, graph)

            if tgt not in mapping:
                tgt_id = get_positions(new_tokens, tgt)
            else:
                tgt_id = sorted(list(mapping[tgt]))
        except:
            print(graph_triples)
            print(src, edge, tgt)
            print("error")

            print(" ".join(new_tokens))

        for s_id in src_id:
            if (s_id, edge_id, 'd') not in triples_set:
                triples.append((s_id, edge_id, 'd'))
                triples_set.add((s_id, edge_id, 'd'))
                triples.append((edge_id, s_id, 'r'))
        for t_id in tgt_id:
            if (edge_id, t_id, 'd') not in triples_set:
                triples.append((edge_id, t_id, 'd'))
                triples_set.add((edge_id, t_id, 'd'))
                triples.append((t_id, edge_id, 'r'))

    if nodes_to_print == []:
        # single node graph, first triple is ":top", second triple is the node
        triples.append((0, 0, 's'))
    return nodes_to_print, triples


def get_edge(tokens, edge, edge_id, triple, mapping, graph):
    for idx in range(edge_id + 1, len(tokens)):
        if tokens[idx] == edge:
            return idx


def create_set_instances(graph_penman):
    instances = graph_penman.instances()
    dict_insts = {}
    for i in instances:
        dict_insts[i.source] = i.target
    return dict_insts


def simplify_amr_nopar(amr):
    try:
        graph_penman = penman.decode(amr)
        v2c_penman = create_set_instances(graph_penman)

        amr_penman = penman.encode(graph_penman)
        amr_penman = amr_penman.replace('\t', '')
        amr_penman = amr_penman.replace('\n', '')
        tokens = amr_penman.split()
    except:
        print('error')
        exit()
        return None

    try:
        new_tokens, mapping = simplify_nopar(tokens, v2c_penman)
    except Exception as e:
        print(e.message, e.args)
        print('error simply')
        # exit()
        return None

    roles_in_order = []
    for token in amr_penman.split():
        if token.startswith(":"):
            if token == ':instance-of':
                continue
            roles_in_order.append(token)

    nodes, triples = get_line_amr_graph(graph_penman, new_tokens, mapping, roles_in_order, amr)
    triples = sorted(triples)

    return nodes, triples


def create_amr_graph(sentence: str, stog_model):
    return stog_model.parse_sents([sentence])[0]


def load_single_amr_from_string(amr_string, remove_wiki=False, output_alignments=False):
    print('[amr]', 'Loading AMR from string')
    penman_wrapper = PENMAN_Wrapper(style='isi')
    metadata_parser = Matedata_Parser()

    # Split the string into metadata and AMR parts
    parts = amr_string.strip().split('\n')
    metadata_lines = [line for line in parts if line.startswith('# ::')]
    amr_lines = [line for line in parts if not line.startswith('# ::')]

    # Parse metadata
    metadata = {}
    for line in metadata_lines:
        key, value = line[4:].split(' ', 1)
        metadata[key] = value.strip()

    # Join AMR lines
    amr_string = ''.join(amr_lines).strip()
    amr_string = re.sub(' +', ' ', amr_string)

    # Ensure the AMR string is valid
    if not amr_string.startswith('(') or not amr_string.endswith(')'):
        raise Exception('Could not parse AMR from: ', amr_string)

    # Get tokens from metadata or split the sentence
    tokens = metadata.get('tok', metadata.get('snt', '').split())
    tokens = AMR_Reader._clean_tokens(tokens)

    # Parse AMR
    amr, other_stuff = penman_wrapper.parse_amr(tokens, amr_string)
    amr.id = metadata.get('id', '0')

    # Handle alignments
    alignments = {}
    if output_alignments:
        alignments[amr.id] = []
        if 'alignments' in metadata:
            aligns = metadata['alignments'].split()
            if any('|' in a for a in aligns):
                jamr_labels = other_stuff[1]
                alignments[amr.id] = AMR_Reader._parse_jamr_alignments(amr, "string_input", aligns, jamr_labels,
                                                                       metadata_parser)
            else:
                isi_labels, isi_edge_labels = other_stuff[2:4]
                alignments[amr.id] = AMR_Reader._parse_isi_alignments(amr, "string_input", aligns, isi_labels,
                                                                      isi_edge_labels)
        else:
            alignments[amr.id] = other_stuff[4]

    # Store metadata
    amr.metadata = {k: v for k, v in metadata.items() if k not in ['tok', 'id']}

    # Remove wiki information if requested
    if remove_wiki:
        wiki_nodes = []
        wiki_edges = []
        for s, r, t in amr.edges.copy():
            if r == ':wiki':
                amr.edges.remove((s, r, t))
                del amr.nodes[t]
                wiki_nodes.append(t)
                wiki_edges.append((s, r, t))
        if output_alignments:
            for align in alignments[amr.id]:
                for n in wiki_nodes:
                    if n in align.nodes:
                        align.nodes.remove(n)
                for e in wiki_edges:
                    if e in align.edges:
                        align.edges.remove(e)

    if output_alignments:
        return amr, alignments
    return amr


def combine(src, tgt):
    error_log = 0
    error_log_claim = 0
    error_log_g = 0

    d = {}
    d['score'] = -1
    ref1_sen = ' '.join(src.tokens)
    d['ref1'] = ref1_sen
    ref1_graph = src.graph_string()

    graph_simple, triples = simplify_amr_nopar(ref1_graph)

    d['graph_ref1'] = {}
    graph_simple = ' '.join(graph_simple)
    d['graph_ref1']['amr_simple'] = graph_simple
    d['graph_ref1']['triples'] = json.dumps(triples)

    try:
        ref2_sen = ' '.join(tgt.tokens)
        d['ref2'] = ref2_sen
        ref2_graph = tgt.graph_string()

        graph_simple, triples = simplify_amr_nopar(ref2_graph)

        d['graph_ref2'] = {}
        graph_simple = ' '.join(graph_simple)
        d['graph_ref2']['amr_simple'] = graph_simple
        d['graph_ref2']['triples'] = json.dumps(triples)

    except:
        error_log_claim += 1
        print("skip graph claim", error_log_claim)
        d['graph_ref2'] = {}
        d['graph_ref2']['amr_simple'] = ''
        d['graph_ref2']['triples'] = ''

    print("skipped graph sents", error_log_g)
    print("skipped sents", error_log)
    print("skipped graph claim", error_log_claim)

    return d
