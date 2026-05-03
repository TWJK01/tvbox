import { Crypto } from 'assets://js/lib/cat.js'

let api = 'http://www.viaov.top/api/wbtj5hmx'
let crapi = 'http://lc.aacalive.com:26789/list/ghjnvq5o/cr.json'
let device_id = "02:fc:20:23:38:4cd0:22:be:df:9a:74"
let hardware = 'overlord-Amlogic-4-3.93 GB-117 GB-nw'
let version = 'DreamTV 20240211'
let from = '2011'
let key = 'MZkF@270mp#cOKD0%8Y8dV&5AmH&BTzq'

let siteKey = '';
let siteType = "3";

let tokenInfo = {
    token: null,
    server: null,
    client_id: null,
    password: null,
    expireTime: 0
};

let xApiKey = null;
let liveCache = null;
let bgTimerHandle = null;

const TOKEN_TTL_SEC = 300;
const MIN_BINARY_B64 = 32;
const BG_INTERVAL_MS = 5 * 60 * 1000;
const STEP_DELAY_MS = 200;

// ============== 工具 ==============
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function genXApiKey() {
    const rand = Math.floor(Math.random() * 2147483647).toString();
    const keyMd5 = Crypto.MD5(rand).toString();
    const uuid = keyMd5.replace(/(.{8}).(.{4}).(.{4}).(.{4})(.*)/, "$1-$2-$3-$4-$5");
    const t = Math.floor(Date.now() / 1000);
    const apikey = uuid + 'rfsy&doqg@hdvpameh#ptrcg%jgerlcs' + t;
    const apikeySha = Crypto.SHA256(apikey).toString();
    return apikeySha + '..0..' + t + '..' + uuid;
}

function base64Encode(text) {
    return Crypto.enc.Base64.stringify(Crypto.enc.Utf8.parse(text));
}

function base64Decode(text) {
    return Crypto.enc.Utf8.stringify(Crypto.enc.Base64.parse(text));
}

