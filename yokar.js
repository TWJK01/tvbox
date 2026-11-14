var rule = {
    title: 'YOKAR',
    host: 'https://yokar.net',
    url: '/fyclass?page=fypage',
    searchUrl: '/search?wd=**&page=fypage',
    searchable: 2,
    quickSearch: 0,
    filterable: 0,
    headers: {
        'User-Agent': 'PC_UA',
        'Referer': 'https://yokar.net/'
    },
    timeout: 5000,
    // 依據網站導覽列設定分類：電影、動漫、戲劇
    class_name: '電影&動漫&戲劇',
    class_url: 'movie&anime&drama',
    play_parse: true,
    // 啟用網頁嗅探（針對 YouTube 嵌入或播放頁面）
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
    // 首頁推薦列表解析（若網站結構不同，可微調 CSS 選擇器）
    推薦: 'a[href*="/detail/"],a[href*="/vod/"],a[href*="/video/"];a&&title||img&&alt;img&&data-src||img&&src;.remarks||.tag&&Text;a&&href',
    // 分類列表解析（列表容器;標題;圖片;副標題;詳情連結）
    一級: 'a[href*="/detail/"],a[href*="/vod/"],a[href*="/video/"];a&&title||img&&alt;img&&data-src||img&&src;.remarks||.tag&&Text;a&&href',
    // 詳情頁與播放集數解析
    二級: {
        title: 'h1&&Text',
        img: '.poster img&&src||meta[property="og:image"]&&content',
        desc: '.desc&&Text||.intro&&Text||meta[property="og:description"]&&content',
        content: '.content&&Text',
        tabs: 'js:TABS=["YOKAR-YT"]',
        lists: 'a[href*="/play/"],a[href*="/watch/"],a[href*="youtube"],a[href*="youtu.be"]'
    },
    // 搜尋結果解析（直接沿用一級列表規則）
    搜索: '*'
};
