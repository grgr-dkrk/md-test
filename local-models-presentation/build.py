"""Render the original Markdown without editorial changes; package browser media."""
from pathlib import Path
from html import escape
import base64
import hashlib
import json
import mimetypes
import re
import shutil
import subprocess
import zipfile
import markdown
import imageio_ffmpeg

PROJECT = Path(__file__).resolve().parent
SOURCE = PROJECT.parent
DIST = PROJECT / 'dist'
ASSETS = DIST / 'assets'
ASSETS.mkdir(parents=True, exist_ok=True)
source = SOURCE / '最近ローカルでよく使っているモデル.md'
original = source.read_text()
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
embeds = list(dict.fromkeys(re.findall(r'!\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', original)))
audio_links = re.findall(r'(?<!!)\[([^\]]+)\]\(([^)]+\.(?:flac|wav|mp3|m4a|mp4))\)', original, re.I)
linked_audio = list(dict.fromkeys(name for _, name in audio_links))
media_names = list(dict.fromkeys(embeds + linked_audio))
missing = [name for name in media_names if not (SOURCE / name).is_file()]
if missing:
    raise FileNotFoundError(', '.join(missing))

# Remove generated audio for samples removed from the Markdown since the last build.
previous_report = PROJECT / 'asset-report.json'
if previous_report.exists():
    previous = json.loads(previous_report.read_text())
    active_outputs = {entry['web_file'] for entry in previous.get('embedded', [])
                      if entry['name'] in media_names}
    for entry in previous.get('embedded', []):
        stale = ASSETS / entry['web_file']
        if entry['name'] not in embeds and stale.name not in active_outputs and stale.exists():
            stale.unlink()

# Use ASCII URLs for hosted files; the standalone document embeds all its media.
media = {}
for name in embeds:
    src = SOURCE / name
    stem = hashlib.sha256(name.encode()).hexdigest()[:12]
    suffix = src.suffix.lower()
    if suffix in {'.mov', '.mp4'}:
        target = ASSETS / (stem + '.mp4')
        if not target.exists() or target.stat().st_mtime < src.stat().st_mtime:
            subprocess.run([ffmpeg, '-v', 'error', '-y', '-i', str(src), '-map', '0:v:0', '-map', '0:a?', '-c:v', 'copy', '-c:a', 'aac', '-movflags', '+faststart', str(target)], check=True)
        poster = ASSETS / (stem + '.jpg')
        if not poster.exists() or poster.stat().st_mtime < src.stat().st_mtime:
            subprocess.run([ffmpeg, '-v', 'error', '-y', '-i', str(target), '-frames:v', '1', '-vf', 'scale=960:-2', '-q:v', '3', str(poster)], check=True)
        media[name] = ('video', target, poster)
    elif suffix == '.flac':
        target = ASSETS / (stem + '.m4a')
        if not target.exists() or target.stat().st_mtime < src.stat().st_mtime:
            subprocess.run([ffmpeg, '-v', 'error', '-y', '-i', str(src), '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', str(target)], check=True)
        media[name] = ('audio', target, None)
    else:
        target = ASSETS / (stem + suffix)
        shutil.copy2(src, target)
        media[name] = ('image', target, None)
for name in linked_audio:
    if name not in media:
        src = SOURCE / name
        target = ASSETS / (hashlib.sha256(name.encode()).hexdigest()[:12] + '.m4a')
        if not target.exists() or target.stat().st_mtime < src.stat().st_mtime:
            subprocess.run([ffmpeg, '-v', 'error', '-y', '-i', str(src), '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', str(target)], check=True)
        media[name] = ('audio', target, None)


def uri(path, standalone):
    if not standalone:
        return 'assets/' + path.name
    mime = {'.m4a': 'audio/mp4', '.mp4': 'video/mp4'}.get(path.suffix) or mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
    return 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode()


