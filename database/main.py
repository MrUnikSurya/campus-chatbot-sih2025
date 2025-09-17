# import os
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# import pdfplumber
# import json

# # Base URL of notices page (adjust if different for 2025 notices)
# BASE_URL = "https://www.uniraj.ac.in/index.php?mid=196"   # Example: Sports/Notices
# YEAR = 2025
# SAVE_DIR = f"pdfs_{YEAR}"
# FAQ_JSON = f"faq_{YEAR}.json"

# os.makedirs(SAVE_DIR, exist_ok=True)

# def fetch_pdf_links(url):
#     """Scrape all PDF links from the notices page."""
#     r = requests.get(url)
#     soup = BeautifulSoup(r.text, "html.parser")
#     pdf_links = []
#     for a in soup.find_all("a", href=True):
#         if ".pdf" in a['href'].lower():
#             pdf_links.append(urljoin(url, a['href']))
#     return list(set(pdf_links))  # unique links

# def download_pdfs(links):
#     """Download all PDFs to local folder."""
#     files = []
#     for link in links:
#         filename = os.path.join(SAVE_DIR, os.path.basename(link))
#         try:
#             if not os.path.exists(filename):
#                 print(f"Downloading {link}")
#                 pdf_data = requests.get(link).content
#                 with open(filename, "wb") as f:
#                     f.write(pdf_data)
#             files.append(filename)
#         except Exception as e:
#             print(f"Error downloading {link}: {e}")
#     return files

# def extract_text_from_pdf(file):
#     """Extract text from a single PDF."""
#     text = ""
#     try:
#         with pdfplumber.open(file) as pdf:
#             for page in pdf.pages:
#                 page_text = page.extract_text()
#                 if page_text:
#                     text += page_text + "\n"
#     except Exception as e:
#         print(f"Error reading {file}: {e}")
#     return text.strip()

# def generate_faqs_from_text(text, filename):
#     """
#     Generate simple Q&A pairs from the notice text.
#     For hackathon demo, we only extract date, event, contact, etc.
#     """
#     faqs = []
#     lines = text.split("\n")
#     snippet = " ".join(lines[:5])  # first 5 lines as summary

#     # Example basic Q&A
#     if "Date" in text or "date" in text:
#         faqs.append({
#             "question": f"When is the event mentioned in {filename}?",
#             "answer": snippet
#         })
#     if "contact" in text.lower() or "email" in text.lower():
#         faqs.append({
#             "question": f"What is the contact information in {filename}?",
#             "answer": snippet
#         })
#     if "University" in text:
#         faqs.append({
#             "question": f"Which university released {filename} notice?",
#             "answer": "University of Rajasthan"
#         })

#     # fallback: always include one general Q/A
#     faqs.append({
#         "question": f"What is the summary of {filename}?",
#         "answer": snippet
#     })

#     return faqs

# def main():
#     print(f"Fetching PDFs for year {YEAR}...")
#     pdf_links = fetch_pdf_links(BASE_URL)
#     print(f"Found {len(pdf_links)} PDFs")

#     pdf_files = download_pdfs(pdf_links)

#     all_faqs = []
#     for pdf_file in pdf_files:
#         print(f"Extracting text from {pdf_file}")
#         text = extract_text_from_pdf(pdf_file)
#         if text:
#             faqs = generate_faqs_from_text(text, os.path.basename(pdf_file))
#             all_faqs.extend(faqs)

#     # Save to JSON
#     with open(FAQ_JSON, "w", encoding="utf-8") as f:
#         json.dump(all_faqs, f, indent=2, ensure_ascii=False)

#     print(f"FAQ JSON created: {FAQ_JSON} ✅")

# if __name__ == "__main__":
#     main()





# import os
# import re
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# import pdfplumber
# import json

# BASE_URL = "https://www.uniraj.ac.in/index.php?mid=196"  # Notices page
# SAVE_DIR = "pdfs_uniraj"
# FAQ_JSON = "faq_uniraj.json"

# os.makedirs(SAVE_DIR, exist_ok=True)

# def get_pdf_links(url, limit=5):
#     """Fetch first N PDF links from notices page."""
#     r = requests.get(url)
#     soup = BeautifulSoup(r.text, "html.parser")
#     pdf_links = []
#     for a in soup.find_all("a", href=True):
#         if ".pdf" in a['href'].lower():
#             full_url = urljoin(url, a['href'])
#             pdf_links.append(full_url)
#         if len(pdf_links) >= limit:
#             break
#     return pdf_links

