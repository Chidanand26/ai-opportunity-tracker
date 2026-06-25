"""
Adapter registry — maps adapter_class strings to concrete adapter classes.

The `adapter_class` column on the Source model stores a short key (e.g. "rss_feed")
or a fully-qualified dotted import path. The registry resolves either form.

Adding a new adapter:
  1. Implement it in sources/<name>.py.
  2. Add it to _BUILTIN_ADAPTERS below.
  3. Register sources in the DB with adapter_class="<key>".
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.infrastructure.scrapers.adapter import BaseSourceAdapter

# Short-key → fully-qualified class path
_BUILTIN_ADAPTERS: dict[str, str] = {
    "rss_feed": "app.infrastructure.scrapers.sources.rss_feed.RssFeedAdapter",
    # Future entries (added as steps are implemented):
    # "university_portal": "app.infrastructure.scrapers.sources.university_portal.UniversityPortalAdapter",
    # "professor_page":    "app.infrastructure.scrapers.sources.professor_page.ProfessorPageAdapter",
    # "company_portal":   "app.infrastructure.scrapers.sources.company_portal.CompanyPortalAdapter",
}


def get_adapter_class(adapter_class: str) -> type["BaseSourceAdapter"]:
    """
    Resolve an adapter_class string to the concrete Python class.

    Accepts either:
      - A short key:  "rss_feed"
      - A dotted path: "app.infrastructure.scrapers.sources.rss_feed.RssFeedAdapter"

    Raises:
        KeyError: short key not registered.
        ImportError / AttributeError: dotted path not importable.
    """
    # Resolve short key to dotted path
    dotted = _BUILTIN_ADAPTERS.get(adapter_class, adapter_class)

    module_path, _, class_name = dotted.rpartition(".")
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def make_adapter(adapter_class: str, source_config: dict | None = None) -> "BaseSourceAdapter":
    """Instantiate an adapter by its class string."""
    cls = get_adapter_class(adapter_class)
    return cls(source_config=source_config)


def list_registered() -> list[str]:
    """Return all registered short keys (for admin UI)."""
    return list(_BUILTIN_ADAPTERS.keys())
