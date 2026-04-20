"""Selftest · diagnostic of arch-brain-web v6

Validates without hitting external APIs:
- Python files parse
- Core imports work (streamlit mocked)
- JSON parser handles all 4 input shapes
- 8 presets all structurally valid
- Portfolio HTML generation
- Site SVG rendering
- Prompt building
- KG file integrity

Run: python scripts/selftest.py
Exit code 0 = all pass · non-zero = failures
"""

import json
import re
import subprocess
import sys
import types
from pathlib import Path


REPO = Path(__file__).parent.parent
results: list[tuple[str, bool, str]] = []


def check(name: str):
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


def _install_mock_streamlit():
    st = types.ModuleType("streamlit")

    class _Col:
        def __getattr__(self, name):
            if name in ("text_input", "text_area"):
                return lambda *a, **k: ""
            if name == "multiselect":
                return lambda *a, **k: []
            if name == "button":
                return lambda *a, **k: False
            if name == "number_input":
                return lambda *a, **k: 0.0
            if name == "selectbox" or name == "radio":
                def f(label, options=None, *a, **k):
                    opts = options or (a[0] if a else None)
                    if opts:
                        try:
                            return list(opts)[0]
                        except Exception:
                            pass
                    return ""
                return f
            return _Col()
        def __call__(self, *a, **k):
            return _Col()
        def __enter__(self): return self
        def __exit__(self, *a): pass

    class _M:
        def __getattr__(self, n): return _M()
        def __call__(self, *a, **k):
            if a and isinstance(a[0], (int, list, tuple)):
                n = a[0] if isinstance(a[0], int) else len(a[0])
                return tuple(_Col() for _ in range(n))
            return _M()
        def __enter__(self): return self
        def __exit__(self, *a): pass

    st.cache_data = lambda *a, **k: (a[0] if a and callable(a[0]) else (lambda f: f))
    st.session_state = {}
    st.query_params = {}
    st.text_input = lambda *a, **k: ""
    st.text_area = lambda *a, **k: ""
    st.number_input = lambda *a, **k: 0.0
    st.slider = lambda *a, **k: 0
    st.selectbox = lambda l, o=None, *a, **k: (list(o)[0] if o else "")
    st.radio = lambda l, o=None, *a, **k: (list(o)[0] if o else "")
    st.multiselect = lambda *a, **k: []
    st.file_uploader = lambda *a, **k: None
    st.columns = lambda n: tuple(_Col() for _ in range(n if isinstance(n, int) else len(n)))
    st.button = lambda *a, **k: False
    st.column_config = types.SimpleNamespace(ProgressColumn=lambda *a, **k: _M())
    for n in ["set_page_config", "sidebar", "markdown", "title", "caption",
              "header", "subheader", "info", "success", "warning", "error",
              "divider", "expander", "download_button", "spinner", "rerun",
              "image", "tabs", "write", "code", "dataframe", "json", "metric",
              "progress", "toggle", "status", "empty", "html", "table"]:
        setattr(st, n, _M())
    sys.modules["streamlit"] = st


# ============================================================================
# Checks
# ============================================================================

@check("All Python files parse")
def _t_syntax():
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
        raise AssertionError("\n  ".join(failures))
    count = sum(1 for p in REPO.rglob("*.py")
                 if ".git" not in p.parts and "__pycache__" not in p.parts)
    return f"{count} .py files OK"


@check("Core imports · brain + app")
def _t_imports():
    _install_mock_streamlit()
    sys.path.insert(0, str(REPO))
    import brain
    import app
    return "brain + app imported"


@check("JSON parser · 4 input shapes")
def _t_json():
    sys.path.insert(0, str(REPO))
    import brain
    cases = [
        ('{"k":1}', {"k": 1}),
        ('```json\n{"k":1}\n```', {"k": 1}),
        ('prefix {"k":1} suffix', {"k": 1}),
        ('invalid', None),
    ]
    for inp, expected in cases:
        got = brain.extract_json(inp)
        assert got == expected, f"{inp!r} → {got}, expected {expected}"
    return f"{len(cases)} cases OK"


@check("All 8 presets structurally valid")
def _t_presets():
    sys.path.insert(0, str(REPO))
    import app
    assert len(app.PRESETS) == 8, f"expected 8 presets, got {len(app.PRESETS)}"
    required = {"label", "tagline", "meta", "icon", "gradient", "data"}
    for k, p in app.PRESETS.items():
        missing = required - set(p.keys())
        assert not missing, f"{k} missing {missing}"
        for field in ["name", "land_w", "land_d", "province", "zone",
                      "floors", "bedrooms", "budget"]:
            assert field in p["data"], f"{k}.data missing {field}"
        assert p["gradient"].startswith("linear-gradient")
    return f"8/8 presets valid"


