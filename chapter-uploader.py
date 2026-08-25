#!/usr/bin/env python3
from __future__ import annotations
import argparse
import html
import json
import mimetypes
import os
import re
import signal
import sys
import time
import urllib.parse
from datetime import datetime
from email.parser import BytesParser
from email.policy import default as email_policy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MAX_REQUEST = 180 * 1024 * 1024
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
START = "<!-- CHAPTER-PHOTOS:START -->"
END = "<!-- CHAPTER-PHOTOS:END -->"

def esc(s): return html.escape(str(s or ""), quote=True)

class ChapterPhotoServer(ThreadingHTTPServer):
    allow_reuse_address = True
    def __init__(self, addr, handler, site: Path):
        super().__init__(addr, handler)
        self.site = site.resolve()
        self.manifest_path = self.site / "chapter-photos.json"

def load_manifest(server):
    if not server.manifest_path.exists():
        raise RuntimeError("chapter-photos.json is missing")
    return json.loads(server.manifest_path.read_text(encoding="utf-8"))

def save_manifest(server, data):
    tmp = server.manifest_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(server.manifest_path)

def safe_name(name):
    stem = Path(name).stem
    ext = Path(name).suffix.lower()
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-_.") or "photo"
    return stem[:80] + ext

def within_site(site, rel):
    p = (site / rel).resolve()
    try:
        p.relative_to(site.resolve())
        return p
    except ValueError:
        raise ValueError("Unsafe path")

def update_home_cover(site: Path, slug: str, relpath: str):
    p = site / "index.html"
    text = p.read_text(encoding="utf-8")
    # Card images are marked by data-chapter-card-image.
    pat = re.compile(
        rf'(<img\b[^>]*data-chapter-card-image="{re.escape(slug)}"[^>]*\bsrc=")[^"]*(")',
        re.I,
    )
    text, n = pat.subn(rf'\1{relpath}\2', text, count=1)
    if n != 1:
        raise RuntimeError(f"Could not find homepage card image marker for {slug}")
    p.write_text(text, encoding="utf-8")

def update_page_cover(site: Path, slug: str, relpath: str, page: str):
    p = site / page
    text = p.read_text(encoding="utf-8")
    pat = re.compile(
        rf'(<img\b[^>]*data-chapter-cover="{re.escape(slug)}"[^>]*\bsrc=")[^"]*(")',
        re.I,
    )
    text, n = pat.subn(rf'\1{relpath}\2', text, count=1)
    if n != 1:
        raise RuntimeError(f"Could not find chapter hero marker in {page}")
    p.write_text(text, encoding="utf-8")

def rebuild_gallery(site: Path, slug: str, ch: dict):
    p = site / ch["page"]
    text = p.read_text(encoding="utf-8")
    photos = ch.get("photos", [])
    if photos:
        figures = []
        for item in photos:
            cap = item.get("caption", "").strip()
            figcap = f"<figcaption>{esc(cap)}</figcaption>" if cap else ""
            figures.append(
                f'<figure><img src="{esc(item["path"])}" alt="{esc(cap or ch["title"] + " photograph")}" loading="lazy">{figcap}</figure>'
            )
        block = f"""{START}
<section class="chapter-photo-archive" id="chapter-photo-archive">
  <header class="chapter-photo-heading">
    <p class="kicker">From the Photo Archive</p>
    <h2>More from {esc(ch["title"])}</h2>
    <p>Photographs added directly to this chapter’s visual record.</p>
  </header>
  <div class="chapter-photo-gallery">
    {''.join(figures)}
  </div>
</section>
{END}"""
    else:
        block = ""

    if START in text and END in text:
        text = re.sub(re.escape(START) + r".*?" + re.escape(END), block, text, flags=re.S)
    elif block:
        # Put the archive before the closing quote when possible, otherwise before </main>.
        pos = text.find('<section class="closing-quote')
        if pos < 0:
            pos = text.rfind("</main>")
        if pos < 0:
            raise RuntimeError(f"Could not find insertion point in {ch['page']}")
        text = text[:pos] + block + "\n\n" + text[pos:]
    p.write_text(text, encoding="utf-8")

