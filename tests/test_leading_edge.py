from fde_powerhouse.leading_edge import (
    all_homepages,
    by_category,
    categories,
    library_stats,
    load_sources,
)


def test_load_sources():
    data = load_sources()
    assert data.get("schema", "").startswith("fde.leading_edge")
    assert "tech_news" in data.get("categories", {})
    assert "dev_news" in data["categories"]
    assert "declassified_public_technical" in data["categories"]


def test_homepages_are_https():
    pages = all_homepages()
    assert len(pages) >= 40
    for p in pages:
        assert p["homepage"].startswith("https://"), p


def test_stats():
    s = library_stats()
    assert s["sources"] >= 40
    assert s["categories"] >= 5


def test_by_category_ai():
    srcs = by_category("ai_frontier")
    assert any("anthropic" in (x.get("id") or "") for x in srcs)
    assert any("openai" in (x.get("id") or "") for x in srcs)


def test_categories_sorted():
    c = categories()
    assert c == sorted(c)
