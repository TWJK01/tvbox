import { Crypto } from 'assets://js/lib/cat.js'

let api = '' //API 
let device_id = "" // 就Mac
let hardware = '' //硬體資訊
let version = '' //版本
let from = '' //appID
let key = '' //各app對應的key

let siteKey = '';
let siteType = "3";

// Token信息和过期时间管理
let tokenInfo = {
    token: null,
    server: null,
    client_id: null,
    password: null,
    expireTime: 0  // token过期时间戳
};

// ============== 函数 ==============
function base64Encode(text) {
    return Crypto.enc.Base64.stringify(Crypto.enc.Utf8.parse(text));
}

function base64Decode(text) {
    return Crypto.enc.Utf8.stringify(Crypto.enc.Base64.parse(text));
}


function getUrlDir(link) {
    // 去掉末尾的 / 或 文件名部分
    return link.replace(/\/[^\/?#]+(\?.*)?(#.*)?$/, '');
}

async function curl_post(url, postdata, headerArr) {
    const headers = headerArr.reduce((acc, h) => {
        let [k, v] = h.split(/:\s*/)
        acc[k] = v
        return acc
    }, {})
    headers["Content-Type"] = "application/json"
    
    try {
        let res = await req(url, {
            method: 'post',
            headers,
            data: postdata
        })
        return res.content
    } catch (error) {
        console.log('curl_post error:', error);
        throw error;
    }
}

async function curl_get(url) {
    const headers = {
        "User-Agent": "Lavf/58.12.100",
        "Userid": tokenInfo.client_id || "",
        "Usertoken": tokenInfo.token || ""
    }
    
    try {
        let res = await req(url, { headers })
        return res.content
    } catch (error) {
        console.log('curl_get error:', error);
        throw error;
    }
}

async function curl_get2(url) {
    const headers = {
        "User-Agent": "Lavf/58.12.100",
        "Userid": tokenInfo.client_id || "",
        "Usertoken": tokenInfo.token || ""
    }
    
    try {
        let res = await req(url, { buffer: 2, headers })
        return res.content
    } catch (error) {
        console.log('curl_get2 error:', error);
        throw error;
    }
}

function getCode(Method) {
    // 以 PHP 相同順序組字串: appid + secret + time + method + sn
    const now = Math.floor(Date.now() / 1000);
    const sign = Crypto.MD5(
        String(from) + String(key) + String(now) + String(Method) + String(device_id)
    ).toString();

    const vparams = {};
    if (tokenInfo.token) {
        vparams["client_id"] = tokenInfo.client_id;
        vparams["password"] = tokenInfo.password;
        vparams["token"] = tokenInfo.token;
    }
    vparams["device_id"] = device_id;
    vparams["hardware"] = hardware;
    vparams["sn"] = device_id;
    vparams["version"] = version;

    const vSys = {
        from,
        sign,
        time: now,
        version: "V1"
    };
    const vArr = {
        method: Method,
        system: vSys,
        params: vparams
    };
    return vArr;
}

// 检查token是否即将过期（850秒后过期）
function isTokenExpiring() {
    return Date.now() >= tokenInfo.expireTime;
}

// 刷新token信息
async function refreshToken() {
    console.log('Refreshing token...');
    
    try {
        const header = ["User-Agent: okhttp/3.12.5"]
        let resp1 = await curl_post(api, getCode("1-1-2"), header)
        let obj1 = JSON.parse(resp1).data
        
        if (!obj1?.server?.hosts || obj1.server.hosts.length === 0) {
            throw new Error('No server hosts available');
        }
        
        tokenInfo.token = obj1.client.token;
        tokenInfo.server = obj1.server.hosts[0].url;
        tokenInfo.client_id = obj1.client.client_id;
        tokenInfo.password = obj1.client.password;
        tokenInfo.expireTime = Date.now() + (850 * 1000); // 850秒后过期
        
        if (!tokenInfo.token || !tokenInfo.server) {
            throw new Error('Invalid token or server');
        }
        
        console.log('Token refreshed successfully. Expires at:', new Date(tokenInfo.expireTime).toLocaleString());
        return tokenInfo;
    } catch (error) {
        console.log('Refresh token error:', error);
        throw error;
    }
}

// 获取有效的token信息
async function getValidTokenInfo() {
    // 如果没有token或者即将过期，则刷新
    if (!tokenInfo.token || isTokenExpiring()) {
        await refreshToken();
    }
    
    return tokenInfo;
}

// ============== init函数 ==============
async function init(cfg) {
    if (cfg && typeof cfg === 'object') {
        siteKey = cfg.skey || cfg.siteKey || '';
        siteType = cfg.stype || cfg.siteType || "3";
    } else {
        console.warn('Invalid config passed to init:', cfg);
        siteKey = '';
        siteType = "3";
    }
    
    console.log('Config initialized:', { siteKey, siteType });
}

async function live() {
    console.log('Live function started. Config:', { siteKey, siteType });
    
    try {
        // 获取有效token信息
        await getValidTokenInfo();
        
        const header = ["User-Agent: okhttp/3.12.5"]
        
        // 验证账号
        await curl_post(api, getCode("1-1-3"), header)
        
        // 拉取列表
        let resp3 = await curl_post(api, getCode("1-1-4"), header)
        let rCode = JSON.parse(resp3)
        
        if (rCode.code == 1) {
            console.log('API returned error code 1');
            return "";
        }

        console.log('Getting js2Proxy with params:', { siteType, siteKey });
        const js2Base = await js2Proxy(true, siteType, siteKey, 'smart/', {})
        
        let cc = ""
        let cate = [...new Set(rCode.data.map(v => v.category))]
        
        cate.forEach(ct => {
            cc += ct + ",#genre#\n"
            rCode.data.forEach(v => {
                if (v.category === ct) {
                    if (v.url.startsWith("http")) {
                        cc += v.name + "," + v.url + "\n"
                    } else {
                        cc += v.name + "," + js2Base + base64Encode(tokenInfo.server + v.url) + "\n"
                    }
                }
            })
        })
        
        console.log('Live list generated successfully. Categories:', cate.length);
        return cc
    } catch (error) {
        console.log('Live function error:', error);
        return "";
    }
}

async function proxy(segments, headers) {
    if (!segments || segments.length < 2) {
        return JSON.stringify({
            code: 400,
            content: 'Invalid segments',
        })
    }
    
    let what = segments[0]
    let id = base64Decode(segments[1]);
    
    console.log('Proxy called with:', { what, idLength: id.length });

    if (what === 'smart') {
        try {
            await getValidTokenInfo();
            
            console.log('Fetching M3U8 from:', id);
            const data = await curl_get(id)
            
            if (data && data.includes("EXTM3U")) {
                let dir = getUrlDir(id);
                console.log('M3U8 directory:', dir);
                
                const js2B = await js2Proxy(false, siteType, siteKey, 'sts/', {})
                let result = ''
                let tsCount = 0;
                
                data.split("\n").forEach(v => {
                    if (v.includes(".ts")) {
                        let ts = js2B + base64Encode(dir + "/" + v)
                        result += `${ts}\n`
                        tsCount++;
                    } else if (v !== '') {
                        result += `${v}\n`
                    }
                })
                
                console.log('M3U8 processed successfully. TS segments:', tsCount);
                return JSON.stringify({
                    code: 200,
                    content: result,
                    headers: {
                        'Content-Type': 'application/vnd.apple.mpegurl',
                    }
                })
            } else {
                console.log('Invalid M3U8 response or empty data');
            }
        } catch (error) {
            console.log('Proxy smart error:', error);
        }
    } else if (what === "sts") {
        try {
            await getValidTokenInfo();
            
            let turl = id
            console.log('Fetching TS segment:', { 
                url: turl.substring(0, 100) + '...', 
                fullLength: turl.length 
            });
            
            const resp = await curl_get2(turl)
            
            console.log('TS segment fetched successfully. Size:', resp ? resp.length : 0);
            return JSON.stringify({
                code: 200,
                buffer: 2,
                content: resp,
                headers: {
                    'Content-Type': 'video/MP2T',
                },
            });
        } catch (error) {
            console.log('Proxy sts error:', error);
            return JSON.stringify({
                code: 500,
                content: 'TS segment fetch failed',
            })
        }
    }

    console.log('Unknown proxy type or error occurred');
    return JSON.stringify({
        code: 500,
        content: 'Unknown error',
    })
}

export function __jsEvalReturn() {
    return {
        init,
        live,
        proxy
    }
}