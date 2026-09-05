# CMJM Lab Entry Assessment
# 資料夾結構說明

## 環境設定

### conda 環境（推薦）
```bash
conda activate cmjm_entry
```

### 從頭建立（別人復現）
```bash
conda env create -f environment.yml
conda activate cmjm_entry
python -m ipykernel install --user --name cmjm_entry --display-name "Python (cmjm_entry)"
```

### 啟動 Jupyter
```bash
conda activate cmjm_entry
jupyter notebook starter_notebook.ipynb
```

---

## 環境內容（cmjm_entry）
| 套件 | 用途 |
|------|------|
| pandas | 表格資料處理（核心）|
| numpy | 數值運算 |
| scipy | 統計檢定（t-test, correlation 等）|
| matplotlib | 畫圖 |
| seaborn | 統計視覺化 |
| scikit-learn | 機器學習（若作業需要）|
| statsmodels | 迴歸模型 / OLS |
| openpyxl / xlrd | 讀 Excel 檔 |
| jupyter / ipykernel | Notebook 環境 |

---

## 資料夾結構（建議）
```
cmjm_entry/
├── data/               ← 把收到的資料檔放這裡（不要改路徑）
├── figures/            ← 圖表輸出（程式自動建立）
├── starter_notebook.ipynb  ← 從這裡開始
├── requirements.txt    ← pip 可用
├── environment.yml     ← conda 復現用
└── README.md
```

---

## CMJM 評分重點提醒
1. **Correctness** — 結果要對，且要能說明你怎麼確認的
2. **Reproducibility** — 不能 hard-code 路徑，別人的電腦也要跑得起來
3. **Clarity** — 程式碼要可讀，決策要有簡短 comment
4. **Quality of reasoning** — 報告裡的「為什麼」比「做了什麼」更重要
5. **AI disclosure** — 用了 AI 助理要說明，但每行程式碼都要能解釋
