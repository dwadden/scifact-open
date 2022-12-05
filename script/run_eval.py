"""
Reproduce evaluations from Table 5 of the SciFact-Open paper.
"""

import json

import pandas as pd
import numpy as np
from sklearn.utils.extmath import stable_cumsum


########################################################################################

# Utility functions


def load_jsonl(fname):
    return [json.loads(line) for line in open(fname)]


########################################################################################

# Evaluation functions. Adapted from scikit-learn.

# I needed to make some slight modifications because in standard retrieval the goal is
# to predict relevance (0 / 1), whereas here we need to predict not just relevants but
# also correctly predict SUPPORTS vs. REFUTES.


def precision_recall_curve(preds):
    # Adapted from: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_curve.html
    n_relevant = np.sum(preds["label"] != "NEI")

    # Drop gold examples that weren't retrieved. The model never made predictions on
    # these. The model is penalized for missing these examples, since they're included
    # in `n_relevant`.
    preds = preds.sort_values("rank").dropna(subset=["best_label", "best_score"])

    # True pos has best label equal to gold label, and gold label is not NEI.
    true_pos = (preds["best_label"] == preds["label"]) & (preds["label"] != "NEI")

    true_pos = (true_pos).values.astype(np.int)
    false_pos = 1 - true_pos
    y_score = preds["best_score"].values

    distinct_value_indices = np.where(np.diff(y_score))[0]
    threshold_idxs = np.r_[distinct_value_indices, y_score.size - 1]

    tps = stable_cumsum(true_pos)[threshold_idxs]
    fps = stable_cumsum(false_pos)[threshold_idxs]
    thresholds = y_score[threshold_idxs]

    precision = tps / (tps + fps)
    precision[np.isnan(precision)] = 0

    # Note that recall might never hit 1; some docs weren't identified in the retrieval
    # stage.
    recall = tps / n_relevant

    # stop when best recall attained
    # and reverse the outputs so recall is decreasing
    last_ind = tps.searchsorted(tps[-1])
    sl = slice(last_ind, None, -1)
    return np.r_[precision[sl], 1], np.r_[recall[sl], 0], thresholds[sl]


def compute_average_precision(preds):
    precision, recall, _ = precision_recall_curve(preds)

    average_precision = -np.sum(np.diff(recall) * np.array(precision)[:-1])
    return average_precision


def compute_f1_score(preds):
    n_relevant = np.sum(preds["label"] != "NEI")
    is_predicted = preds["predicted_label"] != "NEI"
    is_correct = (preds["label"] != "NEI") & (
        preds["label"] == preds["predicted_label"]
    )

    precision = is_correct.sum() / is_predicted.sum()
    recall = is_correct.sum() / n_relevant
    f1 = (2 * precision * recall) / (precision + recall)

    res = {"P": precision, "R": recall, "F1": f1}
    return res


########################################################################################

# Evaluator class.


class Evaluator:
    """
    Run evaluation on SciFact-Open for all models.
    Reproduces Table 5 in the paper, modulo differences due to bootstrap-resampling.
    """

    def __init__(self, claims_file, predictions_file):
        preds = pd.read_parquet(predictions_file)
        self.preds = self._format_predictions(preds)
        claims = load_jsonl(claims_file)
        self.gold = self._simplify_claims(claims)

    @staticmethod
    def _simplify_claims(claims):
        res = []
        for claim in claims:
            for doc_id, evidence in claim["evidence"].items():
                to_append = {
                    "claim_id": claim["id"],
                    "doc_id": int(doc_id),
                    "label": evidence["label"],
                }
                res.append(to_append)

        return pd.DataFrame(res)

    @staticmethod
    def _format_predictions(preds):
        # Add field for the best non-NEI prediction, and the score associated with it.
        # Need this to compute precision-recall curve.
        best_scores = []
        best_labels = []
        for _, row in preds.iterrows():
            if row["p_contradict"] > row["p_support"]:
                best_score = row["p_contradict"]
                best_label = "CONTRADICT"
            else:
                best_score = row["p_support"]
                best_label = "SUPPORT"

            best_scores.append(best_score)
            best_labels.append(best_label)

        preds["best_score"] = best_scores
        preds["best_label"] = best_labels

        return preds

    def evaluate(self):
        """
        Invoke this method to run evaluation.
        """
        metrics = []
        models = sorted(self.preds["model"].unique())
        for model in models:
            cols = [
                "claim_id",
                "doc_id",
                "predicted_label",
                "rank",
                "best_score",
                "best_label",
            ]
            preds_model = self.preds.query(f"model == '{model}'")[cols]
            metrics_model = self._evaluate_model(preds_model)
            if model == "arsjoint":
                metrics_model["avg_precision"] = np.nan
            metrics_model["model"] = model
            metrics.append(metrics_model)

        metrics = pd.DataFrame(metrics).set_index("model") * 100
        print(metrics)

    def _evaluate_model(self, preds_model):
        # Merge gold and predicted.
        fillers = {"label": "NEI", "predicted_label": "NEI"}
        merged = self.gold.merge(
            preds_model, on=["claim_id", "doc_id"], how="outer"
        ).fillna(fillers)

        res = compute_f1_score(merged)
        res["avg_precision"] = compute_average_precision(merged)

        return res


########################################################################################

# Run evaluation.

if __name__ == "__main__":
    evaluator = Evaluator(
        claims_file="data/claims.jsonl",
        predictions_file="prediction/model_predictions.parqet",
    )
    evaluator.evaluate()
