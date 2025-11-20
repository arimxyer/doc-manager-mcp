"""Code indexing modules for doc-manager."""

# Re-export from subdirectories for backward compatibility
from .analysis import (
    CodeValidator,
    SemanticChange,
    Symbol,
    SymbolIndexer,
    SymbolType,
    compare_symbols,
    load_symbol_baseline,
    save_symbol_baseline,
)
from .parsers import MarkdownParser
from .transforms import (
    compute_link_mappings,
    compute_relative_link,
    extract_frontmatter,
    extract_hugo_shortcodes,
    generate_toc,
    preserve_frontmatter,
    rewrite_links_in_content,
    slugify,
    update_or_insert_toc,
)

__all__ = [
    "CodeValidator",
    "MarkdownParser",
    "SemanticChange",
    "Symbol",
    "SymbolIndexer",
    "SymbolType",
    "compare_symbols",
    "compute_link_mappings",
    "compute_relative_link",
    "extract_frontmatter",
    "extract_hugo_shortcodes",
    "generate_toc",
    "load_symbol_baseline",
    "preserve_frontmatter",
    "rewrite_links_in_content",
    "save_symbol_baseline",
    "slugify",
    "update_or_insert_toc",
]
