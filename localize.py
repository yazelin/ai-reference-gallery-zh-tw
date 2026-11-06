"""抓四個原站、翻成繁中，輸出到指定目錄：python3 localize.py 輸出目錄 [--cache 目錄]
  輸出目錄/<庫>/ 是各庫的繁中頁面與給 AI 用的資料檔，首頁 hub/ 另外複製。
  對照表 zh-tw.json 沒有的日文字串保持原樣，列在 missing.txt（前面標庫名）。
  --cache：原站檔案存在這裡，已存在就不重抓（本機反覆測試用）。"""
import json, os, re, sys, urllib.request

REPO = 'https://github.com/yazelin/ai-reference-gallery-zh-tw'
UA = 'Mozilla/5.0 (ai-reference-gallery-zh-tw; +' + REPO + ')'
JA = re.compile(r'[぀-ヿ㐀-鿿＀-￯　-〿]+'
                r'(?:[ A-Za-z0-9・ー\-/:()（）]*[぀-ヿ㐀-鿿＀-￯　-〿]+)*')

# 內嵌資料的三個站：index.html 裡有一段 [{"id"...}] 陣列
POSE_KEYS = {'id': 'id', '系統': 'series', 'ポーズ番号': 'pose_no', '分類': 'category', 'ポーズ名': 'name',
             'アングル': 'angle', 'サムネ': 'thumb', '原寸': 'image'}
SITES = {
    'pose': dict(origin='https://ai-pose-gallery.pages.dev/', author='ギア', title='姿勢集 POSE-DB-01',
                 tr=('系統', '分類', 'ポーズ名', 'アングル'), urls=('サムネ', '原寸'),
                 idents='系統|ポーズ番号|ポーズ名|分類|アングル|サムネ|原寸|番号|名',
                 data='poses.json', keys=POSE_KEYS),
    'depth': dict(origin='https://ai-pose-depth-gallery.pages.dev/', author='ギア', title='depth 姿勢集 POSE-DB-02',
                  tr=('系統', '分類', 'ポーズ名', 'アングル'), urls=('サムネ', '原寸'),
                  idents='系統|ポーズ番号|ポーズ名|分類|アングル|サムネ|原寸|番号|名',
                  data='poses.json', keys=POSE_KEYS),
    'costume': dict(origin='https://ai-costume-gallery.pages.dev/', author='ギア', title='服裝集 COSTUME-DB-01',
                    tr=('カテゴリ',), urls=('サムネ', '画像', '原寸'),
                    idents='カテゴリ|キーワード|サムネ|画像|原寸',
                    data='costumes.json',
                    keys={'id': 'id', 'カテゴリ': 'category', 'キーワード': 'keywords', 'サムネ': 'thumb',
                          '画像': 'preview', '原寸': 'image'}),
}
# 人臉站是多檔結構，資料在 data/images.js
PORTRAIT = dict(origin='https://ai-portrait-gallery.pages.dev/', author='@agi_aibusi', title='AI 模特兒臉部資料庫',
                files=('index.html', 'assets/app.js', 'assets/style.css', 'data/images.js', 'data/ranking.js'),
                data='faces.json')


# 英文字開頭的句子切不進對照表（日文片段從英文字後面才開始），整句先換
WHOLE = {'LINEオープンチャットに参加する（新しいタブ）': '加入 LINE OpenChat 群組（另開分頁）',
         'LINEオープンチャットに参加する': '加入 LINE OpenChat 群組',
         'LINEオープンチャット（活用事例）': 'LINE OpenChat 群組（運用實例）'}


def note(origin, author):
    return ('<div style="background:#1a1e24;border-bottom:1px solid #343a44;color:#a3abb8;font-size:13px;'
            'padding:8px 16px;text-align:center;font-family:sans-serif">繁體中文翻譯版。原站：<a style="color:#8fb4ff" href="'
            + origin + '">' + origin + '</a>（作者 ' + author + '）。圖片一律從原站載入。'
            '<a style="color:#8fb4ff" href="../">其他圖庫</a>・<a style="color:#8fb4ff" href="' + REPO + '">說明</a></div>')


def fetch(url, cache):
    path = cache and os.path.join(cache, re.sub(r'[^A-Za-z0-9.]+', '_', url))
    if path and os.path.exists(path):
        return open(path, encoding='utf-8').read()
    s = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60).read().decode('utf-8')
    if path:
        os.makedirs(cache, exist_ok=True)
        open(path, 'w', encoding='utf-8').write(s)
    return s


class Tr:
    def __init__(self, table):
        self.table, self.missing = table, set()

    def __call__(self, x):
        if x in self.table:
            return self.table[x]
        self.missing.add(x)
        return x

    def text(self, s, idents=None):
        """把一段文字（HTML 或 JS）裡的日文換掉；idents 是 JS 裡當欄位名用、不能翻的字"""
        kept = []
        for a, b in WHOLE.items():
            s = s.replace(a, f'\1{len(kept)}\1')
            kept.append(b)
        if idents:
            s = re.sub(r'(?<=[.{,])(?:' + idents + r')(?=[^぀-鿿])',
                       lambda m: kept.append(m[0]) or f'\1{len(kept) - 1}\1', s)
        s = JA.sub(lambda m: self(m[0]), s)
        return re.sub('\x01(\\d+)\x01', lambda m: kept[int(m[1])], s)


