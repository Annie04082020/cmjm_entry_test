# Data Study Report (9/5, 9/6)

## AI Assistance
Used Antigravity (Claude) to help write and debug Python scripts for data inspection and solution.py. All code was reviewed and understood by the author.

## Process
- Study readme
- Loading data
- First glance of data
- Discuss and write code with Antigravity(Claude)
- Check results
- Discuss and analyse the results with antigravity

## Breif Data Understanding (before processing)

- 大致看起來像是細胞型態跟藥物各種組合的實驗數據，但我看不懂實際上這些名詞跟數字代表甚麼意思

- test 跟 train 是同個格式，差別在 test 沒有response 結果(大概是特定 cell 狀態+特定藥物會造成什麼結果的數值?)
然後cell 跟drug id就是分別去取 drug embedding 跟 cell embedding的32維度查表資料這樣

- 所以實際上 AI 拿來訓練用的東西會分成32(cell embedding)+32(drug embedding)，總共 64 欄

- 同時也會需要額外一個欄位，用來區分原本是 test 還是 train 還是 validation 的資料，才不會讓模型學到原本是 test 的資料

## Decisions

- 本來有想要讓 train 裡面每個 cell 跟 drug 的種類都分成 80:20 的比例去切，但後來發現幾乎每一種都只有一筆資料，最後直接隨機
- 使用 jupyter notebook 分成不同 part 來做可以更明確保留階段性成果(以這次的題目來說)
- random forest 跟 linear regression、PCA 都跑過一遍進行比較實驗

## Results and Feedback

### Part1 Data Loading and Inspection

- Train 共有503筆、4欄資料
欄位分別是 sample_id, cell_line_id, drug_id, response
- Test 共有100筆、3欄資料
欄位分別是 sample_id, cell_line_id, drug_id
- cell embedding 有360筆、34欄資料
欄位分別是 cell_line_id 跟其他32維度的資料
- drug embedding 有208筆、33欄資料
欄位分別是 drug_id 跟其他32維度的資料

train 和 test 的架構相同，惟test會缺少response(作為預測目標的數值)
cell_line_id 和 drug_id 為查表內容，故在模型輸入時會被替換成32維度的cell embedding 和 drug embedding

### Part2 Construction of Processed Feature Tables

- [train_processed.csv](results/train_processed.csv)
- [test_processed.csv](results/test_processed.csv)



### Part3 Data Validation and Quality Control

![](figures/fig_id_overlap_pie.png)

- 資料集特徵: train 清理後樣本數共 500 筆，其中cell 共 328 種，test 共 98 筆，drug 共 197 種；test 清理後樣本數共 98 筆，其中 cell 有 89 種，drug 84 種。
- 平均每種樣本數並不多，並且有部分種類只存在於 test 或是 train中，因此訓練結果非常考驗模型的泛化能力



### Part4 Baseline Model Comparison

[Random Forest](results/RandomForest/metrics.csv)
[Linear Regression](results/LinearRegression/metrics.csv)

### Part5 Lightweight Model Experiment

[Random Forest](results/RandomForest/metrics_part5.csv)

### Part6



-----

Viewed report.md:1-69

老實說，現在還有幾個問題要修：

---

**❌ 錯誤（要改）**

1. **Line 37**: `cell embedding 有60筆` → 應該是 **360筆**（打少一個字）
2. **Line 21**: feature 欄位說明不對，模型實際吃的是 **64 欄**（32+32），不是 65/66，`sample_id`、`cell_line_id`、`drug_id` 不餵給模型
3. **Line 1**: `Breif` → `Brief`（拼字）

---

**⚠️ 內容太薄（需要補）**

| Section | 現狀 | 缺什麼 |
|---|---|---|
| **Part2** | 只有兩個檔案連結 | 要說明怎麼 merge、欄位怎麼命名（cell_emb_* 和 drug_emb_*）|
| **Part3** | 有圖、有統計數字 | 要列出四個已知問題各自怎麼偵測、怎麼處理（README 明確要求這三點）|
| **Part4** | 只有 CSV 連結 | 要寫結果數字、哪個最好、為什麼 |
| **Part5** | 只有 CSV 連結 | 要說明用什麼 lightweight 策略、結果比較、為什麼有用 |
| **Part6** | 空白 | 待補 |

---

**Part3 特別重要**，README 說：
> *"For each issue: Confirm detected, Describe how handled, Ensure final tables remain valid"*

要一條一條列出來，不能只放統計數字。

要我列出 Part3 應該包含哪四條的框架讓你自己填嗎？

Edited report.md
Edited report.md
Edited report.md
Viewed report.md:32-56