def render(standalone):
    figures = []
    def embed(match):
        name, width = match[1], match[2]
        kind, path, poster = media[name]
        url = uri(path, standalone)
        label = escape(name, quote=True)
        if kind == 'image':
            size = f' width="{int(width)}"' if width and width.isdigit() else ''
            tag = f'<img src="{url}" alt="{label}"{size}>'
        elif kind == 'video':
            tag = f'<video controls playsinline preload="metadata" poster="{uri(poster, standalone)}" aria-label="{label}" src="{url}">動画を再生できません。</video>'
        else:
            tag = f'<audio controls preload="metadata" aria-label="{label}" src="{url}">音声を再生できません。</audio>'
        figures.append(f'<figure>{tag}</figure>')
        return '\n\nMEDIAINSERT' + str(len(figures)-1) + '\n\n'
    prepared = re.sub(r'!\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', embed, original)
    def render_audio_link(match):
        label, name = match[1], match[2]
        _, path, _ = media[name]
        control = f'<figure class="linked-audio"><figcaption>{escape(label)}</figcaption><audio controls preload="metadata" aria-label="{escape(label, quote=True)}" src="{uri(path, standalone)}">音声を再生できません。</audio></figure>'
        figures.append(control)
        return '\n\nMEDIAINSERT' + str(len(figures)-1) + '\n\n'
    prepared = re.sub(r'(?<!!)\[([^\]]+)\]\(([^)]+\.(?:flac|wav|mp3|m4a|mp4))\)', render_audio_link, prepared, flags=re.I)
    # The source contains bare URLs. Link them without changing the visible text.
    prepared = re.sub(r'(?m)^(https?://\S+)\s*$', lambda m:'<' + m[1] + '>', prepared)
    body = markdown.markdown(prepared, extensions=['tables', 'fenced_code', 'nl2br'], tab_length=4)
    body = re.sub(r'~~(.+?)~~', r'<del>\1</del>', body)
    for i, figure in enumerate(figures):
        body = body.replace(f'<p>MEDIAINSERT{i}</p>', figure)
    # Keep the original captions and text, while presenting the two examples as a pair.
    body = re.sub(r'<p>一例<br\s*/?>\s*Qwen</p>', '<p>一例</p><p>Qwen</p>', body, count=1)
    def image_comparison(match):
        cards = re.findall(r'<p>([^<]+)</p>\s*(<figure>.*?</figure>)', match[2], re.S)
        content = ''.join(f'<div class="image-card"><p>{caption}</p>{figure}</div>'
                          for caption, figure in cards)
        return match[1] + '<div class="image-comparison">' + content + '</div>'
    body = re.sub(
        r'(<p>一例(?:<br\s*/?>\s*[^<]+)?</p>\s*)'
        r'(((?:<p>[^<]+</p>\s*<figure>.*?</figure>\s*){2,}))',
        image_comparison, body, count=1, flags=re.S)
    body = body.replace('OpenCode の無料のモデル', '<span class="free">OpenCode の無料のモデル</span>')
    body = body.replace('ChatGPT の Plus プラン（GPT-Image）', '<span class="paid">ChatGPT の Plus プラン（GPT-Image）</span>')
    body = body.replace('<table>', '<div class="table-scroll"><table>').replace('</table>', '</table></div>')
    return (PROJECT / 'template.html').read_text().replace('{{title}}', escape(source.stem)).replace('{{body}}', body)

(DIST / 'index.html').write_text(render(False))
standalone_path = SOURCE / (source.stem + '.html')
standalone_path.write_text(render(True))
shutil.copy2(source, DIST / 'source.md')
(DIST / '.nojekyll').touch()
# Preserve all supplied media in the downloadable package, including unreferenced recordings.
extensions = {'.mov', '.mp4', '.png', '.jpg', '.jpeg', '.webm', '.flac'}
files = sorted(p for p in SOURCE.iterdir() if p.is_file() and p.suffix.lower() in extensions)
for path in files:
    shutil.copy2(path, ASSETS / path.name)
report = {'source': source.name, 'standalone': standalone_path.name, 'missing': missing,
          'embedded': [{'name': name, 'web_file': entry[1].name} for name, entry in media.items()],
          'attachments': [{'name': p.name, 'bytes': p.stat().st_size} for p in files]}
(PROJECT / 'asset-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
with zipfile.ZipFile(PROJECT / 'presentation.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(DIST.rglob('*')):
        if path.is_file():
            archive.write(path, path.relative_to(DIST))
print(f'Standalone: {standalone_path} ({standalone_path.stat().st_size / 1024**2:.1f} MiB)')
print(f'Hosted: {DIST / "index.html"}')
print(f'{len(media)} embedded media; {len(files)} original attachments; no missing files')
