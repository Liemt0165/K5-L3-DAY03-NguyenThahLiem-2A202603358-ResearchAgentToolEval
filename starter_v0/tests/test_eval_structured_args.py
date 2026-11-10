from run_eval import compare_subset


def test_structured_items_compare_without_sorting_dicts():
    items = [{"url": "https://example.com/a", "title": "First"},
             {"url": "https://example.com/a?utm_source=x", "title": "Second"}]
    assert compare_subset({"items": items}, {"items": items})[0]
    assert not compare_subset({"items": items}, {"items": items[::-1]})[0]


def test_scalar_list_comparison_retains_existing_behavior():
    assert compare_subset({"values": ["B", "a"]}, {"values": ["A", "b"]})[0]
