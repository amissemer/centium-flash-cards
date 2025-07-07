# Requires: pip install translate beautifulsoup4
import os
import requests
import html
import sys
from dotenv import load_dotenv
try:
    from translate import Translator
except ImportError:
    # If not installed, pip install translate
    raise
from bs4 import BeautifulSoup, Tag

load_dotenv()

CENTIUM_TXT = os.path.join(os.path.dirname(__file__), 'centium.txt')
OUTPUT_HTML = os.path.join(os.path.dirname(__file__), 'centium.html')
IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY', 'YOUR_UNSPLASH_ACCESS_KEY')  # Replace or set env var

translator = Translator(to_lang="en", from_lang="fr")

# --- Utility: Download image and return local filename ---
def download_image(url, num, idx):
    if not os.path.exists(IMG_DIR):
        os.makedirs(IMG_DIR)
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; CentiumBot/1.0)'}
    ext = os.path.splitext(url.split('?')[0])[1].lower()
    if ext not in ['.png', '.jpg', '.jpeg', '.svg']:
        try:
            resp = requests.get(url, stream=True, timeout=10, headers=headers)
            ct = resp.headers.get('content-type', '')
            if 'svg' in ct:
                ext = '.svg'
            elif 'png' in ct:
                ext = '.png'
            elif 'jpeg' in ct or 'jpg' in ct:
                ext = '.jpg'
            else:
                ext = '.img'
        except Exception:
            ext = '.img'
    else:
        resp = requests.get(url, stream=True, timeout=10, headers=headers)
    fname = f"{num}_{idx}{ext}"
    fpath = os.path.join(IMG_DIR, fname)
    try:
        with open(fpath, 'wb') as f:
            for chunk in resp.iter_content(1024):
                f.write(chunk)
        return fname
    except Exception as e:
        print(f"Failed to save {url} as {fname}: {e}")
        return None

# --- Openclipart Scraper ---
def scrape_openclipart(word):
    url = f"https://openclipart.org/search/?query={word}"
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        artwork_divs = soup.find_all("div", class_="artwork")
        urls = []
        for artwork_div in artwork_divs[:3]:  # Get first 3 artwork divs
            thumb = artwork_div.find("img")
            if isinstance(thumb, Tag) and thumb.has_attr('src'):
                src = thumb['src']
                urls.append(f"https://openclipart.org{src}")
        return urls
    except Exception as e:
        print(f"Openclipart scrape error for '{word}': {e}")
    return []

# --- API Search Functions ---
def search_wikimedia(word):
    url = 'https://commons.wikimedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'imageinfo',
        'generator': 'search',
        'gsrsearch': f'{word} filemime:image/svg+xml',
        'gsrlimit': 3,
        'gsrnamespace': 6,  # Only search in the File namespace (images)
        'iiprop': 'url',
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        pages = data.get('query', {}).get('pages', {})
        urls = []
        limit=3
        for page in pages.values():
            if 'imageinfo' in page:
                urls.append(page['imageinfo'][0]['url'])
                if limit <= 0:
                    break
                limit -= 1
        return urls
    except Exception:
        pass
    return []

def search_unsplash(word):
    if not UNSPLASH_ACCESS_KEY or UNSPLASH_ACCESS_KEY == 'YOUR_UNSPLASH_ACCESS_KEY':
        return []
    url = 'https://api.unsplash.com/search/photos'
    headers = {'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'}
    params = {'query': word, 'per_page': 3}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=5)
        data = resp.json()
        results = data.get('results', [])
        return [r['urls']['small'] for r in results]
    except Exception:
        pass
    return []

def img_html(filenames, alt, label):
    if filenames:
        if not isinstance(filenames, list):
            filenames = [filenames]
        img_tags = []
        for fname in filenames:
            img_tags.append(f"<img src='./img/{fname}' width='128' alt='{html.escape(alt)} ({label})'>")
        return ''.join(img_tags)
    return ''

def main():
    # Parse args
    start = 0
    count = 10
    if len(sys.argv) > 1:
        try:
            start = int(sys.argv[1])
        except Exception:
            pass
    if len(sys.argv) > 2:
        try:
            count = int(sys.argv[2])
        except Exception:
            pass
    rows = []
    with open(CENTIUM_TXT, encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() and ':' in line]
        for i, line in enumerate(lines[start:start+count], start=start):
            num, word_full = line.split(':', 1)
            word_full = word_full.strip()  # This is the display value, keep parenthesis
            # For image search, use only the part before parenthesis
            word_search = word_full.split('(')[0].strip()
            try:
                word_en = translator.translate(word_search)
            except Exception:
                word_en = word_search  # fallback to original if translation fails
            print(f"Processing {num}: {word_full} (search: '{word_en}')")
            openclipart_urls = scrape_openclipart(word_en)
            wikimedia_urls = search_wikimedia(word_en)
            unsplash_urls = search_unsplash(word_en)
            # Download images and get local filenames
            all_imgs = []
            for src_list, label in zip([openclipart_urls, wikimedia_urls, unsplash_urls], ['Openclipart', 'Wikimedia', 'Unsplash']):
                local_filenames = []
                for idx, url in enumerate(src_list, 1):
                    fname = download_image(url, num, f"{label.lower()}_{idx}")
                    if fname:
                        local_filenames.append(fname)
                all_imgs.append(local_filenames)
            row = f"<tr><td>{num}</td><td>{html.escape(word_full)}</td>" \
                  f"<td>{img_html(all_imgs[0], word_full, 'Openclipart')}</td>" \
                  f"<td>{img_html(all_imgs[1], word_full, 'Wikimedia')}</td>" \
                  f"<td>{img_html(all_imgs[2], word_full, 'Unsplash')}</td></tr>"
            rows.append(row)
    html_out = f"""
    <html><head><meta charset='utf-8'><title>Centium Table</title></head>
    <body>
    <h1>Centium Table</h1>
    <table border='1' cellpadding='8' style='border-collapse:collapse;'>
      <tr><th>Number</th><th>Word</th><th>Openclipart</th><th>Wikimedia</th><th>Unsplash</th></tr>
      {''.join(rows)}
    </table>
    <p>Images from <a href='https://openclipart.org/'>Openclipart</a>, <a href='https://commons.wikimedia.org/'>Wikimedia Commons</a>, <a href='https://unsplash.com/'>Unsplash</a>. If a cell is empty, no image was found for that source. Search terms are translated to English for better results.</p>
    </body></html>
    """
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_out)
    print(f"Wrote {OUTPUT_HTML}")

if __name__ == '__main__':
    main()
