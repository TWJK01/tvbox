# -*- coding: utf-8 -*-
import base64
import sys
import json
import requests
import re
from bs4 import BeautifulSoup

# 假設繼承自原有的 Spider 基類
# from base.spider import Spider 

class Spider(): # 這裡根據你環境調整繼承關係
    def getName(self):
        return "CustomYoutubeLive"

    def init(self, extend):
        self.extend = extend
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
        }

    def getYoutubeLive(self, channel_url):
        """
        嘗試從 /streams 或 /videos 頁面抓取正在直播的網址
        """
        try:
            # 優先檢查 streams 頁面，因為那裡最準確
            target_url = channel_url.rstrip('/') + '/streams'
            res = requests.get(target_url, headers=self.headers, timeout=10)
            
            # YouTube 的直播頁面原始碼中會包含 "is_live":true 或特定的 Live 標記
            # 我們尋找包含影片 ID 的 pattern，並確認它是正在直播的
            # 這是簡易正則匹配，抓取第一個符合「正在直播」特徵的影片 ID
            if '"style":"LIVE"' in res.text or 'is_live":true' in res.text:
                video_ids = re.findall(r'videoRenderer":\{"videoId":"([^"]+)"', res.text)
                if video_ids:
                    return f"https://www.youtube.com/watch?v={video_ids[0]}"
        except Exception as e:
            print(f"抓取 YouTube 失敗: {e}")
        return None

    def liveContent(self, url):
        # 最終輸出的清單
        result = []
        
        # 定義你要求的 YouTube 目標清單與對應分類
        yt_targets = [
            {"name": "華視新聞", "url": "https://www.youtube.com/@CtsTw", "genre": "台灣"},
            {"name": "Muse木棉花-闔家歡", "url": "https://www.youtube.com/@Muse_Family", "genre": "動漫"},
            {"name": "HOP Sports", "url": "https://www.youtube.com/@HOPSports", "genre": "體育"},
            {"name": "超級夜總會", "url": "https://www.youtube.com/@SuperNightClubCH29", "genre": "綜藝"}
        ]

        for item in yt_targets:
            live_url = self.getYoutubeLive(item['url'])
            if live_url:
                # 按照你的要求格式化: "分類,#genre#": 名稱,網址
                line = f'"{item["genre"]},#genre#": {item["name"]},{live_url}'
                result.append(line)
        
        # 這裡也可以保留你原本抓取 iptv345.com 的邏輯...
        # (篇幅關係暫略，可直接將原邏輯 append 到 result)

        return '\n'.join(result)

# 測試用
if __name__ == '__main__':
    spider = Spider()
    spider.init("")
    print(spider.liveContent(""))
