from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[3] / "web/local-dashboard"


class ShellParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str]]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        self.tags.append((tag, dict(attrs)))


def test_html_is_a_semantic_loading_shell_without_governed_records() -> None:
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    parser = ShellParser()
    parser.feed(text)
    tags = [tag for tag, _ in parser.tags]
    attributes = [attrs for _, attrs in parser.tags]

    assert tags.count("h1") == 1
    for landmark in ("header", "nav", "main", "footer"):
        assert landmark in tags
    assert sum(tag == "a" and attrs.get("href", "").startswith("#") for tag, attrs in parser.tags) >= 3
    ids = {attrs.get("id") for attrs in attributes}
    assert {"app", "loading-state", "fatal-error", "status-live"} <= ids
    assert any(attrs.get("aria-live") == "polite" for attrs in attributes)
    assert "mfi-orchestrator" not in text.casefold()
    assert "begin prompt source" not in text.casefold()


def test_assets_are_local_only_and_expose_no_mutation_surface() -> None:
    contents = {
        path.name: path.read_text(encoding="utf-8")
        for path in (ROOT / "index.html", ROOT / "styles.css", ROOT / "app.js")
    }
    combined = "\n".join(contents.values()).casefold()
    for forbidden in (
        "http://", "https://", "//cdn", "@import", "localstorage", "sessionstorage",
        "eval(", "method: 'post'", 'method: "post"', "activate-agent", "approve-agent",
    ):
        assert forbidden not in combined
    assert not re.search(r"\son[a-z]+\s*=", contents["index.html"], re.IGNORECASE)


def test_javascript_uses_safe_dom_rendering_and_explicit_prompt_reveal() -> None:
    script = (ROOT / "app.js").read_text(encoding="utf-8")
    assert "innerHTML" not in script
    assert "insertAdjacentHTML" not in script
    assert "document.write" not in script
    assert "textContent" in script
    assert "createElement" in script
    assert "encodeURIComponent" in script
    assert script.count("/prompt") == 1
    reveal_start = script.index("async function revealPrompt")
    reveal_end = script.index("function closePrompt", reveal_start)
    assert reveal_start < script.index("/prompt") < reveal_end


def test_styles_include_approved_tokens_responsive_focus_and_reduced_motion() -> None:
    styles = (ROOT / "styles.css").read_text(encoding="utf-8").casefold()
    for token in ("#f3f5f2", "#183047", "#2e668f", "#b8873e", "#39776e", "#c66b2b"):
        assert token in styles
    assert "cambria" in styles
    assert "bahnschrift" in styles
    assert ":focus-visible" in styles
    assert "min-height: 44px" in styles
    assert "prefers-reduced-motion" in styles
    assert "@media" in styles


def test_mobile_styles_contain_long_headings_and_navigation_labels() -> None:
    styles = (ROOT / "styles.css").read_text(encoding="utf-8").casefold()
    assert ".page-head h1 { overflow-wrap: anywhere; }" in styles
    assert ".rail-links a { min-width: 0;" in styles
    assert ".governance-ribbon { width: 100%; max-width: 100vw; }" in styles
    assert ".rail-links { width: 100%; min-width: 0; }" in styles
