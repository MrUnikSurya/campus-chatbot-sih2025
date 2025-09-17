# save as scrape_university_pdfs.py
import os, time, csv, sqlite3, re
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

# pdf extraction
import pdfplumber  # pip install pdfplumber

BASE_URL = "https://www.uniraj.ac.in/index.php?mid=196"  # example circulars page
OUTPUT_CSV = "uniraj_pdfs.csv"
DB_FILE = "uniraj_logs.db"
HEADERS = {"User-Agent": "CampusChatbotBot/1.0 (+your-email@example.com)"}  # polite UA

# 1) helpers
def is_pdf_link(href):
    return href and href.lower().endswith(".pdf")

def safe_filename(url):
    p = urlparse(url).path
    name = os.path.basename(p)
    if not name:
        name = "file_" + str(abs(hash(url)))
    return re.sub(r'[^A-Za-z0-9_.-]', '_', name)

# 2) create DB
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS downloads (
      id INTEGER PRIMARY KEY,
      url TEXT UNIQUE,
      filename TEXT,
      downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      status TEXT,
      extracts TEXT
    );
    """)
    conn.commit()
    return conn

# 3) crawl page and find pdf links
def find_pdf_links(page_url):
    r = requests.get(page_url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a['href']
        if is_pdf_link(href) or ".pdf" in href.lower():
            full = urljoin(page_url, href)
            links.append(full)
    # deduplicate
    return list(dict.fromkeys(links))

# 4) download -> extract text
def download_and_extract(pdf_url, download_dir="pdfs"):
    os.makedirs(download_dir, exist_ok=True)
    filename = safe_filename(pdf_url)
    path = os.path.join(download_dir, filename)
    try:
        if not os.path.exists(path):
            resp = requests.get(pdf_url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            with open(path, "wb") as f:
                f.write(resp.content)
        # extract
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return filename, text[:200000]  # limit size
    except Exception as e:
        return filename, f"ERROR: {e}"

def main():
    conn = init_db()
    cur = conn.cursor()
    pdfs = find_pdf_links(BASE_URL)
    print(f"Found {len(pdfs)} pdf links.")
    with open(OUTPUT_CSV, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["url", "filename", "snippet"])
        for url in pdfs:
            print("Downloading:", url)
            fname, text = download_and_extract(url)
            writer.writerow([url, fname, (text[:500] if text else "")])
            status = "ok" if not text.startswith("ERROR") else "error"
            cur.execute("INSERT OR REPLACE INTO downloads (url, filename, status, extracts) VALUES (?, ?, ?, ?)",
                        (url, fname, status, (text[:10000] if text else "")))
            conn.commit()
            time.sleep(1.5)  # be polite
    conn.close()
    print("Done. CSV:", OUTPUT_CSV, "DB:", DB_FILE)

if __name__ == "__main__":
    main()
