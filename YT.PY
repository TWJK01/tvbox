from flask import Flask, Response
import yt_dlp

app = Flask(__name__)

def get_youtube_lives(channel_url):
    """抓取頻道中所有直播中的網址"""
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
    }
    lines = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(channel_url, download=False)
            if 'entries' in result:
                for entry in result['entries']:
                    if entry.get('live_status') == 'live':
                        title = entry.get('title').replace(',', ' ') # 避免標題有逗號搞亂格式
                        url = f"https://www.youtube.com/watch?v={entry.get('id')}"
                        lines.append(f"{title},{url}")
        except Exception as e:
            return [f"錯誤,請檢查網路或IP: {str(e)}"]
    return lines

@app.route('/muse.txt')
def muse_live_api():
    # 木棉花直播頁面
    channel_url = "https://www.youtube.com/@Muse_Family/streams"
    live_lines = get_youtube_lives(channel_url)
    
    # 組合內容
    content = "\n".join(live_lines)
    
    # 返回純文字格式，這是 TVBox 讀取直播源的標準格式
    return Response(content, mimetype='text/plain')

if __name__ == '__main__':
    # 啟動在 5000 端口，外網可訪問請設為 0.0.0.0
    app.run(host='0.0.0.0', port=5000)
