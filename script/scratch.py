x = {
    "id": number,                   # An integer claim ID.
    "claim": string,                # The text of the claim.
    "evidence": {                   # The evidence for the claim.
        [doc_id]:                  # The rationales for a single document, keyed by S2ORC ID.
            {
                "provenance": enum("citation" | "pooling")    # Evidence source. See below.
                "label": enum("SUPPORT" | "CONTRADICT"),      # Veracity label.
                "sentences": number[],                        # Evidence "highlights".
                "model_ranks": {[model_name]: number} | None  # Model ranks for evidence via pooling.
            }
    }
}
