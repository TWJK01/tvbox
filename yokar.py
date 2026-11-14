#!/usr/bin/python3
# -*- coding: utf-8 -*-

R = 'vod_pic'
Q = 'span.public-list-prb.hide.ft2'  # 可依 youkar.net 實際標籤微調
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
        A.extend = extend

    def getDependence(A):
        return []

    def isVideoFormat(A, url):
        return any(x in url.lower() for x in ['.m3u8', '.mp4']) if url else False

    def manualVideoCheck(A):
        return False

    def liveContent(B, url):
        return A

    def homeContent(G, filter):
        # 依據 yokar.net 截圖中的三大分類：電影、動漫、戲劇
        A = 'type_id'
        C = {
            'class': [
                {A: 'movie', D: '电影'},
                {A: 'anime', D: '动漫'},
                {A: 'drama', D: '戏剧'}
            ],
            'filters': {},
            B: [],
            E: 0,
            F: 0
        }
        return C

    def homeVideoContent(C):
        # 首頁推薦可直接留空或回傳列表
        A = {B: [], E: 0, F: 0}
        return A

    def categoryContent(D, cid, page, filter, ext):
        M = {B: [], E: 0, F: 0}
        N = D.home_url + f"/{cid}?page={page}"
        O = C.get(N, headers=D.headers)
        S = H(O.text.encode())
        # 抓取影片卡片清單（對應常見 AppleCMS / 響應式模板結構）
        T = S('a[href*="/detail/"], a[href*="/vod/"], a[href*="/video/"]')
        for A in T.items():
            U = A.attr(I)
            V = A.attr('title') or A('img').attr('alt')
            W = A('img').attr(P) or A('img').attr('src')
            X = A(Q).text()
            if U and V:
                M[B].append({J: U, K: V, R: W, L: X})
        return M

    def detailContent(N, did):
        U = '$$$'
        O = {B: [], E: 0, F: 0}
        P = did[0]
        M = N.home_url + (P if P.startswith('http') else f"/{P.lstrip('/')}")
        
        try:
            V = C.get(M, headers=N.headers)
            Q = H(V.text.encode())
            title = Q('h1').text() or Q('meta[property="og:title"]').attr('content')
            pic = Q('meta[property="og:image"]').attr('content')
            desc = Q('meta[property="og:description"]').attr('content')
            
            # 抓取播放集數清單
            X = Q('a[href*="/play/"], a[href*="/watch/"], a[href*="youtube"]')
            S = []
            for T in X.items():
                Z = T.text().strip() or "正片"
                M_url = T.attr(I)
                if M_url:
                    S.append(f"{Z}${M_url}")
            
            play_url = '#'.join(S) if S else f"播放正片${P}"
            
            O[B].append({
                D: A, J: P, K: title, L: A, 
                'vod_year': A, 'vod_area': A, 'vod_actor': A, 'vod_director': A, 
                'vod_content': desc, 'vod_play_from': 'YOKAR-YT', 'vod_play_url': play_url
            })
        except Exception as e:
            O[B].append({D: A, J: P, K: '解析錯誤', L: A, 'vod_play_from': 'error', 'vod_play_url': '播放$#'})
            
        return O

    def searchContent(D, key, quick, page='1'):
        G = {B: [], E: 0, F: 0}
        N = D.home_url + f"/search?wd={key}&page={page}"
        try:
            O = C.get(N, headers=D.headers)
            S = H(O.text.encode())
            T = S('a[href*="/detail/"], a[href*="/vod/"]')
            for A in T.items():
                U = A.attr(I)
                V = A.attr('title') or A('img').attr('alt')
                W = A('img').attr(P) or A('img').attr('src')
                X = A(Q).text()
                if U and V:
                    G[B].append({J: U, K: V, R: W, L: X})
        except Exception as e:
            pass
        return G

    def playerContent(B, flag, pid, vipFlags):
        # 因為是 YouTube 來源，設定 parse: 1 交由 App 內建嗅探播放
        play_url = pid if pid.startswith('http') else B.home_url + (pid if pid.startswith('/') else f"
