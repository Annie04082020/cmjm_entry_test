# Programming Assessment

## Data Processing, Feature Table Construction, and Lightweight Model Evaluation

### Background

In computational drug response prediction, an essential task is to predict how sensitive a given cancer cell line is to a given drug. Each cell line can be represented by a numeric embedding vector (derived from its genomic profile), and each drug can similarly be represented by an embedding vector (derived from its molecular structure). The prediction target is a continuous drug response value (log IC50).

In this assessment you will work with a small dataset sampled from this setting.

---

### Provided Files

| File | Key Columns | Description |
|------|-------------|-------------|
| `train.csv` | `sample_id`, `cell_line_id`, `drug_id`, `response` | Training samples with drug response values |
| `test.csv` | `sample_id`, `cell_line_id`, `drug_id` | Test samples (no response column) |
| `global_cell_embeddings.csv` | `cell_line_id`, `emb_0` ... `emb_31` | 32-dimensional embedding for each cell line |
| `drug_embeddings.csv` | `drug_id`, `emb_0` ... `emb_31` | 32-dimensional embedding for each drug |

---

### Required Tasks

#### Part 1. Data Loading and Inspection

- Read all four input files.
- Report the dimensions (rows, columns) of each file.
- Inspect and describe the column structure of each file.

#### Part 2. Construction of Processed Feature Tables

Create the following output files by merging the response/ID tables with their corresponding embedding tables:

**`train_processed.csv`** — merge `train.csv` with `global_cell_embeddings.csv` and `drug_embeddings.csv`

**`test_processed.csv`** — merge `test.csv` with `global_cell_embeddings.csv` and `drug_embeddings.csv`

Each row in the processed file should contain the sample identifiers, the cell line embedding features, the drug embedding features, and (for training data) the response value.

#### Part 3. Data Validation and Quality Control

**The provided files contain the following known data issues. You are expected to detect and handle all of them:**

1. **Duplicate rows** — `train.csv` contains a small number of duplicated entries (identical `cell_line_id`, `drug_id`, and `response` but different `sample_id`).
2. **Trailing whitespace in IDs** — Some `drug_id` values in `train.csv` contain trailing spaces, which will cause merge failures if not cleaned.
3. **Missing values in embeddings** — `global_cell_embeddings.csv` contains a few `NaN` values scattered across its embedding columns.
4. **Unmatched IDs** — Some `cell_line_id` values in `test.csv` do not have a corresponding entry in `global_cell_embeddings.csv`.

For each issue, please:

1. Confirm that you detected it (e.g., show counts or affected rows),
2. Describe how you handled it, and
3. Ensure that the final processed tables remain valid for downstream use.

#### Part 4 (Optional Bonus 1). Baseline Model Comparison

Using the processed training data (train_processed.csv), train and compare the following three baseline models to predict `response`:

| Model | Features Used |
|-------|---------------|
| Model A | Cell line embeddings only (32 features) |
| Model B | Drug embeddings only (32 features) |
| Model C | Cell line + Drug embeddings combined (64 features) |

**Allowed model types:** Linear Regression or Random Forest Regressor

**Requirements:**

- Use a simple train/validation split (80/20)
- Report the validation **Mean Squared Error (MSE)** for all three models
- Briefly indicate which feature set performed best and why that might be the case

This part is intended as a basic modeling exercise. The focus is on implementation quality rather than parameter tuning.

#### Part 5 (Optional Bonus 2). Lightweight Model Experiment

Starting from Model C, implement **one** simple strategy to make the model more lightweight, and compare it with the original Model C.

You may choose one of the following approaches:

- Dimensionality reduction (e.g., PCA)
- Feature selection (e.g., based on importance scores)
- A smaller model with fewer parameters
- Distillation into a simpler model

Please report:

- Which lightweight strategy you used
- The resulting validation MSE
- A brief comparison with the original Model C
- Why your chosen approach may be useful for lightweight AI deployment

---

### Deliverables

Your code must be executable from start to finish without manual editing of intermediate files.

**Within 24 hours** — submit your code and results:

| Deliverable | Description |
|-------------|-------------|
| `train_processed.csv` | Processed training feature table |
| `test_processed.csv` | Processed test feature table |
| `metrics.csv` (if attempted) | Validation MSE for each model (at minimum: columns `model` and `mse`) |
| Source code | A single script (e.g., `solution.py`) or a small project folder covering all steps above |

**Within 48 hours** — submit your report:

| Deliverable | Description |
|-------------|-------------|
| `report.md` or `report.pdf` | Report: how you merged the data, what data issues you found and how you handled them, which model performed best (if attempted) and why, and (if attempted) your lightweight strategy |

---

### Submission

Upload all deliverables to the shared Google Drive folder provided to you.

---

### Technical Notes

- You may use the programming language you prefer, though **Python** is suggested.
- If using Python, standard packages such as `pandas`, `numpy`, and `scikit-learn` are sufficient.
- No deep learning framework is required.
- Please prioritize **clarity**, **correctness**, and **reproducibility**.
