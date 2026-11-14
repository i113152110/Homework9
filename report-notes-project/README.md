# 報表拆解室（Report Notes）

一個使用原生 HTML、CSS、JavaScript 建立的繁體中文股票財報入門筆記網站。

## 專案特色

- 首頁含三張報表的學習流程、可搜尋文章卡片、分類篩選。
- 四篇可直接閱讀的示範頁面，共用網頁樣式和一致的導覽。
- `AGENTS.md` 明確規範 AI 如何新增文章、維護 metadata、命名、測試和避免改壞現有內容。
- `pages/_template.html` 能讓下一篇文章保有相同版型；新增 `data/articles.js` 一筆資料後，首頁會自動出現卡片。
- 無外部套件、無後端、無 API Key，適合直接使用 GitHub Pages 公開。

## 本機預覽

可直接開啟 `index.html`；若瀏覽器對本機 JavaScript 有限制，可從此專案資料夾執行：

```bash
python -m http.server 8000
```

接著開啟 `http://localhost:8000/`。

## GitHub Pages 公開步驟（由使用者自行執行）

1. 建立新的 GitHub repository，例如 `report-notes`。
2. 將**本資料夾內的所有檔案與子資料夾**上傳到 repository 根目錄（要看到 `index.html` 和 `AGENTS.md` 在最外層）。**不要只上傳 ZIP。**
3. 開啟 repository 的 **Settings → Pages**。
4. 在 **Build and deployment** 選 **Deploy from a branch**，branch 選 `main`，folder 選 `/(root)` 並儲存。
5. 發布完成後，網站網址通常是 `https://你的帳號.github.io/report-notes/`，實際網址以 GitHub Pages 畫面為準。

## 如何新增文章（AI 規則已定義）

1. 先閱讀 `AGENTS.md`。
2. 複製 `pages/_template.html` 並改成 `pages/financial-ratios.html`。
3. 撰寫文章，維持既有文章格式，段落 `id` 對應側欄目錄。
4. 在 `data/articles.js` 新增一筆 metadata，`id` 設 `financial-ratios`，`path` 設 `pages/financial-ratios.html`。
5. 執行 `python scripts/validate.py`，確認首頁新增卡片、搜尋、文章連結正確。

完整要求、範例提示詞、檔案位置與修改邊界都記錄在 [`AGENTS.md`](AGENTS.md)。

## 驗證

```bash
python scripts/validate.py
```

只需 Python 標準函式庫。檢查 HTML 相對連結、anchor、h1、標題、metadata、類別篩選、檔名和內容一致性。

## 教學資料說明

「晨光製造」與數值為虛構學習範例，非上市公司的真實數據，網站內容不構成投資建議。