function getUrlDir(link) {
    return link.replace(/\/[^\/?#]+(\?.*)?(#.*)?$/, '');
}

function guessContentType(u) {
    if (/\.m3u8($|\?)/i.test(u)) return 'application/vnd.apple.mpegurl';
    if (/\.vtt($|\?)/i.test(u))  return 'text/vtt';
    if (/\.ts($|\?)/i.test(u))   return 'video/MP2T';
    if (/\.(mp4|m4s|cmfa|cmfv)($|\?)/i.test(u)) return 'video/mp4';
    return 'application/octet-stream';
}

function looksLikeM3U8(txt) {
    return typeof txt === 'string' && /#EXTM3U/.test(txt);
}

function is404orError(data) {
    if (typeof data !== 'string') return false;
    const s = data.slice(0, 300);
    return /404 Not Found|403 Forbidden|openresty|nginx|<html|<!doctype/i.test(s);
}

function joinUrl(base, rel) {
    if (/^https?:\/\//i.test(rel)) return rel;
    if (rel.startsWith('/')) {
        const m = base.match(/^(https?:\/\/[^\/]+)/i);
        return (m ? m[1] : '') + rel;
    }
    return getUrlDir(base).replace(/\/+$/, '') + '/' + rel.replace(/^\.\/+/, '');
}

function _stripBOM(s) {
    return typeof s === 'string' ? s.replace(/^\uFEFF/, '') : s;
}

// ============== HTTP ==============
async function curl_post(url, postdata, headerArr) {
    const headers = headerArr.reduce((acc, h) => {
        const idx = h.indexOf(':');
        if (idx > 0) {
            acc[h.slice(0, idx).trim()] = h.slice(idx + 1).trim();
        }
        return acc;
    }, {});
    headers["Content-Type"] = "application/json";
    try {
        let res = await req(url, { method: 'post', headers, data: postdata });
        return res.content;
    } catch (error) {
        console.log('curl_post error:', error);
        throw error;
    }
}

async function curl_get(url) {
    const headers = {
        "User-Agent": "Lavf/58.12.100",
        "userid":    tokenInfo.client_id || "",
        "usertoken": tokenInfo.token     || "",
        "X-Api-key": xApiKey             || genXApiKey()
    };
    try {
        let res = await req(url, { headers });
        return res.content;
    } catch (error) {
        console.log('curl_get error:', error);
        throw error;
    }
}

async function curl_get2(url) {
    const headers = {
        "User-Agent": "Lavf/58.12.100",
        "userid":    tokenInfo.client_id || "",
        "usertoken": tokenInfo.token     || "",
        "X-Api-key": xApiKey             || genXApiKey()
    };
    try {
        let res = await req(url, { buffer: 2, headers });
        return res.content;
    } catch (error) {
        console.log('curl_get2 error:', error);
        throw error;
    }
}

function getCode(Method) {
    const now = Math.floor(Date.now() / 1000);
    const sign = Crypto.MD5(
        String(from) + String(key) + String(now) + String(Method) + String(device_id)
    ).toString();

    const vparams = {};
    if (tokenInfo.token && tokenInfo.client_id && tokenInfo.password) {
        vparams["client_id"] = tokenInfo.client_id;
        vparams["password"]  = tokenInfo.password;
        vparams["token"]     = tokenInfo.token;
    }
    vparams["device_id"] = device_id;
    vparams["hardware"]  = hardware;
    vparams["sn"]        = device_id;
    vparams["version"]   = version;

    return {
        method: Method,
        system: { from, sign, time: now, version: "V1" },
        params: vparams
    };
}

// ============== API Steps ==============
async function doStep_1_1_2() {
    console.log('[1-1-2] start');
    const header = ["User-Agent: okhttp/3.12.5"];
    const resp = await curl_post(api, getCode("1-1-2"), header);
    const obj = JSON.parse(resp);
    const data = obj?.data;

    if (!data?.server?.hosts?.length) throw new Error('[1-1-2] No server hosts');

    tokenInfo.token     = data.client.token;
    tokenInfo.server    = data.server.hosts[0].url;
    tokenInfo.client_id = data.client.client_id;
    tokenInfo.password  = data.client.password;

    const ttl = data.client?.expire || data.ttl || TOKEN_TTL_SEC;
    tokenInfo.expireTime = Date.now() + (ttl * 1000);

    console.log('[1-1-2] done. token=', tokenInfo.token?.slice(0, 16) + '...',
        'ttl=', ttl, 'expires_at=', new Date(tokenInfo.expireTime).toLocaleString());
}

async function doStep_1_1_3() {
    console.log('[1-1-3] start. current_token=', tokenInfo.token?.slice(0, 16) + '...');
    const header = ["User-Agent: okhttp/3.12.5"];
    const resp = await curl_post(api, getCode("1-1-3"), header);

    const obj = JSON.parse(resp);
    const data = obj?.data;

    if (data?.client?.token)           tokenInfo.token     = data.client.token;
    if (data?.client?.client_id)       tokenInfo.client_id = data.client.client_id;
    if (data?.client?.password)        tokenInfo.password  = data.client.password;
    if (data?.server?.hosts?.[0]?.url) tokenInfo.server    = data.server.hosts[0].url;

    const ttl = data?.client?.expire || data?.ttl || TOKEN_TTL_SEC;
    tokenInfo.expireTime = Date.now() + (ttl * 1000);

    // token 更新完畢，同步產生新的 xApiKey
    xApiKey = genXApiKey();

    console.log('[1-1-3] done. new_token=', tokenInfo.token?.slice(0, 16) + '...',
        'ttl=', ttl, 'expires_at=', new Date(tokenInfo.expireTime).toLocaleString(),
        'xApiKey=', xApiKey?.slice(0, 16) + '...');
}

async function doStep_1_1_4() {
    console.log('[1-1-4] start');
    const header = ["User-Agent: okhttp/3.12.5"];
    const resp = await curl_post(api, getCode("1-1-4"), header);
    const rCode = JSON.parse(resp);
    if (rCode.code == 1) throw new Error('[1-1-4] API returned error code 1');
    console.log('[1-1-4] done. items=', (rCode.data || []).length);
    return rCode;
}

// ============== 背景 Token 刷新 ==============
function startBgTokenRefresh() {
    if (bgTimerHandle !== null) {
        console.log('[bg] already running, skip');
        return;
    }

    const tick = async () => {
        try {
            await doStep_1_1_3();
        } catch (e) {
            console.log('[bg] 1-1-3 error:', e);
        }
        bgTimerHandle = setTimeout(tick, BG_INTERVAL_MS);
    };

    bgTimerHandle = setTimeout(tick, BG_INTERVAL_MS);
    console.log('[bg] scheduled. interval=', BG_INTERVAL_MS / 1000, 's');
}

// ============== getJson ==============
async function getJson(url) {
    let txt;
    try { txt = await curl_get(url); }
    catch (e) { console.log('[getJson] error:', e); return null; }

    const preview = ('' + txt).slice(0, 200);
    if (/Just a moment|cf_chl_opt|challenge-platform/i.test(preview)) {
        console.log('[getJson] Cloudflare challenge'); return null;
    }
    if (/<!doctype|<html/i.test(preview)) {
        console.log('[getJson] HTML error page'); return null;
    }
    try { return JSON.parse(_stripBOM(txt)); }
    catch (e) { console.log('[getJson] parse fail'); return null; }
}

// ============== init ==============
async function init(cfg) {
    if (cfg && typeof cfg === 'object') {
        siteKey  = cfg.skey  || cfg.siteKey  || '';
        siteType = cfg.stype || cfg.siteType || "3";
    } else {
        siteKey  = '';
        siteType = "3";
    }
    console.log('[init] siteKey=', siteKey, 'siteType=', siteType);

    startBgTokenRefresh();
}

// ============== live ==============
async function live() {
    if (liveCache !== null) {
        console.log('[live] cache hit');
        return liveCache;
    }

    console.log('[live] cache miss, building...');
    try {
        await doStep_1_1_2();
        await delay(STEP_DELAY_MS);
        await doStep_1_1_3();
        await delay(STEP_DELAY_MS);
        const rCode = await doStep_1_1_4();

        const js2Base = await js2Proxy(true, siteType, siteKey, 'smart/', {});

        const groups = new Map();
        const put = (cate, name, url) => {
            if (!groups.has(cate)) groups.set(cate, []);
            groups.get(cate).push({ name, url });
        };

        for (const v of rCode.data || []) {
            const ct = v.category || '未分組';
            if (v.url?.startsWith("http")) {
                put(ct, v.name, v.url);
            } else if (v.url) {
                put(ct, v.name, js2Base + base64Encode(tokenInfo.server + v.url));
            }
        }
        console.log('[live] list1 done. categories=',
            new Set((rCode.data || []).map(x => x.category)).size);

        const j2raw = await getJson(crapi);
        let list2 = [];
        if (j2raw && Array.isArray(j2raw.data))              list2 = j2raw.data;
        else if (Array.isArray(j2raw))                        list2 = j2raw;
        else if (j2raw && Array.isArray(j2raw.list))          list2 = j2raw.list;
        else if (j2raw?.items && Array.isArray(j2raw.items))  list2 = j2raw.items;

        let added = 0;
        for (const v of list2) {
            const ct   = v.category || v.group || v.type || v.cate || '未分組';
            const name = v.name     || v.title || v.channel || '未命名';
            const url  = v.url      || v.link  || v.play    || '';
            if (!url) continue;
            put(ct, name, js2Base + base64Encode(url));
            added++;
        }
        console.log('[live] list2 added=', added);

        let out = "";
        for (const [cate, items] of groups.entries()) {
            out += `${cate},#genre#\n`;
            for (const it of items) out += `${it.name},${it.url}\n`;
        }

        liveCache = out;
        console.log('[live] cached. groups=', groups.size);
        return liveCache;

    } catch (error) {
        console.log('[live] error:', error);
        return "";
    }
}

// ============== proxy ==============
async function proxy(segments, headers) {
    if (!segments || segments.length < 2) {
        return JSON.stringify({ code: 400, content: 'Invalid segments' });
    }

    const what = segments[0];
    const id   = base64Decode(segments[1]);

    if (what === 'smart') {
        try {
            let data = await curl_get(id);

            if (is404orError(data)) {
                console.log('[smart] 404 or error page, abort');
                return JSON.stringify({ code: 404, content: '404 Not Found' });
            }

            if (!looksLikeM3U8(data)) {
                console.log('[smart] invalid manifest, retry once');
                data = await curl_get(id);

                if (is404orError(data)) {
                    console.log('[smart] retry also 404, abort');
                    return JSON.stringify({ code: 404, content: '404 Not Found' });
                }
            }

            if (!looksLikeM3U8(data)) {
                return JSON.stringify({ code: 502, content: 'Bad manifest' });
            }

            const js2Sts = await js2Proxy(false, siteType, siteKey, 'sts/', {});
            const js2Smt = await js2Proxy(false, siteType, siteKey, 'smart/', {});

            let result = '';
            let tsCount = 0;

            data.split(/\r?\n/).forEach(raw => {
                const line = (raw || '').trim();
                if (line === '') { result += '\n'; return; }

                if (line.startsWith('#EXT-X-KEY') || line.startsWith('#EXT-X-SESSION-KEY')) {
                    const m = line.match(/URI="([^"]+)"/i);
                    result += m
                        ? line.replace(/URI="([^"]+)"/i, 'URI="' + js2Sts + base64Encode(joinUrl(id, m[1])) + '"') + '\n'
                        : line + '\n';
                    return;
                }
                if (line.startsWith('#EXT-X-MAP')) {
                    const m = line.match(/URI="([^"]+)"/i);
                    result += m
                        ? line.replace(/URI="([^"]+)"/i, 'URI="' + js2Sts + base64Encode(joinUrl(id, m[1])) + '"') + '\n'
                        : line + '\n';
                    return;
                }
                if (line.startsWith('#EXT-X-MEDIA') || line.startsWith('#EXT-X-I-FRAME-STREAM-INF')) {
                    const m = line.match(/URI="([^"]+)"/i);
                    result += m
                        ? line.replace(/URI="([^"]+)"/i, 'URI="' + js2Smt + base64Encode(joinUrl(id, m[1])) + '"') + '\n'
                        : line + '\n';
                    return;
                }
                if (line.startsWith('#')) { result += line + '\n'; return; }

                const full = joinUrl(id, line);
                if (/\.m3u8($|\?)/i.test(full)) {
                    result += js2Smt + base64Encode(full) + '\n';
                } else {
                    result += js2Sts + base64Encode(full) + '\n';
                    tsCount++;
                }
            });

            console.log('[smart] done. ts=', tsCount);
            return JSON.stringify({
                code: 200,
                content: result,
                headers: { 'Content-Type': 'application/vnd.apple.mpegurl' }
            });

        } catch (error) {
            console.log('[smart] error:', error);
            return JSON.stringify({ code: 500, content: 'Smart proxy error' });
        }

    } else if (what === 'sts') {
        try {
            let resp = await curl_get2(id);

            if (is404orError(resp)) {
                console.log('[sts] 404 or error page, abort');
                return JSON.stringify({ code: 404, content: '404 Not Found' });
            }

            let needRetry = false;
            if (typeof resp === 'string') {
                if (/606|403/i.test(resp.slice(0, 200))) needRetry = true;
            } else if (!resp || resp.length < MIN_BINARY_B64) {
                needRetry = true;
            }

            if (needRetry) {
                console.log('[sts] suspect blocked, retry once');
                resp = await curl_get2(id);

                if (is404orError(resp)) {
                    console.log('[sts] retry also 404, abort');
                    return JSON.stringify({ code: 404, content: '404 Not Found' });
                }
            }

            return JSON.stringify({
                code: 200,
                buffer: 2,
                content: resp,
                headers: { 'Content-Type': guessContentType(id) }
            });

        } catch (error) {
            console.log('[sts] error:', error);
            return JSON.stringify({ code: 500, content: 'TS segment fetch failed' });
        }
    }

    return JSON.stringify({ code: 500, content: 'Unknown error' });
}

export function __jsEvalReturn() {
    return { init, live, proxy }
}