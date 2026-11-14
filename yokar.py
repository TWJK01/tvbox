#!/usr/bin/python3
# -*- coding: utf-8 -*-

R = 'vod_pic'
Q = 'span.public-list-prb.hide.ft2'
P = 'data-src'
O = print
L = 'vod_remarks'
K = 'vod_name'
J = 'vod_id'
I = 'href'
G = 'a'
F = 'jx'
E = 'parse'
D = 'type_name'
B = 'list'
A = ''

import hashlib as Z, json, re, sys, time as M, requests as C
from urllib import parse as N
from pyquery import PyQuery as H
sys.path.append('..')
from base.spider import Spider as S

class Spider(S):
    def __init__(A):
        super().__init__()
        A.debug = False
        A.name = 'YOKAR影视'
        A.error_play_url = 'https://sf1-cdn-tos.huoshanstatic.com/obj/media-fe/xgplayer_doc_video/mp4/xgplayer-demo-720p.mp4'
        A.home_url = 'https://yokar.net'
        A.headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36'}

    def getName(A):
        return A.name

    def init(A, extend='{}'):
        try:
            A.extend = json.loads(extend) if isinstance(extend, str) else extend
        except:
            A.extend = {}

    def getDependence(A):
        return []

    def isVideoFormat(A, url):
        if url and ('youtube.com' in url or 'youtu.be' in url):
            return True
        return any(x in url.lower() for x in ['.m3u8', '.mp4']) if url else False

    def manualVideoCheck(A):
        return False

    def liveContent(B, url):
        return A

    def homeContent(G, filter):
        # 保持零網路請求初始化，保證 100% 成功在 App 中顯示站點
        A_key = 'type_id'
        C_dict = {
            'class': [
                {A_key: 'movie', D: '电影'},
                {A_key: 'anime', D: '动漫'},
                {A_key: 'drama', D: '戏剧'}
            ],
            'filters': {},
            B: [],
            E: 0,
            F: 0
        }
        return C_dict

    def homeVideoContent(C):
        M = {B: [], E: 0, F: 0}
        try:
            resp = C.get(C.home_url, headers=C.headers, timeout=10)
            if resp.status_code == 200:
                S_doc = H(resp.text.encode())
                items = S_doc('a:has(img)')
                seen = set()
                for item in items.items():
                    U = item.attr(I)
                    if not U or U in seen or U in ['/', '#']:
                        continue
                    V = item.attr('title') or item('img').attr('alt') or ''
                    W = item('img').attr(P) or item('img').attr('data-original') or item('img').attr('src') or ''
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
            if resp.status_code == 200:
                S_doc = H(resp.text.encode())
                items = S_doc('a:has(img)')
                seen = set()
                for item in items.items():
                    U = item.attr(I)
                    if not U or U in seen or U in ['/', '#', '/movie', '/anime', '/drama']:
                        continue
                    V = item.attr('title') or item('img').attr('alt') or ''
                    if not V or len(V) < 2:
                        V = item('h3, h4, .title, .name').text().strip()
                    W = item('img').attr(P) or item('img').attr('data-original') or item('img').attr('src') or ''
                    if U and V and len(V) > 1:
                        seen.add(U)
                        M[B].append({J: U, K: V, R: W, L: 'YouTube'})
        except Exception as e:
            print(f"categoryContent error: {e}")
        return M

    def detailContent(N, did):
        U = '$$$'
        O = {B: [], E: 0, F: 0}
        P = did[0]
        M_url = N.home_url + (P if P.startswith('http') else f"/{P.lstrip('/')}")
        
        try:
            V = C.get(M_url, headers=N.headers, timeout=10)
            Q_doc = H(V.text.encode())
            title = Q_doc('h1').text() or Q_doc('meta[property="og:title"]').attr('content') or "YouTube影視"
            pic = Q_doc('meta[property="og:image"]').attr('content') or ''
            desc = Q_doc('meta[property="og:description"]').attr('content') or ''
            
            X = Q_doc('a[href*="/play/"], a[href*="/watch/"], a[href*="youtube"], a[href*="youtu.be"], a:has(img)')
            S_list = []
            seen_ep = set()
            for T in X.items():
                link = T.attr(I)
                if not link or link in seen_ep:
                    continue
                if '/play/' in link or '/watch/' in link or 'youtube' in link:
                    seen_ep.add(link)
                    Z = T.text().strip() or f"正片{len(S_list)+1}"
                    S_list.append(f"{Z}${link}")
            
            play_url = '#'.join(S_list) if S_list else f"播放正片${P}"
            
            O[B].append({
                D: A, J: P, K: title, L: A, 
                'vod_year': A, 'vod_area': A, 'vod_actor': A, 'vod_director': A, 
                'vod_content': desc, 'vod_play_from': 'YOKAR-YT', 'vod_play_url': play_url
            })
        except Exception as e:
            O[B].append({D: A, J: P, K: '解析錯誤', L: A, 'vod_play_from': 'error', 'vod_play_url': '播放$#'})
            
        return O

    def searchContent(D, key, quick, page='1'):
        G_dict = {B: [], E: 0, F: 0}
        url = D.home_url + f"/search?wd={key}&page={page}"
        try:
            resp = C.get(url, headers=D.headers, timeout=10)
            if resp.status_code == 200:
                S_doc = H(resp.text.encode())
                items = S_doc('a:has(img)')
                seen = set()
                for item in items.items():
                    U = item.attr(I)
                    if not U or U in seen:
                        continue
                    V = item.attr('title') or item('img').attr('alt') or ''
                    W = item('img').attr(P) or item('img').attr('src') or ''
                    if U and V and len(V) > 1:
                        seen.add(U)
                        G_dict[B].append({J: U, K: V, R: W, L: '搜尋結果'})
        except Exception as e:
            print(f"searchContent error: {e}")
        return G_dict

    def playerContent(B, flag, pid, vipFlags):
        play_url = pid if pid.startswith('http') else B.home_url + (pid if pid.startswith('/') else f"/{pid}")
        try:
            resp = C.get(play_url, headers=B.headers, timeout=10)
            if resp.status_code == 200:
                yt_match = re.search(r'["\'](https?://(?:www\.)?(?:youtube\.com/embed/|youtube\.com/watch\?v=|youtu\.be/)[^"\']+)["\']', resp.text)
                if yt_match:
                    play_url = yt_match.group(1).replace('\\/', '/')
        except Exception:
            pass

        return {
            'url': play_url,
            'parse': 1,  # 啟動網頁嗅探載入 YouTube 框架
            'jx': 0,
            'header': {'User-Agent': B.headers['User-Agent'], 'Referer': B.home_url + '/'}
        }

    def localProxy(A, params):
        return 0

    def destroy(A):
        return '正在Destroy'

if __name__ == '__main__':
    pass
