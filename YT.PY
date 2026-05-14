# coding=utf-8

import requests
import re

# YouTube 頻道直播頁
CHANNEL_URL = "https://www.youtube.com/@Muse_Family/streams"

# Headers
headers = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

try:

    # 取得頁面
    response = requests.get(
        CHANNEL_URL,
        headers=headers,
        timeout=15
    )

    html = response.text

    # 抓所有 LIVE_NOW 的 videoId
    matches = re.findall(
        r'"videoId":"(.*?)".*?LIVE_NOW',
        html,
        re.S
    )

    # 去重
    video_ids = []
    seen = set()

    for vid in matches:

        if vid not in seen:

            seen.add(vid)
            video_ids.append(vid)

    # 輸出結果
    if video_ids:

        for vid in video_ids:

            live_url = (
                "https://www.youtube.com/watch?v="
                + vid
            )

            print(live_url)

    else:

        print("目前沒有正在直播")

except Exception as e:

    print("錯誤:", str(e))
