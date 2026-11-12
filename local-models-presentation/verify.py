from pathlib import Path
import re
from html.parser import HTMLParser
import markdown
from playwright.sync_api import sync_playwright

project = Path(__file__).resolve().parent
root = project.parent
source = root / '最近ローカルでよく使っているモデル.md'
class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []
    def handle_data(self, data):
        self.parts.append(data)
def plain(html):
    p = Text(); p.feed(html)
    return re.sub(r'\s+', '', ''.join(p.parts))
expected = markdown.markdown(re.sub(r'!\[\[[^\]]+\]\]', '', source.read_text()), extensions=['tables', 'fenced_code', 'nl2br'])
for path in [source.with_suffix('.html'), project / 'dist/index.html']:
    html = path.read_text()
    article = re.search(r'<article>(.*?)</article>', html, re.S)[1]
    article = re.sub(r'<figure>.*?</figure>', '', article, flags=re.S)
    assert plain(article) == plain(expected), 'Source text changed'
print('PASS: Both HTML outputs preserve the full original text and order')
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless=True)
    page = browser.new_page(viewport={'width':1280,'height':900})
    for path in [source.with_suffix('.html'), project / 'dist/index.html']:
        page.goto(path.as_uri(), wait_until='load')
        page.wait_for_function('Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)')
        assert page.locator('img').count() == 2
        for player in page.locator('video,audio').all():
            player.evaluate('async e => {e.muted=true; await e.play()}')
            page.wait_for_timeout(500)
            result = player.evaluate('e => ({time:e.currentTime,error:e.error?.message,ready:e.readyState,width:e.videoWidth})')
            assert not result.get('error') and result['time'] > 0, result
            player.evaluate('e => e.pause()')
        assert page.locator('video').count() == 4
        assert page.locator('audio').count() == 2
        print('PASS:', path.name, '2 images loaded; 4 videos and 2 audio tracks played')
    page.screenshot(path=str(project / 'document-desktop.png'))
    page.locator('figure').first.scroll_into_view_if_needed()
    page.screenshot(path=str(project / 'document-media.png'))
    page.set_viewport_size({'width':390,'height':844})
    page.evaluate('scrollTo(0,0)')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Mobile overflow'
    page.screenshot(path=str(project / 'document-mobile.png'))
    browser.close()
print('PASS: Mobile layout fits the viewport')
