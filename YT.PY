# -*- coding: utf-8 -*-
import base64
import sys
import json
import requests
import yt_dlp
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return "MuseFamily"

    def init(self, extend):
        self.extend = extend
        try:
            self.extendDict = json.loads(extend)
        except:
            self.extendDict = {}
        pass

    def getDependence(self):
        return []

    def liveContent(self, url):
        """
        TVBox 讀取直播頻道時會呼叫此函式
        """
        channel_list = ["#EXTM3U"]
        
        # 定義要抓取的 YouTube 頻道
        # 你可以根據需要增加多個頻道
        target_channels = [
            {"name": "木棉花家族", "url": "https://www.youtube.com/@Muse_Family/streams"}
        ]

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True, # 快速提取清單
        }

        for channel in target_channels:
            group_name = channel["name"]
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # 抓取 YouTube 直播分頁
                    result = ydl.extract_info(channel["url"], download=False)
                    
                    if 'entries' in result:
                        for entry in result['entries']:
                            # 過濾出「正在直播」的項目
                            if entry.get('live_status') == 'live':
                                name = entry.get('title').replace(',', ' ') # 移除名稱中的逗號防止格式錯誤
                                video_id = entry.get('id')
                                video_url = f"https://www.youtube.com/watch?v={video_id}"
                                
                                # 依照你要求的格式變化：中文名稱,網址
                                # 在 M3U 中，格式為 #EXTINF...,名稱 \n 網址
                                m3u_entry = (
                                    f'#EXTINF:-1 group-title="{group_name}",{name}\n'
                                    f'{video_url}'
                                )
                                channel_list.append(m3u_entry)
                                
            except Exception as e:
                print(f"抓取 {group_name} 失敗: {str(e)}")

        return '\n'.join(channel_list)

    # 以下為 TVBox Spider 必備但在此案例中可留空的函式
    def homeContent(self, filter):
        return {}

    def homeVideoContent(self):
        return {}

    def categoryContent(self, cid, page, filter, ext):
        return {}

    def detailContent(self, did):
        return {}

    def searchContent(self, key, quick, page='1'):
        return {}

    def playerContent(self, flag, pid, vipFlags):
        # 如果 TVBox 內建解析可以處理 YouTube 連結，這裡回傳空
        # 如果需要手動解析 m3u8，才需要在這裡調用 yt-dlp 獲取直鏈
        return {}

    def destroy(self):
        pass

if __name__ == '__main__':
    # 測試程式碼
    spy = Spider()
    spy.init("")
    print(spy.liveContent(""))
