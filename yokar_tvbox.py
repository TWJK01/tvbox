# -*- coding: utf-8 -*-
import sys, json, time, base64, random, string, hashlib
from urllib.parse import urlencode, quote
from base.spider import Spider
from lxml import etree
from urllib.parse import urljoin

class Spider(Spider):
    def __init__(self):
        super().__init__()
        self.base_url = 'https://yokar.net'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'Referer': 'https://yokar.net/',
            'Origin': 'https://yokar.net'
        }

    def getName(self): 
        return "YOKAR"

    def init(self, extend=""):
        try: 
            cfg = json.loads(extend) if isinstance(extend, str) and extend.strip().startswith('{') else extend if isinstance(extend, dict) else {}
        except Exception: 
            cfg = {}
        self.base_url = cfg.get('base_url', self.base_url)
        return self.homeContent(False)

    def isVideoFormat(self, url): 
        return any(x in url.lower() for x in ['.m3u8', '.mp4']) if url else False
        
    def manualVideoCheck(self): 
        return False
        
    def destroy(self): 
        pass

    def _get_html(self, url, params=None):
        """
        發送 GET 請求並回傳 lxml 解析樹，遵循最新 self.net.req 規範
        """
        options = {
            "headers": self.headers,
            "timeout": 8000
        }
        if params:
            options["params"] = params

        response = self.net.req(url, options)
        if response.get("error"):
            return None
        if not 200 <= response["code"] < 300:
            return None

        content = response.get("content", "")
        if not content:
            return None
        return etree.HTML(content)

    def _parse_vod_list(self, root):
        """
        解析影片清單卡片
        """
        vod_list = []
        if root is None:
            return vod_list

        items = root.xpath('//a[contains(@href, "/detail/") or contains(@href, "/vod/") or contains(@href, "/video/")]')
        seen_ids = set()

        for item in items:
            href = item.xpath('./@href')
            if not href:
                continue
            vod_id = href[0].strip()
            if vod_id in seen_ids or vod_id in ["/", "#"]:
                continue

            title_nodes = item.xpath('.//@title | .//img/@alt | .//h3/text() | ./text()')
            title = "".join(t.strip() for t in title_nodes if t.strip())
            if not title or len(title) < 2:
                continue

            pic_nodes = item.xpath('.//img/@data-src | .//img/@src')
            pic = urljoin(self.base_url, pic_nodes[0].strip()) if pic_nodes else ""

            seen_ids.add(vod_id)
            vod_list.append({
                'vod_id': str(vod_id),
                'vod_name': title,
                'vod_pic': pic,
                'vod_remarks': 'YouTube'
            })
        return vod_list

    def homeContent(self, filter):
        # 依據網站導覽列定義分類
        classes = [
            {'type_name': '電影', 'type_id': 'movie'},
            {'type_name': '動漫', 'type_id': 'anime'},
            {'type_name': '戲劇', 'type_id': 'drama'}
        ]
        return {'class': classes}

    def homeVideoContent(self):
        root = self._get_html(self.base_url)
        videos = self._parse_vod_list(root)
        return {'list': videos}

    def categoryContent(self, tid, pg, filter, extend):
        page = int(pg) if str(pg).isdigit() else 1
        url = f"{self.base_url}/{tid}"
        root = self._get_html(url, params={'page': page})
        videos = self._parse_vod_list(root)
        return {'list': videos, 'page': page, 'pagecount': 9999, 'limit': 24, 'total': 999999}

    def detailContent(self, ids):
        vid = ids[0]
        detail_url = urljoin(self.base_url, vid)
        root = self._get_html(detail_url)
        
        title = "未知影片"
        pic = ""
        desc = ""
        episodes = [f"播放正片${vid}"]

        if root is not None:
            t_nodes = root.xpath('//h1/text() | //meta[@property="og:title"]/@content')
            if t_nodes: 
                title = t_nodes[0].strip()
            p_nodes = root.xpath('//meta[@property="og:image"]/@content')
            if p_nodes: 
                pic = p_nodes[0].strip()
            d_nodes = root.xpath('//meta[@property="og:description"]/@content')
            if d_nodes: 
                desc = d_nodes[0].strip()

            ep_nodes = root.xpath('//a[contains(@href, "/play/") or contains(@href, "/watch/")]')
            if ep_nodes:
                episodes = []
                for ep in ep_nodes:
                    hrefs = ep.xpath('./@href')
                    if hrefs:
                        name = "".join(ep.xpath('.//text()')).strip() or "正片"
                        episodes.append(f"{name}${hrefs[0].strip()}")

        vod = {
            'vod_id': str(vid),
            'vod_name': title,
            'vod_pic': pic,
            'vod_content': desc,
            'vod_play_from': 'YOKAR-YT',
            'vod_play_url': '#'.join(episodes)
        }
        return {'list': [vod]}

    def searchContent(self, key, quick, pg="1"):
        page = int(pg) if str(pg).isdigit() else 1
        search_url = f"{self.base_url}/search"
        root = self._get_html(search_url, params={'wd': key, 'page': page})
        videos = self._parse_vod_list(root)
        return {'list': videos}

    def playerContent(self, flag, id, vipFlags):
        play_url = id if id.startswith("http") else urljoin(self.base_url, id)
        # 因為是 YouTube 來源，交由 App 內建嗅探器播放 (parse: 1)
        return {
            'parse': 1, 
            'url': play_url, 
            'header': self.headers
        }

    def localProxy(self, param): 
        return None
