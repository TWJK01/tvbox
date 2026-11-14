#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOKAR -> TVBox JSON bridge (public-page / authorized-source edition)

What it does:
- Uses a real browser (Playwright) to read publicly visible YOKAR pages.
- Collects movie/anime/drama cards and their public detail-page URLs.
- Visits detail pages and records YouTube watch/embed URLs that are openly exposed.
- Serves a MacCMS-style JSON API for TVBox.
- Does NOT log in, defeat CAPTCHA, bypass DRM, or extract protected media streams.

Important:
YOKAR is JavaScript-rendered. Its live DOM/API may change. This generic crawler
uses conservative card/link heuristics; inspect /debug after the first run and
adjust CARD_SELECTOR / DETAIL_LINK_SELECTOR if the site changes.
"""

import asyncio
import json
import logging
import os
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import uvicorn

BASE = "https://yokar.net"
DATA_FILE = Path("yokar_tvbox_data.json")
CATEGORIES = {
    "電影": "/zh-TW/browse/movie/",
    "動漫": "/zh-TW/browse/anime/",
    "戲劇": "/zh-TW/browse/drama/",
    "全部": "/zh-TW/browse/",
}
HEADLESS = os.getenv("HEADLESS", "1") != "0"
MAX_DETAIL_PAGES = int(os.getenv("MAX_DETAIL_PAGES", "300"))
SCROLL_ROUNDS = int(os.getenv("SCROLL_ROUNDS", "8"))
WAIT_MS = int(os.getenv("WAIT_MS", "1800"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("yokar")

# Optional CSS overrides. Example:
# CARD_SELECTOR='article' DETAIL_LINK_SELECTOR='a[href*="/title/"]' python yokar_tvbox.py crawl
CARD_SELECTOR = os.getenv("CARD_SELECTOR", "").strip()
DETAIL_LINK_SELECTOR = os.getenv("DETAIL_LINK_SELECTOR", "").strip()

def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()

def canonical(url):
    if not url:
        return ""
    return url.split("#", 1)[0]

def youtube_watch_url(url):
    """Return a canonical public YouTube watch URL; do not resolve media streams."""
    try:
        p = urlparse(url)
        host = (p.hostname or "").lower()
        if host in ("youtu.be", "www.youtu.be"):
            vid = p.path.strip("/").split("/")[0]
        elif host.endswith("youtube.com") or host.endswith("youtube-nocookie.com"):
            q = parse_qs(p.query)
            vid = (q.get("v") or [""])[0]
            if not vid and p.path.startswith("/embed/"):
                vid = p.path.split("/embed/", 1)[1].split("/", 1)[0]
            if not vid and p.path.startswith("/shorts/"):
                vid = p.path.split("/shorts/", 1)[1].split("/", 1)[0]
        else:
            return ""
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", vid or ""):
            return "https://www.youtube.com/watch?v=" + vid
    except Exception:
        pass
    return ""

async def scroll_page(page):
    for _ in range(SCROLL_ROUNDS):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(WAIT_MS // 2)
    await page.evaluate("window.scrollTo(0, 0)")

async def collect_cards(page, category):
    """Collect visible card-like anchors with conservative DOM heuristics."""
    selector = CARD_SELECTOR or "article, li, [class*='card'], [class*='item'], [class*='poster']"
    link_selector = DETAIL_LINK_SELECTOR or "a[href]"
    rows = await page.evaluate(
        """({selector, linkSelector, category, base}) => {
          const out = [];
          const seen = new Set();
          const norm = s => (s || '').replace(/\\s+/g, ' ').trim();
          document.querySelectorAll(selector).forEach(card => {
            const a = card.querySelector(linkSelector);
            if (!a) return;
            const href = a.href || '';
            if (!href.startsWith(base) || href.includes('/browse/')) return;
            const titleNode = card.querySelector('h1,h2,h3,h4,[class*="title"],[title]');
            const img = card.querySelector('img');
            const title = norm(titleNode?.innerText || a.getAttribute('title') || img?.alt || a.innerText);
            if (!title || title.length < 2 || title.length > 180) return;
            const key = href + '|' + title;
            if (seen.has(key)) return;
            seen.add(key);
            out.push({
              title,
              url: href,
              image: img?.currentSrc || img?.src || img?.getAttribute('data-src') || '',
              remarks: norm(card.innerText).slice(0, 180),
              category
            });
          });
          return out;
        }""",
        {"selector": selector, "linkSelector": link_selector, "category": category, "base": BASE}
    )
    # Fallback: links with useful visible text if card wrappers weren't detected.
    if not rows:
        rows = await page.evaluate(
            """base => [...document.querySelectorAll('a[href]')]
              .filter(a => a.href.startsWith(base) && !a.href.includes('/browse/'))
              .map(a => ({title:(a.innerText||a.title||'').trim(),url:a.href,
                image:a.querySelector('img')?.src || a.closest('div')?.querySelector('img')?.src || '',
                remarks:(a.closest('article,li,div')?.innerText||'').trim().slice(0,180)}))
              .filter(x => x.title.length >= 2 && x.title.length <= 180)""",
            BASE
        )
        for row in rows:
            row["category"] = category
    return rows

async def extract_detail(page, item):
    """Read only public page links/iframes; never inspect protected player internals."""
    result = dict(item)
    try:
        await page.goto(item["url"], wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(WAIT_MS)
        await scroll_page(page)
        detail = await page.evaluate("""() => {
          const text = (document.body?.innerText || '').replace(/\\s+/g,' ').trim();
          const links = [...document.querySelectorAll('a[href]')].map(a => a.href);
          const frames = [...document.querySelectorAll('iframe[src]')].map(x => x.src);
          const videos = [...document.querySelectorAll('video[src], video source[src]')]
            .map(x => x.src).filter(Boolean);
          const title = document.querySelector('h1,h2,[class*="title"]')?.innerText?.trim() || document.title;
          const description = document.querySelector('meta[name="description"]')?.content ||
            document.querySelector('[class*="description"],[class*="overview"]')?.innerText || '';
          return {text, links, frames, videos, title, description};
        }""")
        candidates = detail["links"] + detail["frames"]
        yt = []
        for u in candidates:
            w = youtube_watch_url(u)
            if w and w not in yt:
                yt.append(w)
        # A visible YouTube URL in page text is also accepted.
        for match in re.findall(r"https?://(?:www\\.)?(?:youtube\\.com/watch\\?v=[\\w-]{11}|youtu\\.be/[\\w-]{11})[^\\s\"'<>]*", detail["text"]):
            w = youtube_watch_url(match)
            if w and w not in yt:
                yt.append(w)
        result["title"] = clean_text(detail["title"]) or item["title"]
        result["content"] = clean_text(detail["description"])[:1200]
        result["episodes"] = yt
        result["playable"] = bool(yt)
        result["source_note"] = "YouTube 官方影片連結" if yt else "未找到公開 YouTube 播放連結；不自動抽取受保護串流"
    except PlaywrightTimeoutError:
        result["episodes"] = []
        result["playable"] = False
        result["source_note"] = "詳情頁逾時，待下次重試"
    except Exception as e:
        log.warning("detail failed %s: %s", item.get("url"), e)
        result["episodes"] = []
        result["playable"] = False
        result["source_note"] = "詳情頁讀取失敗"
    return result

async def crawl():
    items_by_url = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context(
            locale="zh-TW",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125 Safari/537.36"
        )
        page = await context.new_page()
        for category, path in CATEGORIES.items():
            if category == "全部":
                continue
            url = urljoin(BASE, path)
            log.info("讀取分類：%s %s", category, url)
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(WAIT_MS * 2)
                await scroll_page(page)
                rows = await collect_cards(page, category)
                log.info("%s 找到 %d 個候選項目", category, len(rows))
                for row in rows:
                    row["url"] = canonical(row["url"])
                    if row["url"] and row["url"] not in items_by_url:
                        items_by_url[row["url"]] = row
            except Exception as e:
                log.error("分類頁失敗 %s: %s", category, e)

        candidates = list(items_by_url.values())[:MAX_DETAIL_PAGES]
        detailed = []
        for i, item in enumerate(candidates, 1):
            log.info("詳情 %d/%d：%s", i, len(candidates), item["title"])
            detail = await extract_detail(page, item)
            detailed.append(detail)
            if i % 20 == 0:
                DATA_FILE.write_text(json.dumps(detailed, ensure_ascii=False, indent=2), encoding="utf-8")
        await browser.close()

    DATA_FILE.write_text(json.dumps(detailed, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("完成：%d 筆，已寫入 %s", len(detailed), DATA_FILE.resolve())

def load_data():
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

app = FastAPI(title="YOKAR TVBox API", version="1.0")

@app.get("/health")
def health():
    data = load_data()
    return {"ok": True, "items": len(data), "data_file": str(DATA_FILE)}

@app.get("/debug")
def debug():
    data = load_data()
    return {
        "count": len(data),
        "categories": {c: sum(1 for x in data if x.get("category") == c) for c in ("電影", "動漫", "戲劇")},
        "playable": sum(1 for x in data if x.get("playable")),
        "sample": data[:3]
    }

@app.get("/api.php/provide/vod/")
@app.get("/api.php/provide/vod")
def vod_api(
    ac: str = Query("list"),
    t: str = Query(""),
    pg: int = Query(1, ge=1),
    wd: str = Query(""),
    ids: str = Query(""),
    h: str = Query("")
):
    data = load_data()
    if ids:
        wanted = set(ids.split(","))
        selected = [x for x in data if str(x.get("id", x.get("url", ""))) in wanted]
        if not selected:
            selected = [x for x in data if x.get("url", "") in wanted]
        return JSONResponse({"code": 1, "msg": "ok", "page": 1, "pagecount": 1, "limit": len(selected), "total": len(selected), "list": [to_vod(x) for x in selected]})

    if wd:
        key = wd.casefold()
        data = [x for x in data if key in (x.get("title", "") + " " + x.get("content", "")).casefold()]
    if t:
        category = {"1": "電影", "2": "動漫", "3": "戲劇"}.get(t, t)
        data = [x for x in data if x.get("category") == category]

    limit = 30
    total = len(data)
    pagecount = max(1, (total + limit - 1) // limit)
    start = (pg - 1) * limit
    page_data = data[start:start + limit]
    return JSONResponse({
        "code": 1, "msg": "ok", "page": pg, "pagecount": pagecount,
        "limit": limit, "total": total, "list": [to_vod(x) for x in page_data]
    })

def to_vod(item):
    vid = item.get("url", "")
    episodes = item.get("episodes") or []
    play_url = "#".join(
        f"第{i+1}集${u}" for i, u in enumerate(episodes)
    )
    return {
        "vod_id": vid,
        "vod_name": item.get("title", ""),
        "vod_pic": item.get("image", ""),
        "vod_remarks": item.get("source_note", ""),
        "type_id": {"電影": "1", "動漫": "2", "戲劇": "3"}.get(item.get("category"), "0"),
        "type_name": item.get("category", ""),
        "vod_content": item.get("content", ""),
        "vod_play_from": "YouTube官方播放器" if episodes else "",
        "vod_play_url": play_url,
        "vod_play_note": "YouTube 連結需由 TVBox 的 YouTube 播放器/解析插件支援；此接口不提供破解後的 M3U8"
    }

if __name__ == "__main__":
    import sys
    command = sys.argv[1].lower() if len(sys.argv) > 1 else "serve"
    if command == "crawl":
        asyncio.run(crawl())
    elif command == "serve":
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "9978")))
    elif command == "all":
        asyncio.run(crawl())
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "9978")))
    else:
        print("用法：python yokar_tvbox.py crawl | serve | all")
