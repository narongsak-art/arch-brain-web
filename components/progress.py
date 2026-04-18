"""Progress stages · replace spinner with multi-stage status display"""

import streamlit as st
import time


class AnalysisProgress:
    """Context manager that renders progress stages during analysis"""

    STAGES = [
        ("load_kb", "📚 โหลด Knowledge Graph + Full Knowledge"),
        ("build_prompt", "✍ เตรียม system prompt + 5-layer context"),
        ("call_llm", "🧠 เรียก AI วิเคราะห์โครงการ"),
        ("parse", "📊 ประมวลผลและจัดรูปรายงาน"),
    ]

    def __init__(self, provider: str):
        self.provider = provider
        self.status = None
        self.current = 0
        self._start = None

    def __enter__(self):
        provider_name = self.provider.title()
        self.status = st.status(
            f"🧠 กำลังวิเคราะห์ด้วย {provider_name}...",
            expanded=True,
        )
        self.status.__enter__()
        self._start = time.time()
        return self

    def advance(self, stage_key: str, detail: str = ""):
        """Mark a stage as done and start the next"""
        for i, (key, label) in enumerate(self.STAGES):
            if key == stage_key:
                prefix = "✅" if i < self.current else "▶"
                msg = f"{prefix} {label}"
                if detail:
                    msg += f" — _{detail}_"
                st.write(msg)
                self.current = i + 1
                break

    def done(self, success: bool = True):
        elapsed = time.time() - self._start if self._start else 0
        if success:
            self.status.update(
                label=f"✅ วิเคราะห์เสร็จใน {elapsed:.1f} วิ",
                state="complete",
                expanded=False,
            )
        else:
            self.status.update(
                label=f"❌ วิเคราะห์ล้มเหลว ({elapsed:.1f} วิ)",
                state="error",
                expanded=True,
            )

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.done(success=False)
        if self.status:
            self.status.__exit__(exc_type, exc_val, exc_tb)
        return False