# def download_pdfs(links):
#     """Download PDFs."""
#     files = []
#     for link in links:
#         filename = os.path.join(SAVE_DIR, os.path.basename(link))
#         if not os.path.exists(filename):
#             print(f"Downloading {link}")
#             pdf_data = requests.get(link).content
#             with open(filename, "wb") as f:
#                 f.write(pdf_data)
#         files.append(filename)
#     return files

# def extract_text(file):
#     """Extract full text from PDF."""
#     text = ""
#     with pdfplumber.open(file) as pdf:
#         for page in pdf.pages:
#             t = page.extract_text()
#             if t:
#                 text += t + "\n"
#     return text.strip()

# def generate_faqs(text, filename):
#     """Generate as many Q&As as possible from full PDF text."""
#     faqs = []

#     # Generic Q: summary
#     faqs.append({
#         "question": f"What is the notice in {filename} about?",
#         "answer": text
#     })

#     # Extract all dates
#     dates = re.findall(r"\d{1,2}[-./]\d{1,2}[-./]\d{2,4}", text)
#     for d in dates:
#         faqs.append({
#             "question": f"What is the important date mentioned in {filename}?",
#             "answer": d
#         })

#     # Extract emails
#     emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
#     for e in emails:
#         faqs.append({
#             "question": f"What is the email contact in {filename}?",
#             "answer": e
#         })

#     # Extract phone numbers
#     phones = re.findall(r"\b\d{3,4}[- ]?\d{6,7}\b", text)
#     for p in phones:
#         faqs.append({
#             "question": f"What is the phone number mentioned in {filename}?",
#             "answer": p
#         })

#     # If sports/event keyword
#     if "Sports" in text or "sport" in text.lower():
#         faqs.append({
#             "question": f"Which sports are mentioned in {filename}?",
#             "answer": text
#         })

#     return faqs

# def main():
#     pdf_links = get_pdf_links(BASE_URL, limit=5)
#     print(f"Found {len(pdf_links)} PDFs")

#     files = download_pdfs(pdf_links)

#     all_faqs = []
#     for file in files:
#         print(f"Extracting {file}")
#         text = extract_text(file)
#         if text:
#             faqs = generate_faqs(text, os.path.basename(file))
#             all_faqs.extend(faqs)

#     with open(FAQ_JSON, "w", encoding="utf-8") as f:
#         json.dump(all_faqs, f, indent=2, ensure_ascii=False)

#     print(f"FAQ JSON created with {len(all_faqs)} Q&As ✅")

# if __name__ == "__main__":
#     main()



# import os
# import re
# import fitz  # PyMuPDF
# import pdfplumber
# import pytesseract
# from PIL import Image
# import io
# import json

# SAVE_DIR = "pdfs_uniraj"
# FAQ_JSON = "faq_uniraj.json"
# os.makedirs(SAVE_DIR, exist_ok=True)

# # Path to tesseract (if needed)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# # -------------------------
# # STEP 1: Extract Text (without Poppler)
# # -------------------------
# def extract_text(file):
#     text = ""

#     # Try pdfplumber first (works if PDF is digital)
#     try:
#         with pdfplumber.open(file) as pdf:
#             for page in pdf.pages:
#                 t = page.extract_text()
#                 if t:
#                     text += t + "\n"
#     except Exception as e:
#         print(f"pdfplumber failed for {file}: {e}")

#     # If no text found, use OCR with PyMuPDF
#     if not text.strip():
#         print(f"Falling back to OCR for {file}")
#         doc = fitz.open(file)
#         for page in doc:
#             pix = page.get_pixmap()
#             img = Image.open(io.BytesIO(pix.tobytes("png")))
#             text += pytesseract.image_to_string(img, lang="hin+eng") + "\n"

#     return text.strip()

# # -------------------------
# # STEP 2: Generate FAQs
# # -------------------------
# def generate_faqs(text, filename):
#     faqs = []
#     faqs.append({
#         "question": f"{filename} नोटिस किस बारे में है?",
#         "answer": text
#     })

#     # Dates
#     dates = re.findall(r"\d{1,2}[-./]\d{1,2}[-./]\d{2,4}", text)
#     hindi_dates = re.findall(r"\d{1,2}\s?[अ-ह]+\s?\d{4}", text)
#     for d in dates + hindi_dates:
#         faqs.append({
#             "question": f"{filename} में महत्वपूर्ण तिथि क्या है?",
#             "answer": d
#         })

