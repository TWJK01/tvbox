var rule = {
    title: 'YOKAR',
    host: 'https://yokar.net',
    // 依據截圖分類：電影、動漫、戲劇（若點擊後網址路徑不同，可在此微調）
    url: '/fyclass?page=fypage',
    searchUrl: '/search?wd=**&page=fypage',
    searchable: 2,
    quickSearch: 0,
    filterable: 0,
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': 'https://yokar.net/'
    },
    timeout: 8000,
    class_name: '電影&動漫&戲劇',
    class_url: 'movie&anime&drama',
    play_parse: true,
    // 啟用網頁嗅探模式（針對 YouTube 播放）
    sniffer: 1,
    isVideo: 'http((?!http).){26,}?(youtube\\.com|youtu\\.be|googlevideo\\.com|m3u8|mp4)',
    lazy: `js:
        input = {
            jx: 0,
            url: input,
            parse: 1
        };
    `,
    limit: 20,
    double: false,
    // 使用通用 JS 邏輯抓取首頁所有帶有圖片的影片卡片，避免 CSS 選擇器寫死抓不到
    推薦: `js:
        var d = [];
        var html = request(input);
        var items = pdfa(html, 'body&&a:has(img)');
        items.forEach(function(it) {
            var href = pd(it, 'a&&href');
            var title = pdfh(it, 'a&&title') || pdfh(it, 'img&&alt') || pdfh(it, 'a&&Text');
            var pic = pd(it, 'img&&data-src') || pd(it, 'img&&data-original') || pd(it, 'img&&src');
            // 過濾掉 Logo 或無效短連結
            if (href && title && title.trim().length > 1 && href.indexOf('yokar.net') !== -1 && href !== 'https://yokar.net/') {
                d.push({
                    title: title.trim(),
                    pic_url: pic,
                    desc: 'YouTube',
                    url: href
                });
            }
        });
        setResult(d);
    `,
    // 分類列表同樣使用通用抓取邏輯
    一級: `js:
        var d = [];
        var html = request(input);
        var items = pdfa(html, 'body&&a:has(img)');
        items.forEach(function(it) {
            var href = pd(it, 'a&&href');
            var title = pdfh(it, 'a&&title') || pdfh(it, 'img&&alt') || pdfh(it, 'a&&Text');
            var pic = pd(it, 'img&&data-src') || pd(it, 'img&&data-original') || pd(it, 'img&&src');
            if (href && title && title.trim().length > 1 && href.indexOf('yokar.net') !== -1) {
                d.push({
                    title: title.trim(),
                    pic_url: pic,
                    desc: 'YouTube',
                    url: href
                });
            }
        });
        setResult(d);
    `,
    // 二級詳情頁：自動抓取頁面上的標題、封面與所有集數/播放連結
    二級: `js:
        var html = request(input);
        var title = pdfh(html, 'h1&&Text') || pdfh(html, 'title&&Text');
        var pic = pd(html, 'meta[property="og:image"]&&content') || pd(html, 'img&&src');
        var desc = pdfh(html, 'meta[property="og:description"]&&content') || '';
        
        var playUrls = [];
        // 尋找包含 play、watch、ep 或 youtube 的連結作為集數
        var links = pdfa(html, 'body&&a');
        links.forEach(function(a) {
            var h = pd(a, 'a&&href');
            var t = pdfh(a, 'a&&Text').trim();
            if (h && (h.indexOf('/play') !== -1 || h.indexOf('/watch') !== -1 || h.indexOf('youtube') !== -1 || h.indexOf('youtu.be') !== -1)) {
                playUrls.push((t || '正片') + '$' + h);
            }
        });
        
        // 如果詳情頁本身就是播放頁（沒有額外的集數按鈕），直接把當前網址當作播放連結
        if (playUrls.length === 0) {
            playUrls.push('立即播放$' + input);
        }
        
        VOD = {
            vod_name: title,
            vod_pic: pic,
            vod_content: desc,
            vod_play_from: 'YOKAR-YT',
            vod_play_url: playUrls.join('#')
        };
    `,
    搜索: '*'
};
