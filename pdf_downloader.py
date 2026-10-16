import requests
import certifi

def download_pdf(url: str | None) -> bytes | None:
    """Download a PDF from a URL and return its content as bytes, or Non on failure."""

    if not url or not isinstance(url, str):
        return None

    # Mozilla/5.0 is a compatibility artifact to avoid breaking old sites.
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:157.0) Gecko/20100101 Firefox/157.0 "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive"
    }

    try:
        response = requests.get(url, timeout=60, headers=headers, allow_redirects=True, verify=certifi.where())

        if response.status_code == 403:
            print(f"Access denied {403}: {url}")
            print(f"Response content type: "
                  f"{response.headers.get('Content-Type')}")
            print(f"Response preview: {response.text[:200]}")
            return None

        # Checks if the request was successful
        response.raise_for_status()

        # Check that response contains a PDF file with content, not just the URL
        if not response.content.startswith(b"%PDF-"):
            print(f"URL did not return a valid PDF: {url}")
            return None

        return response.content

    except requests.RequestException as error:
        print(f"Failed to download PDF from {url}: {error}")
        return None