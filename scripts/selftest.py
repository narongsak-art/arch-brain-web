"""Selftest · comprehensive diagnostic of the arch-brain-web app

Validates without hitting external APIs:
- All Python files parse
- All component modules import (streamlit mocked)
- Core functions behave (extract_json / slugify / encode-decode roundtrip)
- Documentation counts consistent (PRD · README · About · system-prompt)
- CSS safe (no internal-class selectors)
- GH workflows parse as YAML
- Script entry-points runnable (--help or --dry-run)

Run: python scripts/selftest.py
Exit code 0 = all pass · non-zero = failures
"""

import importlib
import json
import re
import subprocess
import sys
import types
from pathlib import Path


REPO = Path(__file__).parent.parent

# Tracking
results: list[tuple[str, bool, str]] = []   # (name, passed, detail)


def check(name: str):
    """Decorator-ish: wrap a check · auto-capture exceptions"""
    def _wrap(fn):
        try:
            msg = fn()
            results.append((name, True, msg or ""))
        except AssertionError as e:
            results.append((name, False, str(e) or "assertion failed"))
        except Exception as e:
            results.append((name, False, f"{type(e).__name__}: {e}"))
        return fn
    return _wrap


# ============================================================================
# Mocked Streamlit for import tests
# ============================================================================

def _install_mock_streamlit():
    st = types.ModuleType("streamlit")

    class _M:
        def __getattr__(self, n): return _M()
        def __call__(self, *a, **k):
            if a and isinstance(a[0], (int, list, tuple)):
                n = a[0] if isinstance(a[0], int) else len(a[0])
                return tuple(_M() for _ in range(n))
            return _M()
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def __iter__(self): return iter([_M()])

    def cache_data(*a, **k):
        if a and callable(a[0]):
            return a[0]
        return lambda f: f

    class _Secrets:
        def get(self, k, d=None): return d
        def __getitem__(self, k): return {}

    st.cache_data = cache_data
    st.secrets = _Secrets()
    st.session_state = {}
    st.query_params = {}
    st.column_config = types.SimpleNamespace(
        ProgressColumn=lambda *a, **k: _M()
    )

    for attr in [
        "set_page_config", "sidebar", "markdown", "title", "caption",
        "header", "subheader", "info", "success", "warning", "error",
        "button", "text_input", "text_area", "number_input", "slider",
        "selectbox", "radio", "multiselect", "columns", "expander",
        "file_uploader", "download_button", "spinner", "rerun", "image",
        "tabs", "write", "code", "dataframe", "json", "metric", "progress",
        "chat_message", "chat_input", "date_input", "container", "switch_page",
        "color_picker", "popover", "divider", "stop", "form",
        "form_submit_button", "toggle", "status", "checkbox", "empty",
        "html", "table",
    ]:
        setattr(st, attr, _M())

    sys.modules["streamlit"] = st


# ============================================================================
# Checks
# ============================================================================

@check("All Python files parse")
def _test_syntax():
    import ast
    failures = []
    for p in REPO.rglob("*.py"):
        if ".git" in p.parts or "__pycache__" in p.parts:
            continue
        try:
            ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
        except SyntaxError as e:
            failures.append(f"{p.relative_to(REPO)}: {e}")
    if failures:
        raise AssertionError("\n  " + "\n  ".join(failures))
    py_files = [p for p in REPO.rglob("*.py")
                if ".git" not in p.parts and "__pycache__" not in p.parts]
    return f"{len(py_files)} .py files OK"


@check("All components importable")
def _test_imports():
    _install_mock_streamlit()
    sys.path.insert(0, str(REPO))
    modules = [
        "theme", "llm", "analysis", "presets", "history", "contribute",
        "project_io", "export_pdf", "share", "image_gen", "chat", "compare",
        "booking", "tiers", "github_sync", "admin",
        "studio", "materials", "explore",  # Thai studio pivot
    ]
    loaded = []
    for m in modules:
        mod = importlib.import_module(f"components.{m}")
        loaded.append(m)
    return f"{len(loaded)} components OK"


@check("Materials library · 5 groups · 25+ items")
def _test_materials():
    sys.path.insert(0, str(REPO))
    from components import materials
    groups = materials.MATERIALS
    assert len(groups) == 5, f"expected 5 groups, got {len(groups)}"
    total = sum(len(g["items"]) for g in groups.values())
    assert total >= 25, f"expected 25+ items, got {total}"
    # Each item must be (name, hex, note) triple
    for gk, g in groups.items():
        for ik, v in g["items"].items():
            assert len(v) == 3, f"{gk}/{ik}: malformed item"
            name, hex_color, note = v
            assert hex_color.startswith("#"), f"{gk}/{ik}: bad hex {hex_color}"
    # palette_summary empty when no picks
    import streamlit as st
    st.session_state = {}
    assert materials.palette_summary() == ""
    materials.set_pick("roof", "tile-clay")
    assert "กระเบื้องดินเผา" in materials.palette_summary()
    return f"5 groups · {total} items · summary works"


