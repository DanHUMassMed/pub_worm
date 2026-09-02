from datetime import datetime, timedelta
from typing import Any, List, Optional, Union

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, ConfigDict, Field


class Funder(BaseModel):
    name: Optional[str] = ""
    id: Optional[str] = ""
    id_type: Optional[str] = ""
    award: Optional[str] = ""


class Paper(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = ""
    authors: str = ""
    author_corresponding: Optional[str] = ""
    author_corresponding_institution: Optional[str] = ""
    doi: str = ""
    date: str = ""
    version: Union[int, str] = "1"
    type: Optional[str] = ""
    license: Optional[str] = ""
    category: Optional[str] = ""
    jatsxml: Optional[str] = ""
    abstract: Optional[str] = ""
    funder: Union[str, List[Funder]] = ""
    published: Optional[str] = ""
    server: Optional[str] = "bioRxiv"


class Message(BaseModel):
    status: str
    category: Optional[str] = None
    interval: Optional[str] = None
    funder: Optional[str] = None
    cursor: Optional[Union[int, str]] = 0
    count: Optional[Union[int, str]] = 0
    count_new_papers: Optional[Union[int, str]] = 0
    total: Optional[Union[int, str]] = 0


class BioRxivResponse(BaseModel):
    messages: List[Message] = Field(default_factory=list)
    collection: List[Paper] = Field(default_factory=list)

    @property
    def is_ok(self) -> bool:
        return bool(self.messages and self.messages[0].status == "ok")

    @property
    def error_message(self) -> Optional[str]:
        if not self.messages:
            return "Empty response messages"
        if self.messages[0].status != "ok":
            return self.messages[0].status
        return None

    @property
    def total(self) -> int:
        if self.messages and self.messages[0].total is not None:
            try:
                return int(self.messages[0].total)
            except (ValueError, TypeError):
                return 0
        return 0

    @property
    def count(self) -> int:
        if self.messages and self.messages[0].count is not None:
            try:
                return int(self.messages[0].count)
            except (ValueError, TypeError):
                return len(self.collection)
        return len(self.collection)


def biorxiv_most_recent_30_posts() -> bytes:
    """Retrieve raw XML content for the most recent 30 posts on bioRxiv."""
    url = "https://connect.biorxiv.org/biorxiv_xml.php?subject=all"
    response = requests.get(url, timeout=20)
    if response.status_code == 200:
        return response.content
    else:
        raise RuntimeError(f"Failed to retrieve data from bioRxiv feed: {response.status_code}")


# Backwards compatibility alias
biorxiv_most_recent_30__posts = biorxiv_most_recent_30_posts


def _contains_keywords(text: str, keywords: list[str]) -> bool:
    """Check if any keyword is contained in the text (case-insensitive)."""
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords)


def biorxiv_recent_posts_filtered(
    keywords: list[str] = ["caenorhabditis", "elegans"],
) -> list[dict[str, str]]:
    """Retrieve recent posts from the bioRxiv RSS feed matching given keywords."""
    xml_data = biorxiv_most_recent_30_posts()
    soup = BeautifulSoup(xml_data, "xml")
    articles: list[dict[str, str]] = []

    for item in soup.find_all("item"):
        title_tag = item.find("title")
        description_tag = item.find("description")
        date_tag = item.find("dc:date")
        identifier_tag = item.find("dc:identifier")

        title = title_tag.get_text(strip=True) if title_tag else ""
        description = description_tag.get_text(strip=True) if description_tag else ""
        dc_date = date_tag.get_text(strip=True) if date_tag else ""
        dc_identifier = identifier_tag.get_text(strip=True) if identifier_tag else ""

        if _contains_keywords(title, keywords) or _contains_keywords(description, keywords):
            doi_url = f"https://doi.org/{dc_identifier}" if dc_identifier else ""
            articles.append({
                "title": title,
                "date": dc_date,
                "doi": doi_url,
                "url": doi_url,
            })

    return articles


def fetch_biorxiv_page(
    start_date: str,
    end_date: str,
    cursor: int = 0,
    session: Optional[requests.Session] = None,
    timeout: int = 60,
) -> BioRxivResponse:
    """Fetch a single page (up to 30 items) from the bioRxiv REST API."""
    url = f"https://api.biorxiv.org/details/biorxiv/{start_date}/{end_date}/{cursor}/json"
    client = session if session is not None else requests
    try:
        response = client.get(url, timeout=timeout)
        if response.status_code != 200:
            return BioRxivResponse(
                messages=[Message(status=f"HTTP {response.status_code}")],
                collection=[],
            )
        data: dict[str, Any] = response.json()
        return BioRxivResponse.model_validate(data)
    except Exception as error:
        return BioRxivResponse(
            messages=[Message(status=f"Request error: {error}")],
            collection=[],
        )


def biorxiv_search(
    search_criteria: str = "caenorhabditis elegans",
    days: int = 1,
    verbose: bool = True,
    timeout: int = 60,
) -> list[dict[str, str]]:
    """Search bioRxiv for papers published in the last `days` matching criteria via REST API."""
    today = datetime.today()
    start_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")

    cursor = 0
    results: list[dict[str, str]] = []
    keywords = [kw.strip().lower() for kw in search_criteria.lower().split() if kw.strip()]

    with requests.Session() as session:
        while True:
            response_obj = fetch_biorxiv_page(
                start_date=start_date,
                end_date=end_date,
                cursor=cursor,
                session=session,
                timeout=timeout,
            )

            if not response_obj.is_ok or not response_obj.collection:
                if verbose and response_obj.error_message:
                    print(f"bioRxiv API: {response_obj.error_message}", flush=True)
                break

            for paper in response_obj.collection:
                full_text = f"{paper.title} {paper.abstract}".lower()
                if any(kw in full_text for kw in keywords):
                    doi_url = f"https://doi.org/{paper.doi}" if paper.doi else ""
                    results.append({
                        "title": paper.title,
                        "url": doi_url,
                        "doi": paper.doi,
                        "date": paper.date,
                        "category": paper.category or "",
                        "authors": paper.authors,
                    })

            total = response_obj.total
            count = response_obj.count
            if count <= 0:
                break

            cursor += count
            if verbose:
                print(
                    f"Fetched {cursor}/{total} papers ({len(results)} matching)...",
                    flush=True,
                )

            if cursor >= total:
                break

    return results
