"""Tests for markdown parsing cache.

This module tests that the markdown cache correctly caches parsed markdown
content and avoids redundant parsing operations.
"""

import tempfile
from pathlib import Path

import pytest

from doc_manager_mcp.core.markdown_cache import MarkdownCache, ParsedMarkdown


def test_markdown_cache_basic():
    """Test basic cache initialization and usage."""
    cache = MarkdownCache()
    assert cache is not None
    assert len(cache) == 0


def test_parsed_markdown_structure():
    """Test ParsedMarkdown dataclass structure."""
    parsed = ParsedMarkdown(
        headings=[{"level": 1, "text": "Title"}, {"level": 2, "text": "Section"}],
        links=[{"url": "link1.md"}, {"url": "link2.md"}],
        images=[{"alt": "alt text", "src": "image.png"}],
        code_blocks=[{"language": "python", "code": "print('hello')"}]
    )

    assert len(parsed.headings) == 2
    assert len(parsed.links) == 2
    assert len(parsed.images) == 1
    assert len(parsed.code_blocks) == 1


def test_cache_parses_once():
    """Test that cache only parses each file once."""
    cache = MarkdownCache()

    content = """# Title

[Link](page.md)

```python
print('test')
```
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.md"
        file_path.write_text(content)

        # First parse - should cache
        parsed1 = cache.parse(file_path, content)
        assert parsed1 is not None
        assert len(cache) == 1

        # Second parse - should return cached
        parsed2 = cache.parse(file_path, content)
        assert parsed2 is parsed1  # Should be same object (cached)
        assert len(cache) == 1  # Cache size unchanged


def test_cache_extracts_headings():
    """Test that cache correctly extracts headings."""
    cache = MarkdownCache()

    content = """# Main Title

Some text.

## Section 1

More text.

### Subsection

Details.

## Section 2

Final section.
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.md"

        parsed = cache.parse(file_path, content)

        assert len(parsed.headings) >= 4
        # Should have h1, h2, h3, h2
        levels = [h.get("level") for h in parsed.headings]
        assert 1 in levels  # h1
        assert 2 in levels  # h2
        assert 3 in levels  # h3


def test_cache_extracts_links():
    """Test that cache correctly extracts links."""
    cache = MarkdownCache()

    content = """# Test

[Link 1](page1.md)
[Link 2](page2.md)
[External](https://example.com)
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.md"

        parsed = cache.parse(file_path, content)

        assert len(parsed.links) >= 2
        # Should extract link URLs (links are dicts with 'url' key)
        urls = [link.get("url") for link in parsed.links]
        assert any("page1.md" in url for url in urls if url)


def test_cache_extracts_images():
    """Test that cache correctly extracts images."""
    cache = MarkdownCache()

    content = """# Test

![Alt text](image1.png)
![Another image](image2.jpg)
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.md"

        parsed = cache.parse(file_path, content)

        assert len(parsed.images) >= 2


def test_cache_extracts_code_blocks():
    """Test that cache correctly extracts code blocks."""
    cache = MarkdownCache()

    content = """# Test

```python
def hello():
    print("world")
```

```javascript
console.log("test");
```
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.md"

        parsed = cache.parse(file_path, content)

        assert len(parsed.code_blocks) >= 2
        # Should have language and code (code_blocks are dicts with 'language' key)
        languages = [block.get("language", "").lower() for block in parsed.code_blocks]
        assert "python" in languages


def test_cache_multiple_files():
    """Test that cache handles multiple different files."""
    cache = MarkdownCache()

    content1 = "# File 1\n\n[Link](page.md)"
    content2 = "# File 2\n\n```python\ncode```"

    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = Path(tmpdir) / "file1.md"
        file2 = Path(tmpdir) / "file2.md"

        parsed1 = cache.parse(file1, content1)
        parsed2 = cache.parse(file2, content2)

        assert len(cache) == 2
        assert parsed1 is not parsed2  # Different objects


def test_cache_clear():
    """Test that cache can be cleared."""
    cache = MarkdownCache()

    content = "# Test"

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.md"

        # Add to cache
        cache.parse(file_path, content)
        assert len(cache) == 1

        # Clear cache
        cache.clear()
        assert len(cache) == 0


def test_cache_different_content_same_file():
    """Test that cache uses file path as key, not content."""
    cache = MarkdownCache()

    content1 = "# Version 1"
    content2 = "# Version 2"

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.md"

        # First parse
        parsed1 = cache.parse(file_path, content1)
        assert len(parsed1.headings) > 0

        # Second parse with different content (but same file path)
        # Should return cached version (from content1)
        parsed2 = cache.parse(file_path, content2)
        assert parsed2 is parsed1  # Same cached object


def test_cache_invalidate_on_clear():
    """Test that parsing after clear re-parses the file."""
    cache = MarkdownCache()

    content = "# Test\n\n[Link](page.md)"

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.md"

        # First parse
        parsed1 = cache.parse(file_path, content)
        assert len(cache) == 1

        # Clear and re-parse
        cache.clear()
        parsed2 = cache.parse(file_path, content)

        assert len(cache) == 1
        # Should be different object (re-parsed)
        assert parsed2 is not parsed1


def test_cache_performance_benefit():
    """Test that cache provides performance benefit with large content."""
    cache = MarkdownCache()

    # Create large markdown content
    content = "# Title\n\n" + "\n\n".join([
        f"## Section {i}\n\n[Link {i}](page{i}.md)\n\n```python\ncode {i}\n```"
        for i in range(100)
    ])

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "large.md"

        import time

        # First parse (uncached)
        start = time.perf_counter()
        parsed1 = cache.parse(file_path, content)
        time1 = time.perf_counter() - start

        # Second parse (cached)
        start = time.perf_counter()
        parsed2 = cache.parse(file_path, content)
        time2 = time.perf_counter() - start

        # Cached should be much faster (practically instant)
        assert time2 < time1 * 0.1  # At least 10x faster
        assert parsed1 is parsed2  # Same object
