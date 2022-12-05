# SciFact-Open data

After running `get_data.sh` as described in the `README`, a `data` folder will populate, containing the following files:

- `claims.jsonl`: Claims in SciFact-Open, annotated with evidence.
- `claims_metadata.jsonl`: Metadata associated with each claim.
- `corpus.jsonl`: The full SciFact-Open corpus of 500K research abstracts from [S2ORC](https://allenai.org/data/s2orc).
- `corpus_candidates.jsonl`: Subset of documents from `corpus.jsonl` that were retrieved for at least one claim.

Detailed descriptions of each file are included below.

## `claims.jsonl`

A `.jsonl` file with one claim per line, annotated with evidence. The schema is as follows:

```python
{
    "id": number,                   # An integer claim ID.
    "claim": string,                # The text of the claim.
    "evidence": {                   # The evidence for the claim.
        [doc_id]:                  # The rationales for a single document, keyed by S2ORC ID.
            {
                "provenance": enum("citation" | "pooling")    # Evidence source. See below.
                "label": enum("SUPPORT" | "CONTRADICT"),      # Veracity label.
                "sentences": number[],                        # Evidence "highlights".
                "model_ranks": {[model_name]: number} | None  # Ranks for pooled evidence.
            }
    }
}
```

Note that this format is altered slightly from the format for SciFact-Orig; see [below](#differences-from-scifact-orig) for details.

A few of these fields warrant explanation.

- **provenance**: As described in the [paper](https://arxiv.org/abs/2210.13777), evidence in SciFact-Open comes from two sources (see Sec. 3 of the paper for more details):
  1. Evidence from [SciFact-Orig](https://arxiv.org/abs/2004.14974), obtained via citation links.
  2. Evidence added in SciFact-Open via pooling.
  The `provenance` field indicates the source for each piece of evidence in the final SciFact-Open dataset.
- **sentences**: Evidence "highlights" justifying each labeling decision. The source of these highlights is different for `citation` evidence vs. `pooling` evidence:
  - For `citation` evidence, highlights were hand-annotated by experts and are high-quality.
  - For `pooling` evidence, highlights were *not* hand-annotated. Instead, we include the predicted highglights from the model(s) that identified the evidence. These predictions may be incorrect, but are included for convenience and to facilitate future research.
- **model_ranks**: For pooled data collection, predicted evidence is ranked by model confidence, and the `k` most-confidence predictions for each model are annotated; we used `k=250`.
  - For `pooling` evidence, this field provides the rank assigned to this piece of evidence by each model.
  - For `citation` evidence, this field is set to `None`.

Below, we provide an example of a claim with two pieces of evidence: one from SciFact-Orig, and one identified via pooling.

```python
{
  "id": 170,
  "claim": "Bariatric surgery reduces resolution of diabetes.",
  "evidence": {
    "5824985": {
      "provenance": "citation",
      "label": "CONTRADICT",
      "sentences": [
        10,
        15
      ],
      "model_ranks": None
    },

    "7854739": {
      "provenance": "pooling",
      "label": "CONTRADICT",
      "sentences": [
        2,
        5,
        6
      ],
      "model_ranks": {
        "multivers_10": 4556,
        "multivers_20": 3881,
        "paragraph_joint": 947,
        "vert5erini": 120
      }
    }
  }
}
```

### Differences from SciFact-Orig

The format here is slightly different from the format for the original [SciFact dataset](https://github.com/allenai/scifact/blob/master/doc/data.md). In that work, a single document could be associated with multiple *evidence sets*, each of which provides sufficient justification to support or refute the claim. For instance:

```python
{
  # SciFact-Orig
  "id": 263,
  "claim": "Citrullinated proteins externalized in neutrophil extracellular traps act indirectly to disrupt the inflammatory cycle.",
  "evidence": {
    "30041340": [   # Multiple evidence sets associated with a single document.
      { "sentences": [0, 1],
        "label": "CONTRADICT" },
      { "sentences": [11],
        "label": "CONTRADICT" }
    ]
  }
}
```

However, we didn't end up using this evidence set structure in our modeling or evaluation. Therefore, in this work, we simplify things a bit by "flattening" evidence sets, as follows:

```python
{
  # SciFact-Open
  "id": 263,
  "claim": "Citrullinated proteins externalized in neutrophil extracellular traps act indirectly to disrupt the inflammatory cycle.",
  "evidence": {
    "30041340": {   # Flattened evidence, including all highlights for this document.
        "sentences": [0, 1, 11],
        "label": "CONTRADICT"
    },
  }
}
```

## `claims_metadata.jsonl`

Each line includes metadata for a single claim, ordered as in `claims.jsonl`. This information isn't needed for any modeling task related to SciFact-Open, but may be of interest for those interested in designing and analyzing datasets. As background, claims in SciFact were created by re-writing citation sentences found in documents in the S2ORC corpus. We refer to the document used as the source of the claim as the "source document".

```python
{
  "id": number   # Same ID's as in `claims.jsonl`.
  "source_doc_id": number # The S2ORC ID of the document
  "source_metadata": {    # Metadata on claim source document.
    "paper_id": string
    "title": string
    "year": number
    "arxiv_id": string | None
    "pmc_id": string | None
    "pubmed_id": string | None
    "venue": string | None
    "journal": string | None
  },
  "cited_doc_ids": [number] # Documents mentioned in source citation
}
```

## `corpus.jsonl`

A single line represents a document from the SciFact-Open corpus.

```python
{
    "doc_id": number,               # The document's S2ORC ID.
    "title": string,                # The title.
    "abstract": string[],           # The abstract, written as a list of sentences.
    "metadata": {
        "paper_id": string,         # Redundant with `doc_id` above.
        "title": string,
        "year": number,
        "venue": string,
        "s2orc_version: string
    },
    "scifact_orig": bool            # True if this document was part of the corpus from SciFact-Orig
}
```

## `corpus_candidates.jsonl`

This file contains the subset of ~12K documents from `corpus.jsonl` that either contain evidence indicated via citation links (from SciFact-Orig), or were identified via pooling as potential evidence candidates (from SciFact-Open).
