# coding=utf-8
import re
import json
from urllib.parse import urljoin
from lxml import etree
from base.spider import Spider


class Spider(Spider):
    def init(self, extend=""):
        self.base_url = "https://yokar.net"
        self.headers = {
            "User-Agent": self.net.getUserAgent() or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": f"{self.base_url}/"
        }

    def getDependence(self):
        return []

    def _get_html(self, url, params=None):
        """
        統一發送 GET 請求並回傳 lxml 解析樹，遵循最新 self.net.req 規範
        """
        options = {
            "headers": self.headers,
            "timeout": 5000  # 單位為毫秒[cite: 1]
        }
        if params:
            options["params"] = params

        response = self.net.req(url, options)
        if response.get("error"):
            raise RuntimeError(f"網路請求錯誤: {response['error']}")
        if not 200 <= response["code"] < 300:
            raise RuntimeError(f"HTTP 狀態碼異常: {response['code']}")

        content = response.get("content", "")
        if not content:
            return None
        return etree.HTML(content)

    def _parse_vod_list(self, root):
        """
        解析列表頁或推薦頁的影片卡片
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
            if vod_id in seen_ids:
                continue

            title_nodes = item.xpath('.//@title | .//h3/text() | .//h4/text() | .//div[contains(@class, "title")]/text() | ./text()')
            title = "".join(t.strip() for t in title_nodes if t.strip())
            if not title:
                continue

            pic_nodes = item.xpath('.//img/@data-src | .//img/@data-original | .//img/@src')
            pic = urljoin(self.base_url, pic_nodes[0].strip()) if pic_nodes else ""

            remark_nodes = item.xpath('.//span[contains(@class, "tag") or contains(@class, "remarks") or contains(@class, "note")]/text()')
            remark = remark_nodes[0].strip() if remark_nodes else ""

            seen_ids.add(vod_id)
            vod_list.append({
                "vod_id": vod_id,
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": remark
            })

        return vod_list

    def homeContent(self, filter):
        """
        首頁分類與推薦內容（依據網站截圖：電影、動漫、戲劇）[cite: 2]
        """
        classes = [
            {"type_id": "movie", "type_name": "電影"},
            {"type_id": "anime", "type_name": "動漫"},
            {"type_id": "drama", "type_name": "戲劇"}
        ]

        vod_list = []
        try:
            root = self._get_html(self.base_url)
            vod_list = self._parse_vod_list(root)
        except Exception as e:
            print(f"homeContent error: {e}")

        # 直接回傳 dict，不使用 json.dumps[cite: 1]
        return {
            "class": classes,
            "list": vod_list
        }

    def homeVideoContent(self):
        return {"list": []}

    def categoryContent(self, tid, pg, filter, extend):
        """
        分類列表與分頁
        """
        vod_list = []
        try:
            url = f"{self.base_url}/{tid}"
            root = self._get_html(url, params={"page": pg})
            vod_list = self._parse_vod_list(root)
        except Exception as e:
            print(f"categoryContent error: {e}")

        return {
            "list": vod_list,
            "page": int(pg),
            "pagecount": 999,
            "limit": 20,
            "total": 9999
        }

    def detailContent(self, ids):
        """
        影片詳情頁
        """
        vod_id = ids[0]
        detail_url = urljoin(self.base_url, vod_id)

        try:
            root = self._get_html(detail_url)
            if root is None:
                return {"list": []}

            title_node = root.xpath('//h1/text() | //h2[contains(@class, "title")]/text()')
            title = title_node[0].strip() if title_node else "未知片名"

            pic_node = root.xpath('//div[contains(@class, "poster") or contains(@class, "thumb")]//img/@src | //meta[@property="og:image"]/@content')
            pic = urljoin(self.base_url, pic_node[0].strip()) if pic_node else ""

            desc_node = root.xpath('//div[contains(@class, "desc") or contains(@class, "content") or contains(@class, "intro")]//text()')
            desc = "".join(t.strip() for t in desc_node if t.strip())

            ep_nodes = root.xpath('//a[contains(@href, "/play/") or contains(@href, "/watch/")]')
            episodes = []
            for ep in ep_nodes:
                ep_name_list = ep.xpath('.//text()')
                ep_name = "".join(t.strip() for t in ep_name_list if t.strip()) or "正片"
                ep_href = ep.xpath('./@href')
                if ep_href:
                    episodes.append(f"{ep_name}${ep_href[0].strip()}")

            play_from = "YOKAR線路"
            play_url = "#".join(episodes) if episodes else f"立即播放${vod_id}"

            vod = {
                "vod_id": vod_id,
                "vod_name": title,
                "vod_pic": pic,
                "vod_content": desc,
                "vod_play_from": play_from,
                "vod_play_url": play_url
            }
            return {"list": [vod]}

        except Exception as e:
            print(f"detailContent error: {e}")
            return {"list": []}

    def searchContent(self, key, quick, pg="1"):
        """
        關鍵字搜尋
        """
        vod_list = []
        try:
            search_url = f"{self.base_url}/search"
            root = self._get_html(search_url, params={"wd": key, "q": key, "page": pg})
            vod_list = self._parse_vod_list(root)
        except Exception as e:
            print(f"searchContent error: {e}")

        return {"list": vod_list}

    def playerContent(self, flag, id, vipFlags):
        """
        解析播放地址
        """
        play_page_url = urljoin(self.base_url, id)
        try:
            response = self.net.req(play_page_url, {
                "headers": self.headers,
                "timeout": 5000
            })
            if response.get("error") or not 200 <= response["code"] < 300:
                return {"parse": 1, "playUrl": "", "url": play_page_url, "header": self.headers}

            html_text = response.get("content", "")
            # 使用標準庫 re 搜尋直链[cite: 1]
            match = re.search(r'["\'](https?://[^"\']+\.(?:m3u8|mp4)[^"\']*)["\']', html_text)
            if match:
                stream_url = match.group(1).replace("\\/", "/")
                return {
                    "parse": 0,
                    "playUrl": "",
                    "url": stream_url,
                    "header": self.headers
                }
        except Exception as e:
            print(f"playerContent error: {e}")

        return {
            "parse": 1,
            "playUrl": "",
            "url": play_page_url,
            "header": self.headers
        }
