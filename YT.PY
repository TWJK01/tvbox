import yt_dlp

# 定義目標頻道與分類
channels = {
    "新聞": {
        "華視新聞": "https://www.youtube.com/@CtsTw/streams",
    },
    "動漫": {
        "Muse木棉花-闔家歡": "https://www.youtube.com/@Muse_Family/streams",
    },
    "體育": {
        "HOP Sports": "https://www.youtube.com/@HOPSports/streams",
    },
    "綜藝": {
        "超級夜總會": "https://www.youtube.com/@SuperNightClubCH29/streams",
    }
}

def get_live_url(channel_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # 抓取頻道影片列表
            info = ydl.extract_info(channel_url, download=False)
            if 'entries' in info:
                for entry in info['entries']:
                    # 判斷是否為正在進行的直播
                    if entry.get('live_status') == 'is_live':
                        return entry.get('url')
        except Exception as e:
            return None
    return None

# 執行抓取並按格式輸出
print("--- 抓取結果 ---")
for genre, items in channels.items():
    for name, url in items.items():
        live_link = get_live_url(url)
        if live_link:
            # 依照要求的格式輸出
            print(f'"{genre},#genre#": {name},{live_link}')
        else:
            # 若 streams 沒找到，可選 fallback 到 /videos 再檢查一次
            pass