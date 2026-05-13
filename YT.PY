from flask import Flask, jsonify
import requests
import re
import json

app = Flask(__name__)

headers = {
    "User-Agent": "Mozilla/5.0"
}

# 多頻道
CHANNELS = {
    "Muse Family": "https://www.youtube.com/@Muse_Family/streams",
    "台視新聞": "https://www.youtube.com/@TTV_NEWS/streams",
    "中視新聞": "https://www.youtube.com/@chinatvnews/streams",
    "TVBS NEWS": "https://www.youtube.com/@TVBSNEWS01/streams"
}


def get_channel_live(channel_name, url):

    result = []

    try:

        html = requests.get(url, headers=headers, timeout=15).text

        match = re.search(
            r"var ytInitialData = ({.*?});</script>",
            html
        )

        if not match:
            return result

        data = json.loads(match.group(1))

        def find_live(obj):

            if isinstance(obj, dict):

                if "videoRenderer" in obj:

                    vr = obj["videoRenderer"]

                    # 判斷直播中
                    if "LIVE_NOW" in str(vr):

                        vid = vr.get("videoId")

                        title = ""

                        try:
                            title = vr["title"]["runs"][0]["text"]
                        except:
                            pass

                        if vid:

                            result.append({
                                "name": f"[{channel_name}] {title}",
                                "url": f"https://www.youtube.com/watch?v={vid}"
                            })

                for v in obj.values():
                    find_live(v)

            elif isinstance(obj, list):

                for item in obj:
                    find_live(item)

        find_live(data)

    except Exception as e:
        print(channel_name, e)

    return result


@app.route("/live")
def live():

    merged = []
    seen = set()

    for name, url in CHANNELS.items():

        lives = get_channel_live(name, url)

        for item in lives:

            if item["url"] not in seen:

                seen.add(item["url"])
                merged.append(item)

    return jsonify({
        "list": merged
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
