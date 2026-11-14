# -*- coding: utf-8 -*-
import sys
import json
import re
from urllib.parse import urljoin
from base.spider import Spider


class Spider(Spider):
    def getName(self):
        return "YOKAR"

    def init(self, extend=""):
        self.base_url = "https://yokar.net"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "Referer": "https://yokar.net/"
        }

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def _parse_list(self, root):
        vod_list = []
        if root is None:
            return vod_list

        # 尋找頁面中包含圖片的連結卡片
        items = root.xpath('//a[.//img]')
        seen = set()

        for item in items:
            href_list = item.xpath('./@href')
            if not href_list:
                continue
            href = href_list[0].strip()

            # 排除首頁或無效連結
            if not href or href in ["/", "#", "/movie", "/anime", "/drama"] or href in seen:
                continue

            # 擷取片名
            title_nodes = item.xpath('.//@title | .//img/@alt | .//h3/text() | .//h4/text() | ./text()')
            title = "".join(t.strip() for t in title_nodes if t.strip())
            if not title or len(title) < 2:
                continue

            # 擷取封面圖
            pic_nodes = item.xpath('.//img/@data-src | .//img/@data-original | .//img/@src')
            pic = urljoin(self.base_url, pic_nodes[0].strip()) if pic_nodes else ""

            seen.add(href)
            vod_list.append({
                "vod_id": href,
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": "YouTube"
            })

        return vod_list

    def homeContent(self, filter):
        classes = [
            {"type_name": "電影", "type_id": "movie"},
            {"type_name": "動漫", "type_id": "anime"},
            {"type_name": "戲劇", "type_id": "drama"}
        ]
        return {"class": classes}

    def homeVideoContent(self):
        videos = []
        try:
            rsp = self.fetch(self.base_url, headers=self.headers, timeout=10)
            if rsp and rsp.text:
                root = self.html(rsp.text)
                videos = self._parse_list(root)
        except Exception as e:
            print(f"[YOKAR homeVideoContent Error]: {e}")
        return {"list": videos}

    def categoryContent(self, tid, pg, filter, extend):
        videos = []
        try:
            url = f"{self.base_url}/{tid}?page={pg}"
            rsp = self.fetch(url, headers=self.headers, timeout=10)
            if rsp and rsp.text:
                root = self.html(rsp.text)
                videos = self._parse_list(root)
        except Exception as e:
            print(f"[YOKAR categoryContent Error]: {e}")

        return {
            "list": videos,
            "page": int(pg),
            "pagecount": 999,
            "limit": 20,
            "total": 9999
        }

    def detailContent(self, ids):
        vid = ids[0]
        detail_url = urljoin(self.base_url, vid)
        title = "YOKAR 影視"
        pic = ""
        desc = ""
        play_urls = [f"立即播放${vid}"]

        try:
            rsp = self.fetch(detail_url, headers=self.headers, timeout=10)
            if rsp and rsp.text:
                root = self.html(rsp.text)
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

                    # 抓取分集或播放連結
                    ep_nodes = root.xpath('//a[contains(@href, "/play") or contains(@href, "/watch") or contains(@href, "youtube") or contains(@href, "youtu.be")]')
                    if ep_nodes:
                        temp_urls = []
                        seen_ep = set()
                        for ep in ep_nodes:
                            h_list = ep.xpath('./@href')
                            if not h_list:
                                continue
                            h = h_list[0].strip()
                            if h in seen_ep:
                                continue
                            seen_ep.add(h)
                            name = "".join(ep.xpath('.//text()')).strip() or "正片"
                            temp_urls.append(f"{name}${h}")
                        if temp_urls:
                            play_urls = temp_urls
        except Exception as e:
            print(f"[YOKAR detailContent Error]: {e}")

        vod = {
            "vod_id": str(vid),
            "vod_name": title,
            "vod_pic": pic,
            "vod_content": desc,
            "vod_play_from": "YOKAR-YT",
            "vod_play_url": "#".join(play_urls)
        }
        return {"list": [vod]}

    def searchContent(self, key, quick, pg="1"):
        videos = []
        try:
            search_url = f"{self.base_url}/search?wd={key}&page={pg}"
            rsp = self.fetch(search_url, headers=self.headers, timeout=10)
            if rsp and rsp.text:
                root = self.html(rsp.text)
                videos = self._parse_list(root)
        except Exception as e:
            print(f"[YOKAR searchContent Error]: {e}")
        return {"list": videos}

    def playerContent(self, flag, id, vipFlags):
        play_url = id if id.startswith("http") else urljoin(self.base_url, id)
        # 交由影視 App 內建 WebView 嗅探播放 YouTube
        return {
            "parse": 1,
            "url": play_url,
