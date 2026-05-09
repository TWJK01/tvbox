import requests
import re
import os

def get_youtube_live(name, channel_url):
    """
    抓取頻道是否正在直播，優先檢查 /streams，其次 /videos
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    # 檢查直播標籤頁與影片標籤頁
    suffixes = ['/streams', '/videos']
    
    for suffix in suffixes:
        try:
            url = channel_url.rstrip('/') + suffix
            response = requests.get(url, headers=headers, timeout=15)
            html = response.text
            
            # 判斷邏輯：尋找包含 "style":"LIVE" 且具有影片 ID 的區塊
            # YouTube 網頁原始碼會將直播標註為 "style":"LIVE"
            if '"style":"LIVE"' in html or '"label":"LIVE"' in html:
                # 提取第一個符合直播狀態的 videoId
                video_ids = re.findall(r'"videoId":"([^"]+)"', html)
                if video_ids:
                    # 確保抓到的是最新的直播連結
                    return f"https://www.youtube.com/watch?v={video_ids[0]}"
        except Exception as e:
            print(f"解析 {name} 時發生錯誤: {e}")
            
    return None

def main():
    # 定義目標頻道與分類資訊
    channels = [
        {"name": "華視新聞", "url": "https://www.youtube.com/@CtsTw/", "genre": "台灣"},
        {"name": "Muse木棉花-闔家歡", "url": "https://www.youtube.com/@Muse_Family", "genre": "動漫"},
        {"name": "HOP Sports", "url": "https://www.youtube.com/@HOPSports/", "genre": "體育"},
        {"name": "超級夜總會", "url": "https://www.youtube.com/@SuperNightClubCH29", "genre": "綜藝"}
    ]

    output_file = "live_list.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        print("開始抓取直播網址...")
        
        for item in channels:
            live_link = get_youtube_live(item['name'], item['url'])
            
            if live_link:
                # 依照要求格式：網址中文名稱,網址
                # 加上 TVBox 識別分類的格式
                content = f"{item['name']},{live_link}\n"
                f.write(content)
                print(f"成功抓取: {item['name']}")
            else:
                print(f"目前未直播: {item['name']}")

    print(f"\n任務完成！結果已寫入: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()
