"""
RssFeedAdapter — reference implementation.

Scrapes standard RSS 2.0 and Atom 1.0 feeds. Many research labs, university
departments, and academic funding bodies publish their opportunities as feeds.

This adapter demonstrates the minimal surface area every concrete adapter
must implement: get_start_urls() and parse_postings(). Everything else
(retry, rate limiting, robots.txt, logging) is inherited.

Configuration keys (in source.config):
    feed_type        : "rss" | "atom" | "auto"  (default: "auto")
    title_filter     : regex pattern — only ingest items whose title matches
    max_items        : int — cap items per run (default: unlimited)

Example source registration:
    Source(
        name="MIT CSAIL Research Opportunities",
        url="https://www.csail.mit.edu/research/opportunities.rss",
        source_type=SourceType.RSS_FEED,
        adapter_class="rss_feed",
        config={"title_filter": r"(intern|ra|research assistant)", "max_items": 50},
    )
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup, Tag

from app.core.logging import get_logger
from app.domain.entities.source import Source
from app.domain.enums import OpportunityType
from app.domain.ports.scraper_port import RawPosting
from app.infrastructure.scrapers.adapter import BaseSourceAdapter

logger = get_logger(__name__)


class RssFeedAdapter(BaseSourceAdapter):
    """
    RSS 2.0 / Atom 1.0 feed adapter.

    Concrete adapters implement only these two methods.
    All network, retry, rate-limit, robots.txt logic lives in BaseSourceAdapter.
    """

    opportunity_type = OpportunityType.RESEARCH_INTERNSHIP
    needs_browser = False
    requests_per_minute = 30   # feeds are cheap — higher rate OK

    # ── Required: URL discovery ───────────────────────────────────────────────

    async def get_start_urls(self, source: Source) -> list[str]:
        return [source.url]

    # ── Required: parsing ─────────────────────────────────────────────────────

    async def parse_postings(
        self, content: str, url: str, source: Source
    ) -> list[RawPosting]:
        """
        Parse RSS 2.0 or Atom 1.0 XML into RawPosting objects.

        BeautifulSoup with the `xml` parser handles both formats via different
        tag names (<item> for RSS, <entry> for Atom).
        """
        config = source.config or {}
        feed_type = config.get("feed_type", "auto")
        title_filter = config.get("title_filter")
        max_items = config.get("max_items")

        soup = BeautifulSoup(content, "xml")

        # Detect format
        if feed_type == "auto":
            feed_type = "atom" if soup.find("feed") else "rss"

        items = self._get_items(soup, feed_type)
        logger.debug("feed_parsed", url=url, format=feed_type, item_count=len(items))

        postings: list[RawPosting] = []
        for item in items:
            posting = self._parse_item(item, feed_type, source)
            if posting is None:
                continue
            if title_filter and not re.search(title_filter, posting.title, re.IGNORECASE):
                continue
            postings.append(posting)
            if max_items and len(postings) >= int(max_items):
                break

        return postings

    # ── Internals ─────────────────────────────────────────────────────────────

    @staticmethod
    def _get_items(soup: BeautifulSoup, feed_type: str) -> list[Tag]:
        if feed_type == "atom":
            return soup.find_all("entry")
        return soup.find_all("item")

    def _parse_item(
        self, item: Tag, feed_type: str, source: Source
    ) -> RawPosting | None:
        if feed_type == "atom":
            return self._parse_atom_entry(item, source)
        return self._parse_rss_item(item, source)

    @staticmethod
    def _parse_rss_item(item: Tag, source: Source) -> RawPosting | None:
        title = _text(item, "title")
        link = _text(item, "link")
        if not title or not link:
            return None

        description = (
            _text(item, "description")
            or _text(item, "content:encoded")
            or ""
        )
        # Strip HTML tags from description
        description = BeautifulSoup(description, "html.parser").get_text(
            separator=" ", strip=True
        )

        org_name = (
            _text(item, "author")
            or _text(item, "dc:creator")
            or source.name
        )
        pub_date = _text(item, "pubDate") or _text(item, "dc:date") or ""

        return RawPosting(
            title=title.strip(),
            url=link.strip(),
            organization_name=org_name.strip(),
            description=description[:5000],   # cap to avoid huge payloads
            application_deadline="",
            start_date=pub_date,
            extra={"pub_date": pub_date, "source_name": source.name},
        )

    @staticmethod
    def _parse_atom_entry(entry: Tag, source: Source) -> RawPosting | None:
        title = _text(entry, "title")
        # Atom <link> is an element with href attribute, not text content
        link_tag = entry.find("link")
        link = ""
        if isinstance(link_tag, Tag):
            link = link_tag.get("href", "") or _text(entry, "link") or ""

        if not title or not link:
            return None

        description = (
            _text(entry, "summary")
            or _text(entry, "content")
            or ""
        )
        description = BeautifulSoup(description, "html.parser").get_text(
            separator=" ", strip=True
        )

        org_name = (
            _text(entry, "author")
            or _text(entry, "name")       # <author><name>...</name></author>
            or source.name
        )
        published = _text(entry, "published") or _text(entry, "updated") or ""

        return RawPosting(
            title=title.strip(),
            url=str(link).strip(),
            organization_name=org_name.strip(),
            description=description[:5000],
            application_deadline="",
            start_date=published,
            extra={"published": published, "source_name": source.name},
        )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _text(tag: Tag, name: str) -> str:
    """Safely extract text from a child tag; return '' if missing."""
    child = tag.find(name)
    if child is None:
        return ""
    return child.get_text(strip=True) if hasattr(child, "get_text") else ""
