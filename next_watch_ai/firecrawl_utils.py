from typing import Dict,List 
from firecrawl import FirecrawlApp


def make_firecrawl(api_key: str) -> FirecrawlApp:
    return FirecrawlApp(api_key=api_key)

def extract_markdown(scrape_result) -> str:
    if scrape_result is None:
        return ""
    if hasattr(scrape_result, "markdown") and scrape_result.markdown:
        return scrape_result.markdown
    if isinstance(scrape_result, dict):
        return scrape_result.get("markdown", "") or ""
    if hasattr(scrape_result, "data"):
        data = scrape_result.data
        if isinstance(data, dict):
            return data.get("markdown", "") or ""
        if hasattr(data, "markdown"):
            return data.markdown or ""
    return ""

def extract_html(scrape_result) -> str:
    if scrape_result is None:
        return ""
    if hasattr(scrape_result, "html") and scrape_result.html:
        return scrape_result.html
    if isinstance(scrape_result, dict):
        return scrape_result.get("html", "") or ""
    if hasattr(scrape_result, "data"):
        data = scrape_result.data
        if isinstance(data, dict):
            return data.get("html", "") or ""
        if hasattr(data, "html"):
            return data.html or ""
    return ""

def scrape_bundle(
    firecrawl: FirecrawlApp,
    urls: List[str],
    logger=None,
    max_pages: int = 3,
    per_source_chars: int = 2500,
    total_chars: int = 9000,
) -> str:
    """
    Scrape up to max_pages URLs; skip unsupported/blocked URLs instead of crashing.
    """
    chunks = []
    scraped_ok = 0

    for url in urls:
        if scraped_ok >= max_pages:
            break

        try:
            res = firecrawl.scrape(url=url, formats=["markdown"])
            md = extract_markdown(res)

            if md:
                chunks.append(f"SOURCE: {url}\n{md[:per_source_chars]}")
                scraped_ok += 1
            else:
                if logger:
                    logger.info(f"[Firecrawl] Empty markdown: {url}")

        except Exception as e:
            # Firecrawl raises WebsiteNotSupportedError (403) and other errors.
            # We skip and continue.
            if logger:
                logger.warning(f"[Firecrawl] Skipping URL (scrape failed): {url} | {type(e).__name__}: {e}")
            continue

    bundle = "\n\n".join(chunks)
    if logger:
        logger.info(f"[Firecrawl] scrape_bundle complete: kept={scraped_ok} of requested={max_pages}, tried={len(urls)}")
    return bundle[:total_chars]