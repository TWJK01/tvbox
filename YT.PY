# -*- coding: utf-8 -*-
import json
import re
import requests

# TVBox 爬蟲必須繼承自一個基礎類別或符合特定的類別名稱
class Spider():
    def getName(self):
        return "YouTube直播抓取"

    def init(self, extend):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def get_yt_live(self, url):
        """核心：抓取 YouTube 頻道內部的直播網址"""
        try:
            # 請求頻道直播分頁
            res = requests.get(url + "/streams", headers=self.headers, timeout=5)
            # 尋找 "style":"LIVE" 的影片 ID
            if '"style":"LIVE"' in res.text:
                vid = re.search(r'"videoId":"([^"]+)"', res.text).group(1)
                return f"https://www.youtube.com/watch?v={vid}"
        except:
            return None
        return None

    def liveContent(self, url):
        """
        TVBox 直播介面調用的核心函式
        回傳格式為: 分類名稱,#genre#\n頻道名稱,直播連結
        """
        # 定義您要抓取的頻道資訊
        targets = [
            {"name": "華視新聞", "url": "https://www.youtube.com/@CtsTw", "genre": "台灣"},
            {"name": "Muse木棉花-闔家歡", "url": "https://www.youtube.com/@Muse_Family", "genre": "動漫"},
            {"name": "HOP Sports", "url": "https://www.youtube.com/@HOPSports", "genre": "體育"},
            {"name": "超級夜總會", "url": "https://www.youtube.com/@SuperNightClubCH29", "genre": "綜藝"}
        ]

        result = []
        for item in targets:
            live_url = self.get_yt_live(item['url'])
            if live_url:
                # 按照 TVBox 直播格式構建字串
                result.append(f"{item['genre']},#genre#")
                result.append(f"{item['name']},{live_url}")
        
        # 返回給 TVBox 的最終純文字內容
        return "\n".join(result)

    # 以下為 TVBox 必要的空函式，避免報錯
    def homeContent(self, filter): return {}
    def homeVideoContent(self): return {}
    def categoryContent(self, tid, pg, filter, extend): return {}
    def detailContent(self, ids): return {}
    def searchContent(self, key, quick): return {}
    def playerContent(self, flag, id, vipFlags): return {}