def page_html(server, message=""):
    data = load_manifest(server)
    cards = []
    for slug, ch in data["chapters"].items():
        cover = ch.get("cover") or ch.get("default_cover")
        photos = ch.get("photos", [])
        preview = f'<img src="/file/{urllib.parse.quote(cover)}" alt="">' if cover else ""
        photo_rows = ""
        for i, item in enumerate(photos[-12:][::-1]):
            photo_rows += f"""
            <div class="photo-row">
              <img src="/file/{urllib.parse.quote(item['path'])}" alt="">
              <div><strong>{esc(Path(item['path']).name)}</strong><small>{esc(item.get('caption',''))}</small></div>
              <form method="post" action="/set-cover"><input type="hidden" name="chapter" value="{esc(slug)}"><input type="hidden" name="path" value="{esc(item['path'])}"><button type="submit">Use as cover</button></form>
              <form method="post" action="/delete" onsubmit="return confirm('Remove this photo from the chapter?')"><input type="hidden" name="chapter" value="{esc(slug)}"><input type="hidden" name="path" value="{esc(item['path'])}"><button class="danger" type="submit">Remove</button></form>
            </div>"""
        cards.append(f"""
        <section class="chapter">
          <div class="chapter-head">
            {preview}
            <div><span>{esc(ch['number'])}</span><h2>{esc(ch['title'])}</h2><p>{esc(ch['description'])}</p><a href="http://localhost:5600/{esc(ch['page'])}" target="_blank">Open chapter ↗</a></div>
          </div>
          <form class="upload" method="post" action="/upload" enctype="multipart/form-data">
            <input type="hidden" name="chapter" value="{esc(slug)}">
            <label>Choose photographs<input type="file" name="photos" accept="image/jpeg,image/png,image/webp,image/gif" multiple required></label>
            <label>Caption / note for this batch<input type="text" name="caption" placeholder="Optional"></label>
            <label class="check"><input type="checkbox" name="set_cover" value="1" checked> Make the first photo the chapter cover too</label>
            <button type="submit">Add photos to {esc(ch['title'])}</button>
          </form>
          <div class="existing">{photo_rows or '<p class="empty">No uploader-added photographs yet.</p>'}</div>
        </section>""")
    msg = f'<div class="notice">{esc(message)}</div>' if message else ""
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Chapter Photo Uploader · Boulder Gardens</title>
<style>
:root{{--paper:#f7f1e2;--paper2:#eee2c6;--ink:#303229;--green:#596246;--clay:#a9573e;--line:#c4ad82}}
*{{box-sizing:border-box}} body{{margin:0;background:#d8cdb1;color:var(--ink);font:16px/1.45 Georgia,serif}}
header{{padding:2.2rem clamp(1rem,5vw,4rem);background:var(--paper);border-bottom:1px solid var(--line)}}
header h1{{font-size:clamp(2.3rem,5vw,4rem);margin:.2rem 0}} header p{{max-width:850px}}
main{{max-width:1450px;margin:auto;padding:2rem clamp(1rem,4vw,3rem) 5rem}}
.notice{{background:#e9f0df;border:1px solid #9cac88;padding:1rem;margin-bottom:1.5rem}}
.chapter{{background:var(--paper);border:1px solid var(--line);padding:1rem;margin:0 0 1.4rem;box-shadow:7px 7px 0 rgba(80,60,30,.08)}}
.chapter-head{{display:grid;grid-template-columns:220px 1fr;gap:1.3rem;align-items:center}}
.chapter-head img{{width:100%;height:150px;object-fit:cover;border:6px solid #fff}}
.chapter-head span{{color:var(--clay);font:700 .75rem Arial;letter-spacing:.15em}} h2{{font-size:2rem;margin:.15rem 0}} a{{color:var(--clay)}}
.upload{{display:grid;grid-template-columns:1.4fr 1.2fr auto auto;gap:.8rem;align-items:end;margin-top:1rem;padding-top:1rem;border-top:1px solid #ddd0b4}}
label{{font:700 .75rem Arial;letter-spacing:.03em}} input[type=file],input[type=text]{{display:block;width:100%;margin-top:.35rem;padding:.7rem;background:#fff;border:1px solid #b6a47d}}
.check{{display:flex;align-items:center;gap:.45rem;padding-bottom:.7rem;max-width:230px}} .check input{{width:18px;height:18px}}
button{{border:0;background:var(--green);color:white;padding:.78rem 1rem;font-weight:800;cursor:pointer}} button.danger{{background:#8e4c3a}}
.existing{{margin-top:.9rem}} .photo-row{{display:grid;grid-template-columns:80px 1fr auto auto;gap:.7rem;align-items:center;border-top:1px solid #dfd3b8;padding:.55rem 0}}
.photo-row img{{width:80px;height:60px;object-fit:cover}} .photo-row small{{display:block;color:#716d63}} .empty{{color:#777;font-style:italic}}
@media(max-width:800px){{.chapter-head{{grid-template-columns:1fr}}.chapter-head img{{height:220px}}.upload{{grid-template-columns:1fr}}.photo-row{{grid-template-columns:70px 1fr}}.photo-row form{{grid-column:auto}}}}
</style></head>
<body><header><p style="color:var(--clay);font-family:cursive">Boulder Gardens Fieldstation</p><h1>Chapter Photo Uploader</h1><p>A separate website tool for <strong>Chapters from the Land</strong>. It writes only to the public website folder; it does not use or modify the FieldStation app or its database.</p><p><a href="http://localhost:5600/" target="_blank">Open Boulder Gardens website ↗</a></p></header>
<main>{msg}{''.join(cards)}</main></body></html>"""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))

    def send_html(self, text, status=200):
        raw = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def redirect(self, msg=""):
        loc = "/"
        if msg: loc += "?" + urllib.parse.urlencode({"message": msg})
        self.send_response(303)
        self.send_header("Location", loc)
        self.end_headers()

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/":
            q = urllib.parse.parse_qs(u.query)
            self.send_html(page_html(self.server, q.get("message", [""])[0]))
            return
        if u.path.startswith("/file/"):
            rel = urllib.parse.unquote(u.path[len("/file/"):])
            try:
                p = within_site(self.server.site, rel)
                if not p.is_file(): raise FileNotFoundError
                raw = p.read_bytes()
                ctype = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(raw)))
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(raw)
            except Exception:
                self.send_error(404)
            return
        self.send_error(404)

    def read_form(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length > MAX_REQUEST: raise ValueError("Upload too large")
        ctype = self.headers.get("Content-Type", "")
        raw = self.rfile.read(length)
        if ctype.startswith("multipart/form-data"):
            msg = BytesParser(policy=email_policy).parsebytes(
                f"Content-Type: {ctype}\r\nMIME-Version: 1.0\r\n\r\n".encode() + raw
            )
            fields, files = {}, []
            for part in msg.iter_parts():
                name = part.get_param("name", header="content-disposition")
                filename = part.get_filename()
                if not name: continue
                payload = part.get_payload(decode=True) or b""
                if filename:
                    files.append({"field": name, "filename": filename, "data": payload, "ctype": part.get_content_type()})
                else:
                    fields[name] = payload.decode("utf-8", errors="replace")
            return fields, files
        fields = {k:v[-1] for k,v in urllib.parse.parse_qs(raw.decode(), keep_blank_values=True).items()}
        return fields, []

    def do_POST(self):
        try:
            fields, files = self.read_form()
            data = load_manifest(self.server)
            slug = fields.get("chapter", "")
            if slug not in data["chapters"]: raise ValueError("Unknown chapter")
            ch = data["chapters"][slug]

            if self.path == "/upload":
                chosen = [f for f in files if f["field"] == "photos"]
                if not chosen: raise ValueError("No photographs selected")
                caption = fields.get("caption", "").strip()
                folder_rel = f"images/chapters/{slug}"
                folder = within_site(self.server.site, folder_rel)
                folder.mkdir(parents=True, exist_ok=True)
                stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                stored = []
                for n, f in enumerate(chosen, 1):
                    name = safe_name(f["filename"])
                    ext = Path(name).suffix.lower()
                    if ext not in ALLOWED_EXTS: raise ValueError(f"Unsupported image type: {ext}")
                    target_name = f"{stamp}-{n:02d}-{name}"
                    target = folder / target_name
                    target.write_bytes(f["data"])
                    rel = f"{folder_rel}/{target_name}"
                    item = {"path": rel, "caption": caption, "uploaded_at": datetime.now().astimezone().isoformat(timespec="seconds")}
                    ch.setdefault("photos", []).append(item)
                    stored.append(rel)
                if fields.get("set_cover") == "1" and stored:
                    ch["cover"] = stored[0]
                    update_home_cover(self.server.site, slug, stored[0])
                    update_page_cover(self.server.site, slug, stored[0], ch["page"])
                rebuild_gallery(self.server.site, slug, ch)
                save_manifest(self.server, data)
                self.redirect(f"Added {len(stored)} photo{'s' if len(stored)!=1 else ''} to {ch['title']}.")
                return

            if self.path == "/set-cover":
                rel = fields.get("path", "")
                if not any(x.get("path") == rel for x in ch.get("photos", [])): raise ValueError("Photo is not in this chapter")
                ch["cover"] = rel
                update_home_cover(self.server.site, slug, rel)
                update_page_cover(self.server.site, slug, rel, ch["page"])
                save_manifest(self.server, data)
                self.redirect(f"Updated {ch['title']} cover.")
                return

            if self.path == "/delete":
                rel = fields.get("path", "")
                photos = ch.get("photos", [])
                ch["photos"] = [x for x in photos if x.get("path") != rel]
                try:
                    p = within_site(self.server.site, rel)
                    if p.is_file(): p.unlink()
                except Exception:
                    pass
                if ch.get("cover") == rel:
                    ch["cover"] = ch["photos"][0]["path"] if ch["photos"] else ch["default_cover"]
                    update_home_cover(self.server.site, slug, ch["cover"])
                    update_page_cover(self.server.site, slug, ch["cover"], ch["page"])
                rebuild_gallery(self.server.site, slug, ch)
                save_manifest(self.server, data)
                self.redirect(f"Removed photo from {ch['title']}.")
                return

            self.send_error(404)
        except Exception as e:
            self.send_html(page_html(self.server, f"Error: {e}"), 400)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--port", type=int, default=5601)
    args = ap.parse_args()
    site = Path(args.site).expanduser().resolve()
    server = ChapterPhotoServer(("127.0.0.1", args.port), Handler, site)
    print(f"Chapter Photo Uploader: http://localhost:{args.port}/")
    print(f"Website: {site}")
    server.serve_forever()

if __name__ == "__main__":
    main()
