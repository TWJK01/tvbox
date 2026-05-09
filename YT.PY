import requests
import re
import json

# 目標頻道清單
channels = {
    "台灣,#genre#": [
        {"name": "華視新聞", "url": "https://www.youtube.com/@CtsTw/streams"}
    ],
    "動漫,#genre#": [
        {"name": "Muse木棉花-闔家歡", "url": "https://www.youtube.com/@Muse_Family/streams"}
    ],
    "體育,#genre#": [
        {"name": "HOP Sports", "url": "https://www.youtube.com/@HOPSports/streams"}
    ],
    "綜藝,#genre#": [
        {"name": "超級夜總會", "url": "https://www.youtube.com/@SuperNightClubCH29/streams"}
    ]
}

def get_live_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # 搜尋 YouTube 頁面內部的 JSON 數據
        json_str = re.search(r'var ytInitialData = (\{.*?\});', response.text).group(1)
        data = json.loads(json_str)
        
        # 遍歷頁面物件尋找正在直播的標記
        # 通常直播會帶有 "style": "LIVE" 或渲染在影片上方
        if '"style":"LIVE"' in response.text:
            video_id = re.search(r'"videoId":"([^"]+)"', response.text).group(1)
            return f"https://www.youtube.com/watch?v={video_id}"
    except Exception as e:
        print(f"解析失敗: {url}, 錯誤: {e}")
    return None

def save_to_txt():
    with open("live.txt", "w", encoding="utf-8") as f:
        for genre, items in channels.items():
            # 先寫入分類標籤
            f.write(f"{genre}\n")
            for item in items:
                print(f"正在檢查: {item['name']}...")
                live_url = get_live_url(item['url'])
                if live_url:
                    # 格式：網址中文名稱,網址
                    f.write(f"{item['name']},{live_url}\n")
                else:
                    # 若沒直播，可選擇不寫入或註記
                    print(f"--- {item['name']} 目前沒有直播 ---")
            f.write("\n") # 分類間空一行

if __name__ == "__main__":
    save_to_txt()
    print("\n完成！請查看目錄下的 live.txt")