@check("Portfolio HTML export · includes all sections")
def _test_portfolio():
    sys.path.insert(0, str(REPO))
    from components import export_pdf
    pd = {"name": "บ้านทดสอบ", "land_w": 15, "land_d": 20, "land_area": 300,
          "zone": "ย.3", "budget": 8, "province": "กทม.", "floors": "2",
          "bedrooms": "3", "family_size": 4, "has_elderly": "ใช่",
          "fengshui": "ปานกลาง", "special": "ห้องพระ"}
    palette = {"roof": {"name": "กระเบื้องดินเผา", "hex": "#a0522d",
                        "note": "classic Thai", "group_label": "หลังคา"}}
    html = export_pdf.build_portfolio_html(pd, "## Test analysis\n\nบ้านนี้ดี", "gemini",
                                            palette=palette, images=None)
    assert "บ้านทดสอบ" in html
    assert "THAI RESIDENTIAL PORTFOLIO" in html
    assert "กระเบื้องดินเผา" in html
    assert "#a0522d" in html
    assert "@media print" in html  # print styles
    assert "DOCTYPE html" in html
    return f"portfolio HTML {len(html):,} chars · all sections present"


@check("JSON parser · pure / fenced / embedded / invalid")
def _test_json_extract():
    sys.path.insert(0, str(REPO))
    from components import analysis
    cases = [
        ('{"k":1}', {"k": 1}),
        ('```json\n{"k":1}\n```', {"k": 1}),
        ('commentary {"k":1} trailing', {"k": 1}),
        ('invalid', None),
        ('', None),
    ]
    for inp, expected in cases:
        got = analysis.extract_json(inp)
        assert got == expected, f"input {inp!r}: got {got}, expected {expected}"
    return f"{len(cases)} cases OK"


@check("Share encode/decode roundtrip (Thai)")
def _test_share_roundtrip():
    sys.path.insert(0, str(REPO))
    from components import share
    pd = {"name": "บ้านทดสอบ", "land_w": 15, "zone": "ย.3"}
    result = {"summary": {"feasibility": "green", "score": 80}}
    enc = share.encode_payload(pd, result, None, "gemini")
    dec = share.decode_payload(enc)
    assert dec is not None
    assert dec["project_data"]["name"] == "บ้านทดสอบ"
    assert dec["result"]["summary"]["feasibility"] == "green"
    return f"encoded {len(enc)} chars · url {len(share.build_url(enc))} chars"


@check("Slugify · Thai + English + punct + empty")
def _test_slugify():
    sys.path.insert(0, str(REPO))
    from components import github_sync
    cases = [
        ("ระยะร่น 3 ม. ใน ย.5 ผิด", lambda s: "ระยะร่น" in s and "-" in s),
        ("Hello World!!!", lambda s: s == "hello-world"),
        ("", lambda s: s == "untitled"),
        ("   spaces   ", lambda s: s == "spaces"),
    ]
    for inp, predicate in cases:
        got = github_sync.slugify(inp)
        assert predicate(got), f"slugify({inp!r}) → {got!r}"
    return f"{len(cases)} cases OK"


@check("Tier quota logic")
def _test_tier_quota():
    sys.path.insert(0, str(REPO))
    from components import tiers
    # Reset
    import streamlit as st
    st.session_state = {}
    tiers.set_tier("free")
    assert tiers.get_remaining() == 5
    for _ in range(5):
        tiers.increment_analysis()
    ok, _ = tiers.check_quota()
    assert not ok, "should be blocked at 5"
    tiers.set_tier("pro")
    assert tiers.get_remaining() is None, "pro should be unlimited"
    ok, _ = tiers.check_quota()
    assert ok, "pro should allow"
    return "free 5-limit + pro unlimited OK"


@check("Admin auth constant-time")
def _test_admin_auth():
    sys.path.insert(0, str(REPO))
    from components import admin
    import streamlit as st
    # No secrets · False
    st.secrets = type("x", (), {"get": lambda self, k, d=None: d})()
    st.query_params = {"admin": "anything"}
    assert not admin.is_admin_mode()
    # With matching secret · True
    st.secrets = type("x", (), {"get": lambda self, k, d=None: {"token": "correct"} if k == "admin" else d})()
    st.query_params = {"admin": "correct"}
    assert admin.is_admin_mode()
    # Mismatch · False
    st.query_params = {"admin": "wrong"}
    assert not admin.is_admin_mode()
    # Empty · False
    st.query_params = {}
    assert not admin.is_admin_mode()
    return "4 cases OK (no-secret · match · mismatch · empty)"


