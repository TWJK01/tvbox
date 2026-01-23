const express = require('express');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const app = express();
const PORT = 3000;

// ==================== 配置區 ====================
const CONFIG = {
    MAIN_SERVER: 'http://skycn.dpdns.org/api.php',
    API_KEY: '123',
    CACHE_DIR: path.join(__dirname, 'cache'),
    CACHE_TIME: 300 * 1000, // 5 分鐘 (毫秒)
    UA: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
};

// 確保快取目錄存在
if (!fs.existsSync(CONFIG.CACHE_DIR)) {
    fs.mkdirSync(CONFIG.CACHE_DIR, { recursive: true });
}

// ==================== 輔助工具 ====================
const md5 = (str) => crypto.createHash('md5').update(str).digest('hex');

const getCache = (name) => {
    const file = path.join(CONFIG.CACHE_DIR, `${name}.json`);
    if (fs.existsSync(file)) {
        const stats = fs.statSync(file);
        if (Date.now() - stats.mtimeMs < CONFIG.CACHE_TIME) {
            return JSON.parse(fs.readFileSync(file, 'utf-8'));
        }
    }
    return null;
};

const setCache = (name, data) => {
    fs.writeFileSync(path.join(CONFIG.CACHE_DIR, `${name}.json`), JSON.stringify(data));
};

// ==================== 核心處理邏輯 ====================

app.get('/', async (req, res) => {
    const { id, m3u8, ts, action, format } = req.query;
    const protocol = req.protocol;
    const host = req.get('host');
    const selfUrl = `${protocol}://${host}${req.path}`;

    // --- 處理 TS 切片 ---
    if (ts && !id && !m3u8 && !action) {
        const targetTs = decodeURIComponent(ts);
        const urlObj = new URL(targetTs);
        const m3u8Url = `${urlObj.origin}${path.dirname(urlObj.pathname)}/index.m3u8`;
        
        // 從快取尋找對應的 Token
        const tokenInfo = getCache(`token_${md5(m3u8Url)}`);
        if (!tokenInfo) return res.status(404).send("Token cache expired");

        try {
            const response = await axios.get(targetTs, {
                headers: {
                    'User-Agent': CONFIG.UA,
                    'fftoken': tokenInfo.fftoken,
                    'playtoken': tokenInfo.playtoken,
                    'Host': urlObj.host
                },
                responseType: 'arraybuffer'
            });
            res.set('Content-Type', 'video/mp2t');
            return res.send(response.data);
        } catch (e) {
            return res.status(404).send("TS Download Failed");
        }
    }

    // --- 處理 M3U8 清單與重寫 ---
    if (m3u8 && !id && !ts && !action) {
        const targetM3u8 = decodeURIComponent(m3u8);
        const tokenInfo = getCache(`token_${md5(targetM3u8)}`);
        if (!tokenInfo) return res.status(404).send("Token not found");

        try {
            const response = await axios.get(targetM3u8, {
                headers: { 'fftoken': tokenInfo.fftoken, 'playtoken': tokenInfo.playtoken, 'User-Agent': CONFIG.UA }
            });

            const baseUrl = targetM3u8.substring(0, targetM3u8.lastIndexOf('/') + 1);
            const lines = response.data.split(/\r?\n/);
            const newLines = lines.map(line => {
                const t = line.trim();
                if (!t || t.startsWith('#')) return line;
                
                let fullTsUrl;
                if (t.startsWith('http')) {
                    fullTsUrl = t;
                } else if (t.startsWith('/')) {
                    const urlObj = new URL(targetM3u8);
                    fullTsUrl = `${urlObj.origin}${t}`;
                } else {
                    fullTsUrl = baseUrl + t;
                }
                return `${selfUrl}?ts=${encodeURIComponent(fullTsUrl)}`;
            });

            res.set('Content-Type', 'application/vnd.apple.mpegurl');
            return res.send(newLines.join('\n'));
        } catch (e) {
            return res.status(500).send("M3U8 Proxy Error");
        }
    }

    // --- 處理頻道 ID 入口 ---
    if (id && !action) {
        const playInfo = await fetchPlayInfo(id);
        if (playInfo && playInfo.m3u8_url) {
            setCache(`token_${md5(playInfo.m3u8_url)}`, {
                fftoken: playInfo.fftoken,
                playtoken: playInfo.playtoken
            });
            return res.redirect(`${selfUrl}?m3u8=${encodeURIComponent(playInfo.m3u8_url)}`);
        }
        return res.status(404).send("Channel Info Error");
    }

    // --- 處理頻道列表 (輸出 .m3u 格式) ---
    if (action === 'list') {
        const channels = await fetchChannelList();
        if (format === 'json') return res.json(channels);

        let m3u = "#EXTM3U\n";
        channels.forEach(ch => {
            const logo = ch.logo ? ` tvg-logo="${ch.logo}"` : "";
            const group = ch.group ? ` group-title="${ch.group}"` : "";
            m3u += `#EXTINF:-1 tvg-id="${ch.id}"${logo}${group},${ch.title}\n`;
            m3u += `${selfUrl}?id=${ch.id}\n`;
        });
        res.set('Content-Type', 'application/vnd.apple.mpegurl');
        return res.send(m3u);
    }

    // --- 首頁 ---
    res.send(`
        <h2>直播代理伺服器已啟動</h2>
        <ul>
            <li><a href="/?action=list">查看 M3U 頻道列表 (PotPlayer 用)</a></li>
            <li><a href="/?action=list&format=json">查看 JSON 格式</a></li>
        </ul>
    `);
});

// ==================== 資料抓取函數 ====================

async function fetchChannelList() {
    const cached = getCache('channels_list');
    if (cached) return cached;

    try {
        const res = await axios.get(`${CONFIG.MAIN_SERVER}?action=get_channels&api_key=${CONFIG.API_KEY}`);
        if (res.data?.success) {
            const channels = res.data.data.channels;
            setCache('channels_list', channels);
            return channels;
        }
    } catch (e) { console.error("List Error"); }
    return [];
}

async function fetchPlayInfo(id) {
    const cacheKey = `play_${md5(id)}`;
    const cached = getCache(cacheKey);
    if (cached) return cached;

    try {
        const res = await axios.get(`${CONFIG.MAIN_SERVER}?action=get_play_info&id=${id}&api_key=${CONFIG.API_KEY}`);
        if (res.data?.success) {
            const info = res.data.data;
            setCache(cacheKey, info);
            return info;
        }
    } catch (e) { console.error("Play Info Error"); }
    return null;
}

app.listen(PORT, () => {
    console.log(`[Proxy Server] 正在執行：http://localhost:${PORT}`);
    console.log(`[M3U 清單地址] http://localhost:${PORT}/?action=list`);
});