#     # Emails
#     emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
#     for e in emails:
#         faqs.append({
#             "question": f"{filename} में ईमेल क्या दिया गया है?",
#             "answer": e
#         })

#     # Phones
#     phones = re.findall(r"\b\d{3,4}[- ]?\d{6,7}\b", text)
#     for p in phones:
#         faqs.append({
#             "question": f"{filename} में संपर्क नंबर क्या है?",
#             "answer": p
#         })

#     # Keyword detection
#     keywords = {
#         "परीक्षा": "परीक्षा कब आयोजित होगी?",
#         "शुल्क": "शुल्क जमा करने की अंतिम तिथि क्या है?",
#         "छात्रवृत्ति": "छात्रवृत्ति से जुड़ी जानकारी क्या है?",
#         "अवकाश": "अवकाश कब घोषित किया गया है?",
#         "Sports": "कौन सा खेल उल्लेखित है?",
#         "sport": "कौन सा खेल उल्लेखित है?"
#     }
#     for word, q in keywords.items():
#         if word in text:
#             faqs.append({
#                 "question": q,
#                 "answer": text
#             })

#     return faqs

# # -------------------------
# # STEP 3: Main
# # -------------------------
# def main():
#     files = [os.path.join(SAVE_DIR, f) for f in os.listdir(SAVE_DIR) if f.endswith(".pdf")]
#     all_faqs = []

#     for file in files[:5]:  # just first 5 PDFs
#         print(f"Extracting {file}")
#         text = extract_text(file)
#         if text:
#             faqs = generate_faqs(text, os.path.basename(file))
#             all_faqs.extend(faqs)

#     with open(FAQ_JSON, "w", encoding="utf-8") as f:
#         json.dump(all_faqs, f, indent=2, ensure_ascii=False)

#     print(f"FAQ JSON created with {len(all_faqs)} Q&As ✅")

# if __name__ == "__main__":
#     main()


# import os
# import re
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# import pdfplumber
# import json
# from PyPDF2 import PdfReader

# # ----------------- CONFIG -----------------
# BASE_URL = "https://www.uniraj.ac.in/index.php?mid=196"  # Notices page
# SAVE_DIR = "pdfs_uniraj"
# FAQ_JSON = "faq_uniraj.json"
# PDF_LIMIT = 5
# os.makedirs(SAVE_DIR, exist_ok=True)

# # ----------------- FUNCTIONS -----------------
# def get_pdf_links(url, limit=PDF_LIMIT):
#     """Fetch first N PDF links from notices page."""
#     r = requests.get(url)
#     soup = BeautifulSoup(r.text, "html.parser")
#     pdf_links = []
#     for a in soup.find_all("a", href=True):
#         if ".pdf" in a['href'].lower():
#             full_url = urljoin(url, a['href'])
#             pdf_links.append(full_url)
#         if len(pdf_links) >= limit:
#             break
#     return pdf_links

# def download_pdfs(links):
#     """Download PDFs reliably with headers and streaming."""
#     files = []
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
#                       "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
#     }

#     for link in links:
#         filename = os.path.join(SAVE_DIR, os.path.basename(link))
#         if not os.path.exists(filename):
#             print(f"Downloading {link}")
#             try:
#                 with requests.get(link, headers=headers, stream=True, timeout=20) as r:
#                     r.raise_for_status()
#                     with open(filename, "wb") as f:
#                         for chunk in r.iter_content(chunk_size=8192):
#                             if chunk:
#                                 f.write(chunk)
#             except Exception as e:
#                 print(f"Failed to download {link}: {e}")
#                 continue

#         # Verify PDF validity
#         if is_pdf_valid(filename):
#             files.append(filename)
#         else:
#             print(f"PDF is corrupt, deleting: {filename}")
#             os.remove(filename)
#     return files

# def is_pdf_valid(file):
#     """Check if a PDF can be opened by PyPDF2."""
#     try:
#         PdfReader(file)
#         return True
#     except:
#         return False

# def extract_text(file):
#     """Extract full text from PDF."""
#     text = ""
#     with pdfplumber.open(file) as pdf:
#         for page in pdf.pages:
#             t = page.extract_text()
#             if t:
#                 text += t + "\n"
#     return text.strip()

# def generate_faqs(text, filename):
#     """Generate Q&As from full PDF text."""
#     faqs = []

#     # Generic summary question
#     faqs.append({
#         "question": f"What is the notice in {filename} about?",
#         "answer": text
#     })

