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
        options = {
            "headers": self.headers,
            "timeout": 8000
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

    def _clean_text(self, text):
        if not text:
            return ""
        pattern = re.compile('[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]')
        return pattern.sub("", text).strip()

    def _parse_vod_list(self, root):
        vod_list = []
        if root is None:
            return vod_list

        items = root.xpath(
            '//a[contains(@href, "/detail/") or contains(@href, "/vod/") or '
            'contains(@href, "/video/") or contains(@href, "/movie/") or '
            'contains(@href, "/anime/") or contains(@href, "/drama/")]'
        )
        seen_ids = set()

        for item in items:
            href_list = item.xpath('./@href')
            if not href_list:
                continue
            vod_id = href_list[0].strip()

            if vod_id in seen_ids or vod_id in ["/", "/movie", "/anime", "/drama", "#"]:
                continue

            title_nodes = item.xpath(
                './/@title | .//img/@alt | .//h3/text() | .//h4/text() | '
                './/div[contains(@class, "title") or contains(@class, "name")]/text() | ./text()'
            )
            raw_title = "".join(t.strip() for t in title_nodes if t.strip())
            title = self._clean_text(raw_title)
            if not title or len(title) < 2:
                continue

            pic_nodes = item.xpath('.//img/@data-src | .//img/@data-original | .//img/@data-echo | .//img/@src')
            pic = urljoin(self.base_url, pic_nodes[0].strip()) if pic_nodes else ""

            remark_nodes = item.xpath(
                './/span[contains(@class, "tag") or contains(@class, "remarks") or '
                'contains(@class, "note") or contains(@class, "state")]/text()'
            )
            remark = self._clean_text(remark_nodes[0]) if remark_nodes else ""

            seen_ids.add(vod_id)
            vod_list.append({
                "vod_id": vod_id,
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": remark
            })

        return vod_list

    def homeContent(self, filter):
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
            print(f"[YOKAR] homeContent error: {e}")
        return {
            "class": classes,
            "list": vod_list
        }

    def homeVideoContent(self):
        return {"list": []}

    def categoryContent(self, tid, pg, filter, extend):
        vod_list = []
        try:
            url = f"{self.base_url}/{tid}"
            root = self._get_html(url, params={"page": pg})
            vod_list = self._parse_vod_list(root)
        except Exception as e:
            print(f"[YOKAR] categoryContent error: {e}")
        return {
            "list": vod_list,
            "page": int(pg),
            "pagecount": 999,
            "limit": 20,
            "total": 9999
        }

    def detailContent(self, ids):
        vod_id = ids[0]
        detail_url = urljoin(self.base_url, vod_id)

        try:
            root = self._get_html(detail_url)
            if root is None:
                return {"list": []}

            title_node = root.xpath('//h1/text() | //h2[contains(@class, "title")]/text() | //meta[@property="og:title"]/@content')
            title = self._clean_text(title_node[0]) if title_node else "未知影片"

            pic_node = root.xpath('//div[contains(@class, "poster") or contains(@class, "thumb")]//img/@src | //meta[@property="og:image"]/@content')
            pic = urljoin(self.base_url, pic_node[0].strip()) if pic_node else ""

            desc_node = root.xpath('//div[contains(@class, "desc") or contains(@class, "content") or contains(@class, "intro")]//text() | //meta[@property="og:description"]/@content')
            desc = self._clean_text("".join(t.strip() for t in desc_node if t.strip()))

            # 抓取播放集數與連結（若包含 youtube 網址或播放頁面）
            ep_nodes = root.xpath('//a[contains(@href, "/play/") or contains(@href, "/watch/") or contains(@href, "youtube") or contains(@href, "youtu.be")]')
            episodes = []
            seen_eps = set()
            for ep in ep_nodes:
                ep_href_list = ep.xpath('./@href')
                if not ep_href_list:
                    continue
                ep_href = ep_href_list[0].strip()
                if ep_href in seen_eps:
                    continue

                ep_name_list = ep.xpath('.//text()')
                ep_name = self._clean_text("".join(t.strip() for t in ep_name_list if t.strip())) or "正片"
                seen_eps.add(ep_href)
                episodes.append(f"{ep_name}${ep_href}")

            play_from = "YouTube播放源"
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
            print(f"[YOKAR] detailContent error: {e}")
            return {"list": []}

    def searchContent(self, key, quick, pg="1"):
        vod_list = []
        try:
            search_url = f"{self.base_url}/search"
            root = self._get_html(search_url, params={"wd": key, "q": key, "page": pg})
            vod_list = self._parse_vod_list(root)
        except Exception as e:
            print(f"[YOKAR] searchContent error: {e}")
        return {"list": vod_list}

    def playerContent(self, flag, id, vipFlags):
        """
        針對 YouTube 來源，直接將網址或播放頁面交由 App 嗅探與解析 (parse: 1)
        """
        play_url = id if id.startswith("http") else urljoin(self.base_url, id)
        
        # 如果頁面中藏有直接的 YouTube 連結，也可嘗試先請求抓取
        try:
            response = self.net.req(play_url, {"headers": self.headers, "timeout": 8000})
            if not response.get("error") and 200 <= response["code"] < 300:
                html_text = response.get("content", "")
                # 尋找頁面中的 youtube 連結
                yt_match = re.search(r'["\'](https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[^"\']+)["\']', html_text)
                if yt_match:
                    play_url = yt_match.group(1).replace("\\/", "/")
        except Exception as e:
            print(f"[YOKAR] playerContent yt search error: {e}")

        return {
            "parse": 1,  # 啟用 App 內建嗅探/解析來播放 YouTube
            "playUrl": "",
            "url": play_url,
            "header": self.headers
        }
