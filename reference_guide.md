# CMJM Lab Entry Programming Assessment: 技術實作與分析全參考指南 (Reference Guide)

> **文件定位**：本文件依據實驗室招募任務要求（README）及完整實驗流程撰寫，收錄專案中的**領域背景名詞**、**程式碼實作細節**、**資料清洗與模型決策理由**、**實驗結果數據**以及**反思與泛化分析**。供個人撰寫報告時隨時參照、查閱與引用。

---

## 目錄
1. [領域背景與核心名詞解釋](#1-領域背景與核心名詞解釋)
2. [專案架構與資料流總覽](#2-專案架構與資料流總覽)
3. [Part 1: 資料載入與原始檢視 (Data Loading & Inspection)](#3-part-1-資料載入與原始檢視)
4. [Part 2 & 3: 資料清洗決策與特徵表建立 (QC & Feature Table Construction)](#4-part-2--3-資料清洗決策與特徵表建立)
5. [Part 4: 基準模型比較與消融實驗 (Baseline Model Comparison)](#5-part-4-基準模型比較與消融實驗)
6. [Part 5: 輕量化模型實驗 (Lightweight Model Experiment - PCA)](#6-part-5-輕量化模型實驗)
7. [Part 6: 測試集預測與泛化能力分析 (Test Set Prediction & Generalization)](#7-part-6-測試集預測與泛化能力分析)
8. [核心決策與深入反思總結 (Key Decisions & Reflection)](#8-核心決策與深入反思總結)

---

## 1. 領域背景與核心名詞解釋

### 1.1 什麼是計算藥物反應預測 (Computational Drug Response Prediction)？
在精準醫療（Precision Medicine）與癌症藥物研發中，不同病患的癌細胞（或實驗室培育的癌細胞株）對同一種抗癌藥物的敏感度差異極大。傳統上透過濕實驗（Wet Lab）將數百種藥物逐一滴入數百種細胞株培養盤中測試，成本極其高昂且耗時。因此，利用機器學習建立「計算預測模型（In Silico Screening）」，根據**細胞的基因特徵**與**藥物的化學結構特徵**，直接預測其敏感度，是目前計算生物學（Computational Biology）的核心研究方向。

### 1.2 核心名詞詳解

*   **癌細胞株 (Cancer Cell Line, `cell_line_id`)**：
    實驗室長期體外培養、具有無限增殖能力的癌細胞群體（例如：`MCF7` 代表一種乳腺癌細胞、`A549` 代表肺癌細胞）。每一種細胞株擁有其獨特的基因表現型（Gene Expression）、基因突變（Mutations）與拷貝數變異。
*   **藥物化合物 (Drug Molecule, `drug_id`)**：
    具有特定化學結構的小分子化合物或標靶藥物（例如：`Erlotinib`、`Pictilisib`、`JQ1` 等）。
*   **反應值 (Response / $\log \text{IC}_{50}$)**：
    半抑制濃度（Half Maximal Inhibitory Concentration, $\text{IC}_{50}$）指抑制特定細胞生長達 50% 所需的藥物濃度。由於濃度跨越數個數量級，生醫界常取對數標度（$\log \text{IC}_{50}$）：
    *   **$\log \text{IC}_{50}$ 越小（負值越大）**：代表只需極低濃度的藥物即可殺死 50% 癌細胞 $\rightarrow$ **藥效越強、細胞對該藥越敏感（Sensitive）**。
    *   **$\log \text{IC}_{50}$ 越大（正值越大）**：代表需要極高濃度甚至無法抑制 $\rightarrow$ **藥效越弱、細胞對該藥具有抗藥性（Resistant）**。
*   **特徵嵌入向量 (Embedding Vector, 32 維)**：
    原始生物數據（如 DNA 序列、幾萬個基因的表現量）或分子結構（SMILES 化學式、分子圖結構）維度極高且非結構化，機器學習模型難以直接運算。生醫 AI 會透過預訓練模型（如圖神經網路 GNN 處理分子圖、Transformer 處理基因組學數據），將其壓縮映射到低維度密集向量空間（Dense Vector Space）。本資料集提供了：
    *   `cell_emb_0` ~ `cell_emb_31`：捕捉細胞株基因組特徵的 32 維數值向量。
    *   `drug_emb_0` ~ `drug_emb_31`：捕捉藥物分子化學特性的 32 維數值向量。
*   **特徵 (Features $X$) vs. 識別碼 (Identifiers)**：
    *   **特徵 ($X$, 64 維)**：模型拿來進行數學計算、找出與藥效關聯的數值輸入（32 維細胞向量 + 32 維藥物向量）。
    *   **識別碼 (IDs)**：如 `sample_id`, `cell_line_id`, `drug_id`。這些是人類索引或追蹤用的字串標籤，**不可**直接當作連續特徵餵進迴歸模型。
*   **均方誤差 (Mean Squared Error, MSE)**：
    連續數值迴歸的標準評估指標，計算「預測值與真實值差距的平方平均值」：
    $$\text{MSE} = \frac{1}{N} \sum_{i=1}^N (y_i - \hat{y}_i)^2$$
    若想還原至原本 $\log \text{IC}_{50}$ 的誤差單位，可取根號得到 $\text{RMSE} = \sqrt{\text{MSE}}$。

---

## 2. 專案架構與資料流總覽

```mermaid
flowchart TD
    subgraph Raw_Data [原始輸入檔案 (data/)]
        TrainRaw[train.csv<br>503 rows × 4 cols]
        TestRaw[test.csv<br>100 rows × 3 cols]
        CellRaw[global_cell_embeddings.csv<br>360 rows × 33 cols]
        DrugRaw[drug_embeddings.csv<br>208 rows × 33 cols]
    end

    subgraph QC_Cleaning [Part 3 品質控管與清洗]
        DupFix[1. 刪除 3 筆完全重複樣本 → 500 rows]
        StripFix[2. drug_id 移除尾端空白 .str.strip()]
        ImputeFix[3. cell_emb 欄位平均值填補 Mean Imputation]
        DropTestFix[4. test 排除 2 筆無 Embedding 細胞 → 98 rows]
    end

    subgraph Feature_Tables [Part 2 特徵表建立 (results/)]
        TrainProc[train_processed.csv<br>500 rows × 68 cols<br>(4 id/target + 64 features)]
        TestProc[test_processed.csv<br>98 rows × 67 cols<br>(3 id + 64 features)]
    end

    subgraph Modeling [Part 4 & 5 建模與評估]
        Split[80/20 Train/Val Split (400 / 100 筆)]
        ModelA[Model A: Cell Only (32 dims)]
        ModelB[Model B: Drug Only (32 dims)]
        ModelC[Model C: Cell + Drug (64 dims)]
        ModelPCA[Model C + PCA (20 dims)]
    end

    subgraph Inference [Part 6 測試集預測]
        TestPred[test_predictions.csv<br>98 筆預測值 & 泛化評估]
    end

    TrainRaw --> DupFix --> StripFix --> TrainProc
    CellRaw --> ImputeFix --> TrainProc
    DrugRaw --> TrainProc

    TestRaw --> StripFix --> DropTestFix --> TestProc
    ImputeFix --> TestProc
    DrugRaw --> TestProc

    TrainProc --> Split --> ModelA & ModelB & ModelC & ModelPCA
    ModelC --> TestPred
    TestProc --> TestPred
```

---

## 3. Part 1: 資料載入與原始檢視

### 3.1 原始檔案維度與欄位定義
| 檔案名稱 | 原始筆數 (Rows) | 欄位數 (Cols) | 主要欄位與說明 |
|---|---|---|---|
| `train.csv` | 503 | 4 | `sample_id` (樣本編號), `cell_line_id` (細胞名), `drug_id` (藥物名), `response` ($\log \text{IC}_{50}$ 目標值) |
| `test.csv` | 100 | 3 | `sample_id`, `cell_line_id`, `drug_id` (無 response，待預測) |
| `global_cell_embeddings.csv` | 360 | 33 | `cell_line_id`, `emb_0` ~ `emb_31` (32 維基因表現/突變特徵向量) |
| `drug_embeddings.csv` | 208 | 33 | `drug_id`, `emb_0` ~ `emb_31` (32 維化學分子結構特徵向量) |

### 3.2 程式碼核心亮點與解說
為了達成作業要求中「在修改資料前先全面了解其結構（Understanding before manipulating）」，撰寫了自動化檢視函式：
*   **`inspect_dataframe(df, name)`**：印出總形狀、全列重複數（Full-row duplicates）、缺失值分佈、型別。
*   **`check_join_key(df_left, df_right, key)`**：在執行任何 merge 前，利用集合交集（Set intersection）精確統計 left-only、right-only 與 matched 的比例，避免 merge 造成非預期的筆數暴增或無預警遺失。

---

## 4. Part 2 & 3: 資料清洗決策與特徵表建立

官方題目預先埋設了 4 個已知資料瑕疵（Data Issues）。以下為偵測證據、處理策略與生醫決策理由：

### 4.1 Issue 1: `train.csv` 中的重複資料 (Duplicate Rows)
*   **偵測證據**：
    檢查 `subset=['cell_line_id', 'drug_id', 'response']` 發現有 **3 組（共 6 筆）** 實驗紀錄的細胞、藥物與反應值完全一模一樣，僅 `sample_id` 不同（例如 `TRAIN_0083` 與 `TRAIN_0500` 同為 `SKMES1` + `Afatinib`，response 皆為 `2.378772`）。
*   **決策與處理**：
    使用 `train.drop_duplicates(subset=["cell_line_id", "drug_id", "response"], keep="first")` 刪除重複的 3 筆，保留原始 500 筆。
*   **理由**：
    在生物濕實驗中，如果兩次獨立測量結果完全精確至小數點後 6 位，極大概率為系統人為重複匯入或記錄複製；若保留這類重複樣本，在切分 Train/Val 時可能同時出現在訓練集與驗證集，造成**資料洩漏（Data Leakage）**，使驗證評估虛高。

### 4.2 Issue 2: `drug_id` 尾端帶有空白字符 (Trailing Whitespace)
*   **偵測證據**：
    在 `train.csv` 中發現如 `'Buparlisib '` 帶有空白尾端。
*   **決策與處理**：
    使用向量化字串處理：
    ```python
    train["drug_id"] = train["drug_id"].str.strip()
    test["drug_id"]  = test["drug_id"].str.strip()
    ```
*   **理由**：
    SQL 或 Pandas 的字串比對為嚴格匹配，`'Buparlisib '` 與 embedding 表中的 `'Buparlisib'` 會比對失敗，導致合併時 embedding 被填為 NaN。

### 4.3 Issue 3: `global_cell_embeddings.csv` 中的數值缺失 (NaNs in Embeddings)
*   **偵測證據**：
    `global_cell_embeddings.csv` 在 `emb_12` (2 處) 和 `emb_25` (1 處) 散落少數 NaN。
*   **決策與處理**：
    使用**欄位平均值填補（Column Mean Imputation）**：
    ```python
    for c in emb_cols:
        cell_emb[c] = cell_emb[c].fillna(cell_emb[c].mean())
    ```
*   **理由**：
    *   **為何不直接整列丟棄 (`dropna`)？** 細胞株為寶貴樣本，丟棄該列將導致所有包含該細胞株的訓練與測試資料皆無法使用。
    *   **為何用平均值而非補 0？** Embedding 空間為經過標準化或正則化的密集向量空間（值可能在 -2 到 +2 之間震盪），任意補 0 會破壞幾何分佈；補該特徵維度的全局平均值，能在不改變該維度一階矩（期望值）的前提下維持數值平穩。

### 4.4 Issue 4: `test.csv` 中未收錄的細胞株 (Unmatched IDs)
*   **偵測證據**：
    比對發現在 `test.csv` 裡，細胞株 `ABC1`（`TEST_0007`）與 `A427`（`TEST_0068`）在 360 株細胞庫中**完全不存在**。
*   **決策與處理**：
    在合併後排除此 2 筆無法對應的樣本，使最終 `test_processed.csv` 為 **98 筆**。
*   **理由**：
    這兩株細胞缺少全部 32 維特徵。在無任何生物基因標記的情況下，模型無法推測其細胞特異性；若採用盲目填補（如全補 0 或全局平均），模型只會退化為「只看藥物」的不可信預測。正式報告中應明確記錄此處置，並建議實驗室後續補充該兩株細胞的定序資料。

### 4.5 最終產出特徵表規格
*   **特徵命名規範**：將 embedding 欄位分別重命名為 `cell_emb_0` ~ `cell_emb_31` 及 `drug_emb_0` ~ `drug_emb_31`，避免合併時欄位衝突。
*   **`train_processed.csv`**：500 列 × 68 欄（`sample_id`, `cell_line_id`, `drug_id`, `response` + 64 維特徵）。
*   **`test_processed.csv`**：98 列 × 67 欄（`sample_id`, `cell_line_id`, `drug_id` + 64 維特徵）。

---

## 5. Part 4: 基準模型比較與消融實驗

### 5.1 消融實驗設計 (Ablation Study)
為了回答「究竟是細胞資訊重要、藥物資訊重要、還是兩者結合重要？」，設計三個特徵組合：
*   **Model A**：僅使用 Cell Embedding（32 維特徵）
*   **Model B**：僅使用 Drug Embedding（32 維特徵）
*   **Model C**：同時結合 Cell + Drug Embedding（64 維特徵）

### 5.2 訓練與切分決策
*   **80/20 Train/Val 切分**：固定隨機種子 `random_state=42`，400 筆作為訓練、100 筆作為驗證。
*   **為何不採用分層切分 (Stratified Split)？**
    本資料集 500 筆分散在 328 種細胞與 197 種藥物中，平均每種細胞僅出現 1.5 次，幾乎每筆組合都是唯一的孤本（Singleton），在統計學上不可能做到類別均勻分層，隨機抽樣是最客觀且不扭曲分佈的方法。

### 5.3 實測評估數據 (Validation MSE)

| 模型名稱 | 使用特徵 | Random Forest (100 棵樹) MSE | Linear Regression MSE |
|---|---|---|---|
| **Model A (Cell Only)** | 32 維細胞特徵 | **10.5935** | **10.2976** |
| **Model B (Drug Only)** | 32 維藥物特徵 | **3.2744** | **2.8734** |
| **Model C (Cell + Drug)** | 64 維全特徵 | **1.9483** | **1.8294** |

### 5.4 結果分析與核心洞察
1.  **為什麼 Model B 顯著勝過 Model A？（MSE 3.27 vs. 10.59）**
    *   **主效應（Main Effect）強弱**：在藥物反應實驗中，「藥物本身的分子毒性與一般殺傷力」決定了 response 的大範圍基底。有些強效化療藥物在幾乎所有細胞株上都很強，而溫和標靶藥則普遍偏高。
    *   **特徵代表性**：藥物的化學結構與物化性質較具規律性，模型能有效從 32 維分子向量學到一般毒性；反觀單靠細胞特徵時，模型完全不知道現在滴下去的是哪種藥，只能預測該細胞面對所有藥的平均耐受度，因而誤差極大。
2.  **為什麼 Model C 表現最佳？（MSE 降至 1.95 / 1.83）**
    *   藥物反應本質上是「**藥物標靶（Drug Target）與細胞基因突變路徑的交互作用（Interaction）**」。Model C 同時提供了配體（Ligand）與受體/背景（Receptor/Context）的資訊，使模型能捕捉特定的敏感性組合，因此大幅超越單一模態。
3.  **Random Forest vs. Linear Regression 的對比**：
    *   線性迴歸（LR）的 MSE（1.8294）略低於隨機森林（1.9483），且訓練時間快 50~100 倍（0.016 秒 vs. 0.942 秒）。
    *   這說明 64 維 Embedding 在建構時已經高度線性化，且在 400 筆的小樣本下，參數較少的線性模型不容易過擬合，展現出極強的基準效益。

---

## 6. Part 5: 輕量化模型實驗 (Lightweight Strategy - PCA)

### 6.1 實驗策略：主成分分析 (Principal Component Analysis, PCA)
*   **策略目標**：將 64 維特徵壓縮至 20 維（特徵量縮減 **68.75%**），探討在邊緣裝置（Edge Devices）或微型伺服器上部署時的效能與精度權衡（Trade-off）。
*   **防止資料洩漏 (Data Leakage)**：
    使用 `sklearn.pipeline.Pipeline` 將 PCA 與模型串接，**PCA 只能在訓練集（400 筆）上進行 `fit`**，驗證集與後續測試集僅做 `transform`，杜絕任何未來資訊滲漏。

### 6.2 輕量化實驗數據對比

| 模型架構 | 特徵維度 | 驗證集 MSE | 訓練時間 (秒) | 效益評估 |
|---|---|---|---|---|
| **RF - Model C (原版)** | 64 維 | **1.9483** | 0.942 s | 基準 |
| **RF - Model C + PCA** | 20 維 | **2.0047** | 0.600 s | **時間快 36.3%**，MSE 僅微幅上升 2.9% |
| **LR - Model C (原版)** | 64 維 | **1.8294** | 0.0085 s | 線性基準 |
| **LR - Model C + PCA** | 20 維 | **1.5097** | 0.0538 s | **MSE 反而下降 17.5%**（降維消除了多重共線性） |

### 6.3 輕量化效益討論
*   **維度壓縮比極高**：僅用 20 個正交主成分即保留了 64 維中絕大部分的資訊變異量。
*   **隨機森林效益**：樹模型在特徵數從 64 降到 20 時，每次切分評估的維度減少，運算時間從 0.94 秒縮短至 0.60 秒，非常適合資源受限環境。
*   **線性模型額外增益**：小樣本下 64 維特徵可能存在共線性（Multicollinearity），PCA 透過正交旋轉去除了冗餘噪音，反而幫助線性模型泛化得更好（MSE 1.83 $\rightarrow$ 1.51）。

---

## 7. Part 6: 測試集預測與泛化能力分析

在完成模型驗證後，真正的價值在於**對未標記的真實測試集（`test_processed.csv`，98 筆）進行推論與產出**。

### 7.1 產出檔案
*   儲存路徑：[`results/test_predictions.csv`](file:///d:/NTU/cmjm_entry/results/test_predictions.csv)
*   欄位：`sample_id`, `cell_line_id`, `drug_id`, `pred_response_rf`, `pred_response_lr`, `pred_response_pca_lr`, `response`（標準提交格式，以穩定度高的 RF 作為主要 response）。

### 7.2 泛化檢驗三大核心發現

#### ① 模型共識極高（Pearson Correlation $r = 0.9602$）
*   隨機森林（非線性多決策樹）與線性迴歸（高維超平面）在未知的 98 筆測試集上，兩者預測值的相關係數高達 **0.9602**。
*   **意義**：兩套架構截然不同的演算法得出高度一致的預測曲線，代表模型捕捉到了客觀存在的生物化學訊號，而非特定演算法的過擬合幻覺。

#### ② 預測分佈符合真實物理邊界 (Realistic & Bounded)
| 統計指標 | Train 實際值 (500 筆) | Test 預測 (RF, 98 筆) | Test 預測 (LR, 98 筆) |
|---|---|---|---|
| **平均值 (Mean)** | 2.650 | 2.284 | 2.340 |
| **標準差 (Std)** | 3.104 | 2.700 | 3.052 |
| **數值區間 [Min, Max]** | [-7.141, 10.822] | [-4.804, 9.309] | [-6.047, 8.710] |

*   測試集的預測平均值與標準差緊密貼合真實訓練集分佈，沒有產生任何向外擴散的荒謬極端值（如 $>20$ 或 $<-15$）。

#### ③ 外推泛化檢驗：訓練集見過 (Seen) vs. 未見過 (Unseen)
*   測試集 98 筆中，有 **36 筆樣本的細胞株是訓練集從未見過的（Unseen Cell Lines）**。
*   **統計對比**：
    *   **Seen Cells (62 筆)**：RF 預測平均值 $2.322 \pm 2.794$
    *   **Unseen Cells (36 筆)**：RF 預測平均值 $2.217 \pm 2.569$
*   **意義**：對於完全未見過的細胞株，模型依然能依託 32 維特徵空間中的向量距離推導出合理的藥物敏感度，展現了良好的跨樣本外推泛化能力。

---

## 8. 核心決策與深入反思總結

### 8.1 本專案所做的重要工程決策
1.  **資料清洗優先於特徵工程**：嚴格在 Merge 前完成去除重複列、清理字串空白與缺失值填補，確保 Merge 過程純淨無資料膨脹。
2.  **特徵命名防護**：顯式為特徵加上 `cell_emb_` 與 `drug_emb_` 前綴，提高程式碼可讀性並防止特徵混淆。
3.  **模組化與對照設計**：同時實作 Random Forest 與 Linear Regression，並納入消融實驗（A/B/C）與 PCA 降維，提供全方位的橫向比較維度。
4.  **Pipeline 封裝保護**：輕量化實驗全程使用 `Pipeline`，嚴守測試集與驗證集不可見原則，落實資料科學規範。

### 8.2 資料集特徵與反思 (Critical Reflections)
*   **資料稀疏性（Data Sparsity）**：
    500 筆訓練資料涵蓋 328 種細胞與 197 種藥物，平均每一種藥物或細胞的實驗次數只有 1.5 ~ 2.5 次。這反映了真實生物醫學數據標註成本昂貴的典型現象。在此種稀疏度下，試圖尋找「哪種特定細胞最脆弱」通常不具備統計顯著性，模型的重點更著重於學習全域向量特徵的映射關係。
*   **未來若有更多時間的優化方向**：
    1.  **K-Fold 交叉驗證（5-Fold CV）**：目前的單次 80/20 切分可能受到隨機種子波動影響，採用 5-Fold Cross Validation 能給出更具統計可信度的 MSE 與信心區間。
    2.  **嚴格的冷啟動評估（Cold-Start Split）**：將驗證集設計為「完全不包含訓練集細胞」的 GroupKFold，深入評估純外推性能。
    3.  **特徵交互項（Interaction Terms）**：目前的 Model C 是將 32+32 維直接拼接（Concatenation），未來可嘗試雙線性層（Bilinear Pooling）或神經網絡交叉乘積，顯式強化分子與標靶間的交互資訊。
