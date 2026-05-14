# coding=utf-8

import urllib.request
import re
import ssl

# 忽略 SSL
ssl._create_default_https_context = (
    ssl._create_unverified_context
)

url = "https://www.youtube.com/@Muse_Family/streams"

headers = {
    "User-Agent": "Mozilla/5.0"
}

req = urllib.request.Request(
    url,
    headers=headers
)

try:

    html = urllib.request.urlopen(
        req,
        timeout=15
    ).read().decode("utf-8")

    # 抓所有直播 videoId
    matches = re.findall(
        r'"videoId":"(.*?)".*?LIVE_NOW',
        html,
        re.S
    )

    # 去重
    ids = list(set(matches))

    if ids:

        for vid in ids:

            print(
                "https://www.youtube.com/watch?v="
                + vid
            )

    else:

        print("目前沒有直播")

except Exception as e:

    print("錯誤:", e)
