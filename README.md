# ai-reference-gallery-zh-tw

AI 繪圖用的四個日文參考圖庫，翻成繁體中文、放在同一個入口，附上讓 AI 直接查詢、取用的 skill。

- 繁中版網站：<https://yazelin.github.io/ai-reference-gallery-zh-tw/>

| 圖庫 | 原站 | 作者 | 內容 | 繁中版 |
|---|---|---|---|---|
| 姿勢集 POSE-DB-01 | <https://ai-pose-gallery.pages.dev/> | ギア（[X @giaaibusi](https://x.com/giaaibusi)） | 無臉灰色人台線稿 1,439 張，288 個姿勢 × 5 個角度 | [`/pose/`](https://yazelin.github.io/ai-reference-gallery-zh-tw/pose/) |
| depth 姿勢集 POSE-DB-02 | <https://ai-pose-depth-gallery.pages.dev/> | ギア | 同一批姿勢的深度圖 1,439 張 | [`/depth/`](https://yazelin.github.io/ai-reference-gallery-zh-tw/depth/) |
| 服裝集 COSTUME-DB-01 | <https://ai-costume-gallery.pages.dev/> | ギア | 無人物的服裝圖 1,407 套 | [`/costume/`](https://yazelin.github.io/ai-reference-gallery-zh-tw/costume/) |
| AI 模特兒臉部資料庫 | <https://ai-portrait-gallery.pages.dev/> | あぎ（[X @agi_aibusi](https://x.com/agi_aibusi)） | AI 虛構人物 1,499 張（臉部 893、造型 606），CC0 1.0 | [`/portrait/`](https://yazelin.github.io/ai-reference-gallery-zh-tw/portrait/) |

這個 repo 原本叫 `ai-pose-gallery-zh-tw`，只有姿勢集，2026-11-07 擴充成四個圖庫並改名。

## 這個版本多了什麼

原站是給人瀏覽的網頁。這個版本保留同樣的網頁並翻成繁中，另外提供 AI 能直接使用的入口：

| 入口 | 內容 |
|---|---|
| [`skills/reference-gallery/`](skills/reference-gallery/) | AI agent 的 skill。`SKILL.md` 寫明何時使用、怎麼搜尋、怎麼當參考圖、使用規範；`ref.py` 負責搜尋與下載，只用 Python 標準函式庫 |
| 各庫的資料檔 | [`pose/poses.json`](https://yazelin.github.io/ai-reference-gallery-zh-tw/pose/poses.json)、[`depth/poses.json`](https://yazelin.github.io/ai-reference-gallery-zh-tw/depth/poses.json)、[`costume/costumes.json`](https://yazelin.github.io/ai-reference-gallery-zh-tw/costume/costumes.json)、[`portrait/faces.json`](https://yazelin.github.io/ai-reference-gallery-zh-tw/portrait/faces.json)：每張圖的 id、繁中分類與名稱、縮圖與原尺寸圖網址 |
| [`llms.txt`](https://yazelin.github.io/ai-reference-gallery-zh-tw/llms.txt) | 給 AI 讀的網站簡介，指向上面兩項 |

### 給 AI 用

把 skill 裝進 agent 的 skill 目錄（Claude Code 為例）：

```bash
git clone https://github.com/yazelin/ai-reference-gallery-zh-tw.git
ln -s "$PWD/ai-reference-gallery-zh-tw/skills/reference-gallery" ~/.claude/skills/reference-gallery
```

之前裝過 `pose-reference` 的話，先移除舊的連結（`rm ~/.claude/skills/pose-reference`），`git pull` 後改連到新路徑。

其他 agent 直接讀 `skills/reference-gallery/SKILL.md` 照著做即可。不想安裝的話，對 AI 說「讀 https://yazelin.github.io/ai-reference-gallery-zh-tw/llms.txt，幫我找一個跪坐回頭的姿勢、一套冬天的大衣、一張短髮的臉」也可以。

```bash
python3 skills/reference-gallery/ref.py search pose 跪立 後仰 --angle 側面
python3 skills/reference-gallery/ref.py search costume 白 大衣 --cat 冬
python3 skills/reference-gallery/ref.py search portrait 狼尾 --section face
python3 skills/reference-gallery/ref.py get pose full_sexy_P031_side -o refs
```

`get` 一次最多 10 張，因為原站禁止批次下載。

## 和原站相比改了什麼

GitHub Actions 每天台灣時間 03:37 抓一次四個原站的頁面與資料（HTML、JS、CSS，不抓圖片），經 `localize.py` 處理後部署到 GitHub Pages：

1. 介面文字、分類、姿勢名稱、髮型名稱從日文翻成繁體中文，對照表在 `zh-tw.json`，四站共用。服裝站的搜尋對照也一起翻，所以可以用中文搜尋服裝。
2. 圖片沒有複製進來。縮圖、原尺寸圖、下載連結都指回原站，CSP 的 `img-src` 加上原站網域讓圖片載得到。原站注意事項禁止圖片本身的再散布與轉載，所以這個 repo 和 Pages 都不放任何圖片。
3. 移除原站的流量統計：姿勢、depth、服裝三站的 Cloudflare Web Analytics beacon，以及臉部站送到 `/api/hit` 的下載次數統計，避免把繁中版的流量算進原作者的統計。臉部站的即時排行也不抓，改用原站打包時的 `ranking.js`。
4. 每頁頂端加一行說明，註明原站與作者，並連回入口頁與這個 repo。
5. 多產出各庫的 JSON 資料檔和 `llms.txt`（見上一節）。
6. 入口頁 `hub/index.html` 是自己寫的，不來自原站。

`html lang` 改成 `zh-Hant`。除此之外，版面、程式與功能都和原站相同。

### 原站新增內容時

對照表沒有的日文字串會保持日文顯示，並列在當次 Actions 執行的 Summary（前面標庫名）。補進 `zh-tw.json` 後 push，就會重新部署。

```bash
python3 localize.py out --cache cache   # 未翻譯的字串寫在 missing.txt；--cache 讓重跑時不必重抓原站
```

英文字開頭的句子（例如「LINEオープンチャットに参加する」）切不進對照表，放在 `localize.py` 的 `WHOLE` 整句替換。 <!-- speak-tw-ok：日文原句 -->

## 使用規範（摘譯自原站注意事項）

- 四個圖庫的圖片都可免費使用，作品製作中的商業使用、編輯與參考都可以，不必標註出處。
- 禁止圖片本身（含原尺寸與加工後）的再散布、轉載與轉售。臉部庫是 CC0 1.0，但原作者同樣請大家不要再散布圖片本身。
- 姿勢、depth、服裝三庫另外禁止批次下載（含用工具自動抓取），生成時一張一張拿來參考可以。
- 不得用於表現或冒充真實人物、未成年人，也不得用於違反公序良俗的用途。
- 版權歸各原作者所有，詳細條款以原站為準。這個 repo 自己的程式（`localize.py`、`ref.py`、入口頁）可自由使用。