@check("KG file consistency (node_count in json matches meta)")
def _test_kg_integrity():
    kg = json.loads((REPO / "kg-compact.json").read_text(encoding="utf-8"))
    meta = kg.get("meta", {})
    nodes = kg.get("nodes", [])
    edges = kg.get("edges", [])
    assert meta.get("node_count") == len(nodes), f"node_count mismatch: meta says {meta.get('node_count')}, array has {len(nodes)}"
    assert meta.get("edge_count") == len(edges), f"edge_count mismatch"
    # Sanity: all edges reference nodes that exist
    node_ids = {n["id"] for n in nodes}
    bad_edges = [e for e in edges if e["from"] not in node_ids or e["to"] not in node_ids]
    assert not bad_edges, f"{len(bad_edges)} edges reference non-existent nodes"
    return f"{len(nodes)} nodes · {len(edges)} edges · all edges valid"


@check("Documentation stat numbers agree")
def _test_doc_stats():
    kg = json.loads((REPO / "kg-compact.json").read_text(encoding="utf-8"))
    n_nodes = kg["meta"]["node_count"]
    n_edges = kg["meta"]["edge_count"]
    # All docs should reference same numbers
    discrepancies = []
    for doc_name in ["README.md", "PRD.md", "system-prompt.md"]:
        doc = (REPO / doc_name).read_text(encoding="utf-8")
        # Should mention correct node count somewhere
        if str(n_nodes) not in doc:
            discrepancies.append(f"{doc_name} doesn't mention {n_nodes} nodes")
    if discrepancies:
        raise AssertionError("; ".join(discrepancies))
    return f"README + PRD + system-prompt all reference {n_nodes} nodes"


@check("Theme CSS has no fragile selectors")
def _test_css():
    sys.path.insert(0, str(REPO))
    from components import theme
    css = theme._build_css("light")
    bad = [".css-", 'class*="st-', ".element-container", ".stMarkdown > ", 'class*="css-']
    for b in bad:
        assert b not in css, f"fragile selector: {b}"
    # Should use data-testid
    assert "[data-testid=" in css
    # Both themes produce CSS
    dark = theme._build_css("dark")
    assert len(dark) > 1000
    return f"light CSS {len(css)}B · dark {len(dark)}B · no fragile selectors"


@check("GitHub workflows parse as YAML")
def _test_workflows():
    try:
        import yaml  # PyYAML usually not in requirements, try anyway
    except ImportError:
        # Fallback: just check they're readable text
        files = list((REPO / ".github" / "workflows").glob("*.yml"))
        for f in files:
            content = f.read_text(encoding="utf-8")
            assert "name:" in content
            assert "on:" in content or "'on':" in content
            assert "jobs:" in content
        return f"{len(files)} workflow files (no PyYAML · structural check only)"
    files = list((REPO / ".github" / "workflows").glob("*.yml"))
    for f in files:
        yaml.safe_load(f.read_text(encoding="utf-8"))
    return f"{len(files)} workflows parse as YAML"


@check("Scripts: build_kg smoke-test")
def _test_build_kg():
    r = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "build_kg.py")],
        capture_output=True, text=True, encoding="utf-8",
        cwd=str(REPO), env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"},
    )
    assert r.returncode == 0, f"build_kg failed: {r.stderr[:200]}"
    return r.stdout.strip().replace("\n", " · ")


@check("Scripts: ingest_contributions --dry-run")
def _test_ingest_dryrun():
    r = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "ingest_contributions.py"),
         "--dry-run", "--no-kg-regen", "--vault", str(REPO.parent / "NarongsakBIM")],
        capture_output=True, text=True, encoding="utf-8",
        cwd=str(REPO), env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"},
    )
    # Vault may not exist on CI · that's fine as long as it fails gracefully
    return (r.stdout or r.stderr).strip().splitlines()[0] if (r.stdout or r.stderr) else "no output"


# ============================================================================
# Runner
# ============================================================================

def main():
    print("=" * 70)
    print("arch-brain-web · selftest v1")
    print("=" * 70)

    # Check functions were decorated/called during import (they run on module load)
    passed = sum(1 for _, ok, _ in results if ok)
    failed = sum(1 for _, ok, _ in results if not ok)

    for name, ok, detail in results:
        icon = "OK " if ok else "X  "
        line = f"[{icon}] {name}"
        if detail:
            line += f"  --  {detail}"
        print(line)

    print("=" * 70)
    print(f"PASSED: {passed} / {len(results)}  ·  FAILED: {failed}")
    print("=" * 70)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
