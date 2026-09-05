import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")

train    = pd.read_csv(DATA_DIR / "train.csv")
test     = pd.read_csv(DATA_DIR / "test.csv")
cell_emb = pd.read_csv(DATA_DIR / "global_cell_embeddings.csv")
drug_emb = pd.read_csv(DATA_DIR / "drug_embeddings.csv")

# 清掉 trailing space（README 說 drug_id 有這問題）
train["drug_id"] = train["drug_id"].str.strip()
test["drug_id"]  = test["drug_id"].str.strip()

SEP = "=" * 50

# ── train.csv ────────────────────────────────────────
print(SEP)
print("train.csv")
print(f"  總行數:           {len(train)}")
print(f"  唯一 cell_line_id: {train['cell_line_id'].nunique()}")
print(f"  唯一 drug_id:      {train['drug_id'].nunique()}")
print(f"  重複行數:          {train.duplicated(subset=['cell_line_id','drug_id','response']).sum()}")

# ── test.csv ─────────────────────────────────────────
print(SEP)
print("test.csv")
print(f"  總行數:           {len(test)}")
print(f"  唯一 cell_line_id: {test['cell_line_id'].nunique()}")
print(f"  唯一 drug_id:      {test['drug_id'].nunique()}")

# ── cell embeddings ──────────────────────────────────
print(SEP)
print("global_cell_embeddings.csv")
print(f"  總行數 (cell lines): {len(cell_emb)}")
emb_cols = [c for c in cell_emb.columns if c.startswith("emb_")]
print(f"  embedding 維度:      {len(emb_cols)}")
nan_count = cell_emb[emb_cols].isna().sum().sum()
print(f"  NaN 總數:            {nan_count}")

# ── drug embeddings ──────────────────────────────────
print(SEP)
print("drug_embeddings.csv")
print(f"  總行數 (drugs):  {len(drug_emb)}")
demb_cols = [c for c in drug_emb.columns if c.startswith("emb_")]
print(f"  embedding 維度:  {len(demb_cols)}")

# ── train / test 交集 ────────────────────────────────
print(SEP)
print("Train vs Test 重疊")
train_cells = set(train["cell_line_id"])
test_cells  = set(test["cell_line_id"])
print(f"  cell_line: train 有 {len(train_cells)} 個，test 有 {len(test_cells)} 個")
print(f"    -> 共同: {len(train_cells & test_cells)}，test 獨有: {len(test_cells - train_cells)}")

train_drugs = set(train["drug_id"])
test_drugs  = set(test["drug_id"])
print(f"  drug:      train 有 {len(train_drugs)} 個，test 有 {len(test_drugs)} 個")
print(f"    -> 共同: {len(train_drugs & test_drugs)}，test 獨有: {len(test_drugs - train_drugs)}")

# ── cell_line / drug 在 train 裡各出現幾次 ───────────
print(SEP)
print("每個 cell_line_id 在 train 裡出現次數（前 10）：")
print(train["cell_line_id"].value_counts().head(10).to_string())

print()
print("每個 drug_id 在 train 裡出現次數（前 10）：")
print(train["drug_id"].value_counts().head(10).to_string())
print(SEP)