#     # Extract dates
#     dates = re.findall(r"\d{1,2}[-./]\d{1,2}[-./]\d{2,4}", text)
#     for d in dates:
#         faqs.append({
#             "question": f"What is the important date mentioned in {filename}?",
#             "answer": d
#         })

#     # Extract emails
#     emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
#     for e in emails:
#         faqs.append({
#             "question": f"What is the email contact in {filename}?",
#             "answer": e
#         })

#     # Extract phone numbers
#     phones = re.findall(r"\b\d{3,4}[- ]?\d{6,7}\b", text)
#     for p in phones:
#         faqs.append({
#             "question": f"What is the phone number mentioned in {filename}?",
#             "answer": p
#         })

#     # Sports/events
#     if "Sports" in text or "sport" in text.lower():
#         faqs.append({
#             "question": f"Which sports are mentioned in {filename}?",
#             "answer": text
#         })

#     return faqs

# # ----------------- MAIN SCRIPT -----------------
# def main():
#     pdf_links = get_pdf_links(BASE_URL)
#     print(f"Found {len(pdf_links)} PDFs")

#     files = download_pdfs(pdf_links)

#     all_faqs = []
#     for file in files:
#         print(f"Extracting {file}")
#         text = extract_text(file)
#         if text:
#             faqs = generate_faqs(text, os.path.basename(file))
#             all_faqs.extend(faqs)

#     with open(FAQ_JSON, "w", encoding="utf-8") as f:
#         json.dump(all_faqs, f, indent=2, ensure_ascii=False)

#     print(f"FAQ JSON created with {len(all_faqs)} Q&As ✅")

# if __name__ == "__main__":
#     main()


# import os
# import re
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# import pdfplumber
# import json

# # ---------------- CONFIG ----------------
# BASE_URL = "https://www.uniraj.ac.in/index.php?mid=196"
# SAVE_DIR = "pdfs_uniraj"
# FAQ_JSON = "faq_uniraj.json"
# PDF_LIMIT = 50
# os.makedirs(SAVE_DIR, exist_ok=True)

# # ---------------- FUNCTIONS ----------------
# def get_pdf_links(url, limit=PDF_LIMIT):
#     """Fetch first N PDF links from notices page."""
#     r = requests.get(url)
#     soup = BeautifulSoup(r.text, "html.parser")
#     pdf_links = []
#     for a in soup.find_all("a", href=True):
#         if ".pdf" in a['href'].lower():
#             full_url = urljoin(url, a['href'])
#             pdf_links.append(full_url)
#         if len(pdf_links) >= limit:
#             break
#     return pdf_links

# def download_pdfs(links):
#     """Download PDFs with streaming and check validity using pdfplumber."""
#     files = []
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
#                       "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
#     }

#     for link in links:
#         filename = os.path.join(SAVE_DIR, os.path.basename(link))
#         print(f"Downloading {link} ...")
#         try:
#             # Stream download
#             with requests.get(link, headers=headers, stream=True, timeout=30) as r:
#                 r.raise_for_status()
#                 with open(filename, "wb") as f:
#                     for chunk in r.iter_content(8192):
#                         f.write(chunk)

#             # Verify PDF with pdfplumber
#             if not is_pdf_valid(filename):
#                 print(f"Corrupt PDF detected, deleting {filename}")
#                 os.remove(filename)
#             else:
#                 files.append(filename)

#         except Exception as e:
#             print(f"Failed to download {link}: {e}")
#             if os.path.exists(filename):
#                 os.remove(filename)

#     return files

# def is_pdf_valid(file):
#     """Check PDF can be opened with pdfplumber."""
#     try:
#         with pdfplumber.open(file):
#             return True
#     except:
#         return False

# def extract_text(file):
#     """Extract text from PDF."""
#     text = ""
#     with pdfplumber.open(file) as pdf:
#         for page in pdf.pages:
#             t = page.extract_text()
#             if t:
#                 text += t + "\n"
#     return text.strip()

# def generate_faqs(text, filename):
#     """Generate FAQs from PDF text."""
#     faqs = []
#     faqs.append({"question": f"What is the notice in {filename} about?", "answer": text})

#     # Dates
#     dates = re.findall(r"\d{1,2}[-./]\d{1,2}[-./]\d{2,4}", text)
#     for d in dates:
#         faqs.append({"question": f"Important date in {filename}?", "answer": d})

#     # Emails
#     emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
#     for e in emails:
#         faqs.append({"question": f"Email contact in {filename}?", "answer": e})

