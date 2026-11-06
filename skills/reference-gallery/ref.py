"""查 AI 繪圖參考圖（ai-reference-gallery 繁中版，四個圖庫）：
  python3 ref.py search <庫> 關鍵字 [關鍵字...] [選項]
      庫：pose（姿勢線稿）、depth（姿勢深度圖）、costume（服裝）、portrait（臉部）
      pose／depth 選項：--angle 正面|從上方|從下方|側面|斜側  --line 系列
      costume 選項：--cat 春|夏|秋|冬|內衣|派對|泳裝|性感（關鍵字可用中文或英文）
      portrait 選項：--section face|styling  --hair 短髮|及肩|中長髮|長髮|未分類
      --limit N：最多列幾筆（預設 30，0 表示全部）
  python3 ref.py get <庫> <id> [<id>...] [-o 目錄]
      把原尺寸 PNG 下載到本機（預設 ./refs/），給生圖工具當參考圖
原站禁止批次下載（含工具自動抓取）：get 只拿這次要用的那幾張，不要整批抓。
圖片由原站提供，只供自己的作品參考，不要再散布（不要 commit 進公開 repo）。"""
import json, os, sys, urllib.request

BASE = os.environ.get('REF_GALLERY_BASE', 'https://yazelin.github.io/ai-reference-gallery-zh-tw/')
FILES = {'pose': 'pose/poses.json', 'depth': 'depth/poses.json', 'costume': 'costume/costumes.json',
         'portrait': 'portrait/faces.json'}
MAX_GET = 10  # 一次最多下載幾張，避免變成批次下載

# Cloudflare 會擋 Python 預設的 User-Agent
UA = 'Mozilla/5.0 (reference-gallery skill; +https://github.com/yazelin/ai-reference-gallery-zh-tw)'


def load(path):
    req = urllib.request.Request(BASE + path, headers={'User-Agent': UA})
    return json.load(urllib.request.urlopen(req, timeout=30))


def opt(args, name):
    if name in args:
        i = args.index(name)
        v = args[i + 1]
        del args[i:i + 2]
        return v


def lib_of(args):
    if not args or args[0] not in FILES:
        sys.exit('第一個參數要是庫名：' + '、'.join(FILES))
    return args.pop(0)


def search(args):
    lib = lib_of(args)
    limit = int(opt(args, '--limit') or 30)
    f = {k: opt(args, '--' + k) for k in ('angle', 'line', 'cat', 'section', 'hair')}
    words = [w.lower() for w in args]
    if lib == 'costume':  # 中文單字換成服裝資料裡的英文關鍵字
        syn = load('costume/synonyms.json')
        words = [syn.get(w, w) for w in words]
    n = 0
    for d in load(FILES[lib]):
        if lib in ('pose', 'depth'):
            hay = ' '.join([d['id'], d['series'], d['category'], d['name'], d['pose_no']])
            ok = (not f['angle'] or d['angle'] == f['angle']) and (not f['line'] or f['line'] in d['series'])
            line = f"{d['id']}  {d['series']}｜{d['category']}｜{d['name']}｜{d['angle']}"
        elif lib == 'costume':
            hay = ' '.join([d['id'], d['category'], d['keywords']])
            ok = not f['cat'] or d['category'] == f['cat']
            line = f"{d['id']}  {d['category']}｜{d['keywords']}"
        else:
            hay = ' '.join([d['id'], d['section'], d['hair'], d['style']])
            ok = (not f['section'] or d['section'] == f['section']) and (not f['hair'] or d['hair'] == f['hair'])
            line = f"{d['id']}  {d['section']}｜{d['hair']}｜{d['style'] or '—'}"
        hay = hay.lower()
        # 服裝關鍵字是英文單字，整字比對（red 不要配到 shred）；其他庫是中文，用子字串
        if ok and all((w in hay.split()) if lib == 'costume' else (w in hay) for w in words):
            print(f"{line}  縮圖 {d['thumb']}")
            n += 1
            if limit and n >= limit:
                print(f'（只列前 {limit} 筆，加 --limit 0 看全部）')
                break
    if not n:
        print('沒有符合的結果，換個關鍵字或拿掉選項試試')


def get(args):
    lib = lib_of(args)
    out = opt(args, '-o') or 'refs'
    if len(args) > MAX_GET:
        sys.exit(f'一次最多 {MAX_GET} 張。原站禁止批次下載，只拿這次要用的')
    by = {d['id']: d for d in load(FILES[lib])}
    os.makedirs(out, exist_ok=True)
    for i in args:
        if i not in by:
            sys.exit(f'{lib} 找不到 id：{i}（先用 search 查）')
        path = os.path.join(out, f'{lib}_{i}.png')
        req = urllib.request.Request(by[i]['image'], headers={'User-Agent': UA})
        open(path, 'wb').write(urllib.request.urlopen(req, timeout=60).read())
        print(path)


if __name__ == '__main__':
    cmd, rest = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ('', [])
    {'search': search, 'get': get}.get(cmd, lambda _: print(__doc__))(rest)
