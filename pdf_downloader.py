# import requests
import certifi
import aiohttp


# Mozilla/5.0 is a compatibility artifact to avoid breaking old sites.
HEADERS = {
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


async def download_pdf(url: str | None, session: aiohttp.ClientSession) -> bytes | None:
    """Download a valid PDF asynchronously from a URL and return its content as bytes, or Non on failure."""

    if not isinstance(url, str) or not url.strip():
        return None

    try:
        async with session.get(url, headers=HEADERS, allow_redirects=True) as response:
            # Checks if the request was successful
            response.raise_for_status()

            content = await response.read()

            # Check that response contains a PDF file with content, not just the URL
            # Some servers return HTML even when the URL looks like a PDF
            if b"%PDF-" not in content[:1024]:
                print(f"URL did not return a valid PDF: {url}")
                return None

            return content

    except (aiohttp.ClientError, TimeoutError, ValueError) as error:
        print(f"Failed to download PDF from {url}: {error}")
        return None