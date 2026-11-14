def homeVideoContent(C):
        M = {B: [], E: 0, F: 0}
        try:
            resp = C.get(C.home_url, headers=C.headers, timeout=10)
            print(f"=== [YOKAR Debug] Home Status: {resp.status_code}, Length: {len(resp.text) if resp.text else 0} ===")
            if resp.status_code == 200 and resp.text:
                # 印出前 200 字元看看是不是被擋或拿到空白頁
                print(f"=== [YOKAR Debug] Home Snippet: {resp.text[:200]} ===")
                S_doc = H(resp.text.encode())
                items = S_doc('a') # 改用最寬鬆的 a 標籤
                seen = set()
                for item in items.items():
                    U = item.attr(I)
                    if not U or U in seen or U in ['/', '#']:
                        continue
                    V = item.attr('title') or item('img').attr('alt') or item.text().strip()
                    W = item('img').attr(P) or item('img').attr('src') or ''
                    if U and V and len(V) > 1:
                        seen.add(U)
                        M[B].append({J: U, K: V, R: W, L: 'YouTube'})
        except Exception as e:
            print(f"homeVideoContent error: {e}")
        return M

    def categoryContent(D, cid, page, filter, ext):
        M = {B: [], E: 0, F: 0}
        url = D.home_url + f"/{cid}?page={page}"
        try:
            resp = C.get(url, headers=D.headers, timeout=10)
            print(f"=== [YOKAR Debug] Category URL: {url} ===")
            print(f"=== [YOKAR Debug] Category Status: {resp.status_code}, Length: {len(resp.text) if resp.text else 0} ===")
            if resp.status_code == 200 and resp.text:
                S_doc = H(resp.text.encode())
                items = S_doc('a')
                seen = set()
                for item in items.items():
                    U = item.attr(I)
                    if not U or U in seen or U in ['/', '#']:
                        continue
                    V = item.attr('title') or item('img').attr('alt') or item.text().strip()
                    W = item('img').attr(P) or item('img').attr('src') or ''
                    if U and V and len(V) > 1:
                        seen.add(U)
                        M[B].append({J: U, K: V, R: W, L: 'YouTube'})
        except Exception as e:
            print(f"categoryContent error: {e}")
        return M