@check("Site SVG generates correctly")
def _t_svg():
    sys.path.insert(0, str(REPO))
    import brain
    svg = brain._render_site_svg(15, 20, "ใต้", 200, 300)
    assert "<svg" in svg
    assert "rotate(-180)" in svg  # south → 180
    assert "ด้านยาว" in svg
    assert "N" in svg  # north marker
    return f"SVG {len(svg)} chars · orientation rotation OK"


@check("Portfolio HTML generation")
def _t_portfolio():
    sys.path.insert(0, str(REPO))
    import brain
    pd = {"name": "Test", "land_w": 15, "land_d": 20, "land_area": 300,
          "orientation": "ใต้", "budget": 8, "floors": "2",
          "bedrooms": "3", "family_size": 4, "has_elderly": "ใช่"}
    data = {
        "summary": {"feasibility": "green", "score": 85, "note": "ok"},
        "metrics": {"land_area_sqm": 300, "far_allowed": 1.5},
        "compliance": {"building_code": {"status": "pass", "note": "ok"}},
        "layers": {"law": {"status": "pass", "score": 90, "findings": []}},
        "rooms": [], "issues": [], "strengths": [],
        "phases": {}, "actions": [],
    }
    html = brain.build_portfolio_html(pd, data, "gemini")
    assert html.startswith("<!DOCTYPE html>")
    assert html.endswith("</html>")
    for kw in ["THAI RESIDENTIAL PORTFOLIO", "EXECUTIVE SUMMARY",
               "Bai+Jamjuree", "window.print()", "Test"]:
        assert kw in html, f"missing {kw}"
    return f"{len(html):,} chars · all key markers present"


@check("Prompt construction · system + user")
def _t_prompts():
    sys.path.insert(0, str(REPO))
    import brain
    sys_p = brain.build_system_prompt()
    pd = {"name": "x", "land_w": 15, "land_d": 20, "land_area": 300,
          "orientation": "ใต้", "topography": "ราบเรียบ",
          "priority": ["งบ"], "grade": "มาตรฐาน"}
    user_p = brain.build_user_prompt(pd)
    assert "FULL KNOWLEDGE" in sys_p
    assert '"phases"' in sys_p
    assert '"compliance"' in sys_p
    assert "ทิศที่ดิน" in user_p
    assert "Grade" in user_p
    return f"system {len(sys_p):,} · user {len(user_p)} chars"


@check("KG integrity · meta matches arrays")
def _t_kg():
    kg_path = REPO / "kg-compact.json"
    if not kg_path.exists():
        raise AssertionError("kg-compact.json missing")
    kg = json.loads(kg_path.read_text(encoding="utf-8"))
    meta = kg.get("meta", {})
    nodes = kg.get("nodes", [])
    edges = kg.get("edges", [])
    assert meta.get("node_count") == len(nodes)
    node_ids = {n["id"] for n in nodes}
    bad = [e for e in edges if e["from"] not in node_ids or e["to"] not in node_ids]
    assert not bad, f"{len(bad)} bad edges"
    return f"{len(nodes)} nodes · {len(edges)} edges · valid"


@check("CSS has no fragile selectors")
def _t_css():
    sys.path.insert(0, str(REPO))
    import app
    bad = [".css-", 'class*="st-', '.element-container']
    for b in bad:
        assert b not in app.CSS, f"fragile: {b}"
    assert "data-testid" in app.CSS
    return f"CSS {len(app.CSS):,} chars · clean"


@check("All 3 views render · no crash")
def _t_views():
    sys.path.insert(0, str(REPO))
    import streamlit as st
    import app
    st.session_state.update({"history": [], "current": None, "pins": []})
    app.view_create()
    app.view_studio()
    app.view_explore()
    return "create + studio + explore"


# ============================================================================
# Runner
# ============================================================================

def main():
    print("=" * 72)
    print("arch-brain-web v6 · selftest")
    print("=" * 72)
    passed = sum(1 for _, ok, _ in results if ok)
    failed = sum(1 for _, ok, _ in results if not ok)
    for name, ok, detail in results:
        icon = "OK " if ok else "X  "
        line = f"[{icon}] {name}"
        if detail:
            line += f"  -  {detail}"
        print(line)
    print("=" * 72)
    print(f"PASSED: {passed} / {len(results)}  ·  FAILED: {failed}")
    print("=" * 72)
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
