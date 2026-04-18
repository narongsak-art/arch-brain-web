"""Minimal theme · just enough CSS to look clean, no brittle tricks"""

import streamlit as st


CSS = """
<style>
  html, body, [class*="st-"] {
    font-family: 'Sarabun', 'Noto Sans Thai', -apple-system, BlinkMacSystemFont, sans-serif;
  }
  .main .block-container { max-width: 1100px; padding-top: 1.5rem; }
  h1, h2, h3 { letter-spacing: -0.01em; font-weight: 700; }
  .ab-hero {
    padding: 28px 24px;
    border-radius: 14px;
    color: #fff;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
    margin-bottom: 18px;
  }
  .ab-hero h1 { color: #fff !important; margin: 0 0 6px 0; font-size: 2em; }
  .ab-hero p { margin: 0; opacity: 0.95; }
  [data-testid="stMetric"] {
    background: rgba(99, 102, 241, 0.04);
    border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 10px;
    padding: 10px 14px;
  }
</style>
"""


def inject():
    """Inject minimal CSS — works on any Streamlit version"""
    st.markdown(CSS, unsafe_allow_html=True)