#     # Phones
#     phones = re.findall(r"\b\d{3,4}[- ]?\d{6,7}\b", text)
#     for p in phones:
#         faqs.append({"question": f"Phone number in {filename}?", "answer": p})

#     # Sports/events
#     if "Sports" in text or "sport" in text.lower():
#         faqs.append({"question": f"Sports mentioned in {filename}?", "answer": text})

#     return faqs

# # ---------------- MAIN ----------------
# def main():
#     pdf_links = get_pdf_links(BASE_URL)
#     print(f"Found {len(pdf_links)} PDFs.")

#     files = download_pdfs(pdf_links)
#     if not files:
#         print("No valid PDFs downloaded. Exiting.")
#         return

#     all_faqs = []
#     for file in files:
#         print(f"Extracting text from {file} ...")
#         text = extract_text(file)
#         if text:
#             faqs = generate_faqs(text, os.path.basename(file))
#             all_faqs.extend(faqs)

#     with open(FAQ_JSON, "w", encoding="utf-8") as f:
#         json.dump(all_faqs, f, indent=2, ensure_ascii=False)

#     print(f"FAQ JSON created with {len(all_faqs)} Q&As ✅")

# if __name__ == "__main__":
#     main()



import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pdfplumber
import json

BASE_URL = "https://www.uniraj.ac.in/index.php?mid=196"
SAVE_DIR = "pdfs_uniraj"
FAQ_JSON = "faq_uniraj.json"
PDF_LIMIT = 50
os.makedirs(SAVE_DIR, exist_ok=True)

def get_pdf_links(url, limit=PDF_LIMIT):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    pdf_links = []
    for a in soup.find_all("a", href=True):
        if ".pdf" in a['href'].lower():
            full_url = urljoin(url, a['href'])
            if full_url not in pdf_links:
                pdf_links.append(full_url)
        if len(pdf_links) >= limit:
            break
    return pdf_links

def download_pdfs(links):
    files = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    for idx, link in enumerate(links, start=1):
        filename = os.path.join(SAVE_DIR, os.path.basename(link))
        print(f"[{idx}/{len(links)}] Downloading {link}")
        try:
            with requests.get(link, headers=headers, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(filename, "wb") as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)
            if not is_pdf_valid(filename):
                print(f"Corrupt PDF detected: {filename}")
                os.remove(filename)
            else:
                files.append(filename)
        except Exception as e:
            print(f"Failed to download {link}: {e}")
            if os.path.exists(filename):
                os.remove(filename)
        time.sleep(1)
    return files

def is_pdf_valid(file):
    try:
        with pdfplumber.open(file):
            return True
    except:
        return False

def extract_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text.strip()

def generate_faqs(text, filename):
    faqs = []

    # Split text into paragraphs for more Q&A
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    for i, para in enumerate(paragraphs):
        # Skip very short lines
        if len(para) < 20:
            continue
        faqs.append({
            "question": f"Q{i+1}: What information is given in {filename}?",
            "answer": para
        })

    # Dates
    dates = re.findall(r"\d{1,2}[-./]\d{1,2}[-./]\d{2,4}", text)
    for d in dates:
        faqs.append({
            "question": f"What is the important date mentioned in {filename}?",
            "answer": d
        })

    # Emails
    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    for e in emails:
        faqs.append({
            "question": f"What is the email contact in {filename}?",
            "answer": e
        })

    # Phones
    phones = re.findall(r"\b\d{3,4}[- ]?\d{6,7}\b", text)
    for p in phones:
        faqs.append({
            "question": f"What is the phone number mentioned in {filename}?",
            "answer": p
        })

    # Sports/events
    if "Sports" in text or "sport" in text.lower():
        faqs.append({
            "question": f"Which sports are mentioned in {filename}?",
            "answer": text
        })

    return faqs

def main():
    pdf_links = get_pdf_links(BASE_URL)
    print(f"Found {len(pdf_links)} PDFs. Trying to download up to {PDF_LIMIT} PDFs.")

    files = download_pdfs(pdf_links)
    if not files:
        print("No valid PDFs downloaded. Exiting.")
        return

    all_faqs = []
    for file in files:
        print(f"Extracting text from {file}")
        text = extract_text(file)
        if text:
            faqs = generate_faqs(text, os.path.basename(file))
            all_faqs.extend(faqs)

    with open(FAQ_JSON, "w", encoding="utf-8") as f:
        json.dump(all_faqs, f, indent=2, ensure_ascii=False)

    print(f"FAQ JSON created with {len(all_faqs)} Q&As ✅")

if __name__ == "__main__":
    main()
