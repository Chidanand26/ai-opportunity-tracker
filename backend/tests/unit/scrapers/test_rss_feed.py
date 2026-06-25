"""
Unit tests for RssFeedAdapter.parse_postings() — no network, no database.

All feeds are embedded as strings so these tests run offline in any environment.
"""


from app.domain.entities.source import Source
from app.domain.enums import SourceType
from app.infrastructure.scrapers.sources.rss_feed import RssFeedAdapter

# ── Feed fixtures ─────────────────────────────────────────────────────────────

RSS_TWO_ITEMS = """\
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>Research Lab Opportunities</title>
    <link>https://lab.example.edu</link>
    <item>
      <title>Research Internship in NLP</title>
      <link>https://lab.example.edu/positions/nlp-2025</link>
      <description>10-week summer research internship. Stipend $7,000. Deadline: March 15, 2025.</description>
      <pubDate>Wed, 01 Jan 2025 00:00:00 GMT</pubDate>
      <dc:creator>Prof. Ada Lovelace</dc:creator>
    </item>
    <item>
      <title>PhD Opening in Computer Vision</title>
      <link>https://lab.example.edu/positions/cv-phd-2025</link>
      <description>Funded PhD position starting Fall 2025 in computer vision.</description>
      <pubDate>Wed, 08 Jan 2025 00:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""

ATOM_ONE_ENTRY = """\
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>University Research Office</title>
  <id>https://research.university.edu/feed</id>
  <entry>
    <title>NSF Graduate Research Fellowship</title>
    <link href="https://research.university.edu/fellowships/nsf-grfp"/>
    <summary>Apply for the NSF GRFP fellowship. Award covers tuition and stipend.</summary>
    <published>2025-02-01T00:00:00Z</published>
    <author><name>Office of Research</name></author>
  </entry>
</feed>
"""

EMPTY_RSS = """\
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Empty Feed</title>
  </channel>
</rss>
"""

MALFORMED_ITEMS = """\
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Missing link — should be skipped</title>
    </item>
    <item>
      <link>https://example.edu/no-title</link>
    </item>
    <item>
      <title>Valid item with both fields</title>
      <link>https://example.edu/valid</link>
      <description>A valid item.</description>
    </item>
  </channel>
</rss>
"""

FILTERED_RSS = """\
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Software Engineering Internship</title>
      <link>https://corp.example.com/jobs/swe</link>
      <description>12-week summer internship at our headquarters.</description>
    </item>
    <item>
      <title>Research Assistant in NLP</title>
      <link>https://lab.example.edu/positions/ra-nlp</link>
      <description>Join our NLP lab as an RA.</description>
    </item>
  </channel>
</rss>
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_source(config: dict | None = None) -> Source:
    return Source(
        id=1,
        name="Test Lab",
        url="https://lab.example.edu/feed.rss",
        source_type=SourceType.RSS_FEED,
        adapter_class="rss_feed",
        config=config or {},
    )


# ── Tests ─────────────────────────────────────────────────────────────────────


class TestRssFeedAdapterRss:
    async def test_parses_two_items(self):
        adapter = RssFeedAdapter()
        source = make_source()
        postings = await adapter.parse_postings(RSS_TWO_ITEMS, source.url, source)
        assert len(postings) == 2

    async def test_first_item_title(self):
        adapter = RssFeedAdapter()
        source = make_source()
        postings = await adapter.parse_postings(RSS_TWO_ITEMS, source.url, source)
        assert postings[0].title == "Research Internship in NLP"

    async def test_first_item_url(self):
        adapter = RssFeedAdapter()
        source = make_source()
        postings = await adapter.parse_postings(RSS_TWO_ITEMS, source.url, source)
        assert postings[0].url == "https://lab.example.edu/positions/nlp-2025"

    async def test_first_item_description_has_content(self):
        adapter = RssFeedAdapter()
        source = make_source()
        postings = await adapter.parse_postings(RSS_TWO_ITEMS, source.url, source)
        assert "internship" in postings[0].description.lower()

    async def test_org_name_from_dc_creator(self):
        adapter = RssFeedAdapter()
        source = make_source()
        postings = await adapter.parse_postings(RSS_TWO_ITEMS, source.url, source)
        assert "Ada Lovelace" in postings[0].organization_name

    async def test_org_name_falls_back_to_source_name(self):
        adapter = RssFeedAdapter()
        source = make_source()
        postings = await adapter.parse_postings(RSS_TWO_ITEMS, source.url, source)
        # Second item has no dc:creator — falls back to source name
        assert postings[1].organization_name == source.name

    async def test_empty_feed_returns_empty_list(self):
        adapter = RssFeedAdapter()
        source = make_source()
        postings = await adapter.parse_postings(EMPTY_RSS, source.url, source)
        assert postings == []

    async def test_skips_items_missing_title_or_link(self):
        adapter = RssFeedAdapter()
        source = make_source()
        postings = await adapter.parse_postings(MALFORMED_ITEMS, source.url, source)
        assert len(postings) == 1
        assert postings[0].title == "Valid item with both fields"


class TestRssFeedAdapterAtom:
    async def test_parses_atom_entry(self):
        adapter = RssFeedAdapter()
        source = make_source({"feed_type": "atom"})
        postings = await adapter.parse_postings(ATOM_ONE_ENTRY, source.url, source)
        assert len(postings) == 1

    async def test_atom_entry_title(self):
        adapter = RssFeedAdapter()
        source = make_source({"feed_type": "atom"})
        postings = await adapter.parse_postings(ATOM_ONE_ENTRY, source.url, source)
        assert postings[0].title == "NSF Graduate Research Fellowship"

    async def test_atom_entry_url(self):
        adapter = RssFeedAdapter()
        source = make_source({"feed_type": "atom"})
        postings = await adapter.parse_postings(ATOM_ONE_ENTRY, source.url, source)
        assert "nsf-grfp" in postings[0].url

    async def test_atom_entry_description(self):
        adapter = RssFeedAdapter()
        source = make_source({"feed_type": "atom"})
        postings = await adapter.parse_postings(ATOM_ONE_ENTRY, source.url, source)
        assert "fellowship" in postings[0].description.lower()

    async def test_atom_auto_detect(self):
        """feed_type='auto' should detect Atom from <feed> tag."""
        adapter = RssFeedAdapter()
        source = make_source({"feed_type": "auto"})
        postings = await adapter.parse_postings(ATOM_ONE_ENTRY, source.url, source)
        assert len(postings) == 1


class TestRssFeedAdapterConfig:
    async def test_title_filter_includes_matching(self):
        adapter = RssFeedAdapter()
        source = make_source({"title_filter": r"research assistant"})
        postings = await adapter.parse_postings(FILTERED_RSS, source.url, source)
        assert len(postings) == 1
        assert "Research Assistant" in postings[0].title

    async def test_title_filter_excludes_non_matching(self):
        adapter = RssFeedAdapter()
        source = make_source({"title_filter": r"nonexistent_keyword"})
        postings = await adapter.parse_postings(FILTERED_RSS, source.url, source)
        assert len(postings) == 0

    async def test_max_items_caps_results(self):
        adapter = RssFeedAdapter()
        source = make_source({"max_items": 1})
        postings = await adapter.parse_postings(RSS_TWO_ITEMS, source.url, source)
        assert len(postings) == 1

    async def test_get_start_urls_returns_source_url(self):
        adapter = RssFeedAdapter()
        source = make_source()
        urls = await adapter.get_start_urls(source)
        assert urls == [source.url]