def finish_html(s, origin, author):
    s = s.replace('<html lang="ja">', '<html lang="zh-Hant">')
    s = s.replace("img-src 'self' data:", "img-src 'self' data: " + origin.rstrip('/'))
    # 拿掉 Cloudflare Web Analytics，避免把繁中版的流量算進原作者的統計
    s = re.sub(r"<script defer src='https://static\.cloudflareinsights\.com.*?</script>", '', s, flags=re.S)
    s = s.replace("https://static.cloudflareinsights.com", '').replace(" connect-src https://cloudflareinsights.com", " connect-src 'none'")
    return re.sub(r'(<body[^>]*>)', lambda m: m[1] + note(origin, author), s, count=1)


def embedded(site, tr, cache):
    c = SITES[site]
    s = fetch(c['origin'], cache)
    i = s.index('[{"id"')
    j = s.index('}]', i) + 2
    data = json.loads(s[i:j])
    for d in data:
        for k in c['tr']:
            if d.get(k):
                d[k] = tr(d[k])
        for k in c['urls']:  # 條款禁止轉載圖片，只連回原站
            d[k] = c['origin'] + d[k]
    rest = tr.text(s[:i] + '\0' + s[j:], c['idents'])
    out = finish_html(rest.replace('\0', json.dumps(data, ensure_ascii=False)), c['origin'], c['author'])
    files = {'index.html': out}
    if site == 'costume':  # 站上搜尋用的日文→英文關鍵字對照，翻成中文後另存一份給 skill 用中文搜
        k = s.index('"ブラック": "black"')
        syn = json.loads(s[s.rindex('{', 0, k):s.index('}', k) + 1])
        files['synonyms.json'] = json.dumps({tr(a): b for a, b in syn.items()}, ensure_ascii=False, indent=0)
    return files, [{c['keys'][k]: v for k, v in d.items()} for d in data]


def portrait(tr, cache):
    c = PORTRAIT
    src = {f: fetch(c['origin'] + f, cache) for f in c['files']}
    s = src['data/images.js']
    data = json.loads(s[s.index('['):s.rindex(']') + 1])
    for d in data:
        for k in ('hair', 'style'):
            if d.get(k):
                d[k] = tr(d[k])
        for k in ('full', 'thumb'):
            d[k] = c['origin'] + d[k]
    out = {'data/images.js': 'window.GALLERY_IMAGES = ' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n'}
    for f in ('data/ranking.js', 'assets/style.css', 'index.html', 'assets/app.js'):
        out[f] = tr.text(src[f])
    # 使用次數統計（/api/hit）與即時排行（/api/ranking）是相對路徑，在鏡像上會打到 github.io 而 404，
    # 到不了原站。統計整個關掉，排行直接用打包時的 ranking.js
    app = out['assets/app.js']
    app = app.replace('function hit(ev, it) {', 'function hit(ev, it) { return;').replace('window.fetch) {\n    var rankTimer', 'false) {\n    var rankTimer')
    assert app.count('function hit(ev, it) { return;') == 1 and app.count('false) {\n    var rankTimer') == 1, '人臉站 app.js 結構變了'
    out['assets/app.js'] = app
    out['index.html'] = finish_html(out['index.html'], c['origin'], c['author'])
    faces = [{'id': d['id'], 'section': d['section'], 'hair': d['hair'], 'style': d['style'], 'width': d['w'],
              'height': d['h'], 'thumb': d['thumb'], 'image': d['full']} for d in data]
    return out, faces


def main(outdir, cache=None):
    table = json.load(open('zh-tw.json', encoding='utf-8'))
    missing = []
    for name in list(SITES) + ['portrait']:
        tr = Tr(table)
        files, data = portrait(tr, cache) if name == 'portrait' else embedded(name, tr, cache)
        conf = PORTRAIT if name == 'portrait' else SITES[name]
        for f, body in files.items():
            p = os.path.join(outdir, name, f)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, 'w', encoding='utf-8').write(body)
        json.dump(data, open(os.path.join(outdir, name, conf['data']), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        missing += [f'{name}\t{m}' for m in sorted(tr.missing)]
        print(f'{name}: {len(data)} 筆，未翻 {len(tr.missing)} 條')
    open('missing.txt', 'w', encoding='utf-8').write(''.join(m + '\n' for m in missing))


if __name__ == '__main__':
    a = sys.argv[1:]
    cache = None
    if '--cache' in a:
        k = a.index('--cache')
        cache = a[k + 1]
        del a[k:k + 2]
    if len(a) != 1:
        sys.exit(__doc__)
    main(a[0], cache)
