# Scifact-Open

This repository contains data and analysis code for the paper [SciFact-Open: Towards open-domain scientific claim verification](https://arxiv.org/abs/2210.13777).

## Table of contents

- [Setup](#setup)
- [Data](#data)
- [Reproducing paper metrics](#reproducing-paper-metrics)
- [Coming soon](#coming-soon)

## Setup

First, create a Conda environment:

```bash
conda create --name scifact-open python=3.8.5   # Create Conda env.
conda activate scifact-open
pip install -r requirements.txt                 # Install dependencies
```

## Data

To get the data, run `bash script/get_data.sh` from the root of this directory. The script will download the data and populate two folders: `data` contains the annotations for SciFact-Open, and `prediction` contains model predictions for all models used for dataset creation and evaluation. More details on specific files in [data.md](doc/data.md) and [prediction.md](doc/prediction.md).

You can also download the tarball directly fro Google Drive by clicking [here](https://drive.google.com/uc?export=download&id=1sz-9hJTVex8h_jm_NPjXfmTrhi_8Sz-U).

## Reproducing paper metrics

To reproduce the main results reported in Table 5 in the paper, run `python script/run_eval.py`. The script will evaluate the predictions from `prediction/model_predictions.parqet` against the data in `data/claims.jsonl`, and print out evaluation metrics. Note that some metrics will differ slightly (0.1 F1 or so) from the results in Table 5, which reports evaluation metrics averaged over 1,000 bootstrap-resampled versions of the dataset.

## Coming soon

- **Claim revisions**: I will shortly upload examples of *claim revisions* which resolve ambiguity in cases of "claim / evidence specificity mismatch"; see p. 5 of the paper for more details.

- **Model predictions**: I'll post code to make predictions using at least the two MultiVerS models [MultiVerS](https://github.com/dwadden/multivers) models.
