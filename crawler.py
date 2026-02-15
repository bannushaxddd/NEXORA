import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from nexora_engine.storage import init_db, insert_document, insert_link

visited = set()

def crawl(seed_urls, max_pages=20):
    init_db()
    queue = list(seed_urls)

    while queue and len(visited) < max_pages:
        url = queue.pop(0)

        if url in visited:
            continue

        try:
            res = requests.get(url, timeout=5)
            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.text, "html.parser")
            text = soup.get_text(" ", strip=True)

            doc_id = insert_document(url, text)
            visited.add(url)

            # Extract links
            for a in soup.find_all("a", href=True):
                link = urljoin(url, a["href"])

                if link.startswith("http"):
                    linked_id = insert_document(link, "")
                    insert_link(doc_id, linked_id)
                    queue.append(link)

        except Exception:
            continue
