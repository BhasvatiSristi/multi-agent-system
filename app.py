import streamlit as st
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MultiAgent Research System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

/* ── base ── */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #0a0a0f;
    color: #e8e4dc;
}
.stApp { background-color: #0a0a0f; }

/* ── header ── */
.hero {
    text-align: center;
    padding: 3rem 0 2rem 0;
    border-bottom: 1px solid #1e1e2e;
    margin-bottom: 2.5rem;
}
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -2px;
    background: linear-gradient(135deg, #c8f04f 0%, #4fd6f0 60%, #f04fb8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.1;
}
.hero-sub {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: #555570;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 0.6rem;
}

/* ── input area ── */
.stTextInput > div > div > input {
    background: #111120 !important;
    border: 1px solid #2a2a40 !important;
    border-radius: 12px !important;
    color: #e8e4dc !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.9rem 1.2rem !important;
    transition: border-color 0.2s;
}
.stTextInput > div > div > input:focus {
    border-color: #c8f04f !important;
    box-shadow: 0 0 0 2px rgba(200,240,79,0.15) !important;
}
.stTextInput label {
    color: #888 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

/* ── button ── */
.stButton > button {
    background: linear-gradient(135deg, #c8f04f, #4fd6f0) !important;
    color: #0a0a0f !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 1px !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    width: 100% !important;
    transition: opacity 0.2s, transform 0.15s !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}
.stButton > button:disabled {
    opacity: 0.4 !important;
    cursor: not-allowed !important;
}

/* ── step cards ── */
.step-card {
    background: #111120;
    border: 1px solid #1e1e30;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s;
}
.step-card.active   { border-color: #c8f04f; }
.step-card.done     { border-color: #4fd6f0; }
.step-card.idle     { border-color: #1e1e30; }

.step-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}
.step-label.active  { color: #c8f04f; }
.step-label.done    { color: #4fd6f0; }
.step-label.idle    { color: #333350; }

.step-title {
    font-size: 1.05rem;
    font-weight: 700;
}
.step-title.active  { color: #e8e4dc; }
.step-title.done    { color: #9ba3b8; }
.step-title.idle    { color: #2a2a40; }

.step-icon { font-size: 1.5rem; float: right; margin-top: -0.2rem; }

/* ── result panels ── */
.result-panel {
    background: #0d0d1a;
    border: 1px solid #1e1e30;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-top: 1.5rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.82rem;
    line-height: 1.75;
    color: #b0b8cc;
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 340px;
    overflow-y: auto;
}
.result-panel::-webkit-scrollbar { width: 5px; }
.result-panel::-webkit-scrollbar-track { background: transparent; }
.result-panel::-webkit-scrollbar-thumb { background: #2a2a40; border-radius: 4px; }

.panel-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #555570;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── status badge ── */
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 99px;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 700;
}
.badge-running { background: rgba(200,240,79,0.12); color: #c8f04f; border: 1px solid rgba(200,240,79,0.25); }
.badge-done    { background: rgba(79,214,240,0.12); color: #4fd6f0; border: 1px solid rgba(79,214,240,0.25); }
.badge-error   { background: rgba(240,79,184,0.12); color: #f04fb8; border: 1px solid rgba(240,79,184,0.25); }

/* ── final report ── */
.final-report {
    background: linear-gradient(135deg, #0f1220 0%, #0d1a10 100%);
    border: 1px solid #c8f04f33;
    border-radius: 16px;
    padding: 2rem;
    margin-top: 1.5rem;
    color: #ddeedd;
    line-height: 1.9;
    font-size: 0.95rem;
}

/* ── divider ── */
.divider { border: none; border-top: 1px solid #1a1a2a; margin: 1.5rem 0; }

/* ── hide streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <p class="hero-sub">Multi-Agent Research System</p>
    <h1 class="hero-title">Deep Research,<br>Automated.</h1>
</div>
""", unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────────────────────
for key in ["running", "state", "current_step", "error"]:
    if key not in st.session_state:
        st.session_state[key] = None if key in ["state", "error"] else (False if key == "running" else 0)

STEPS = [
    ("🔍", "Search Agent",   "Scouring the web for recent, reliable sources"),
    ("📄", "Reader Agent",   "Scraping top URL for deeper content"),
    ("✍️", "Writer Chain",  "Drafting the structured research report"),
    ("🧐", "Critic Chain",  "Reviewing & scoring the report"),
]

# ── Layout ────────────────────────────────────────────────────────────────────
left, right = st.columns([1, 1.6], gap="large")

with left:
    st.markdown("#### Research Topic")
    topic = st.text_input(
        "TOPIC",
        placeholder="e.g. The impact of AI on the job market",
        label_visibility="collapsed",
        disabled=st.session_state.running,
        key="topic_input",
    )

    run_btn = st.button(
        "⚡  Run Pipeline" if not st.session_state.running else "⏳  Running…",
        disabled=st.session_state.running or not topic.strip(),
    )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("#### Pipeline Steps")

    step_placeholders = []
    for i, (icon, title, desc) in enumerate(STEPS):
        ph = st.empty()
        step_placeholders.append(ph)

    def render_steps(current_step, done_steps=set()):
        for i, (icon, title, desc) in enumerate(STEPS):
            if i in done_steps:
                status, cls = "✓ Done", "done"
            elif i == current_step:
                status, cls = "● Active", "active"
            else:
                status, cls = "", "idle"

            step_placeholders[i].markdown(f"""
<div class="step-card {cls}">
    <span class="step-icon">{icon}</span>
    <div class="step-label {cls}">{status or f"Step {i+1}"}</div>
    <div class="step-title {cls}">{title}</div>
    <div style="font-size:0.78rem; color:#3a3a55; margin-top:0.2rem;">{desc}</div>
</div>
""", unsafe_allow_html=True)

    render_steps(-1)  # initial idle state

# ── Right panel ───────────────────────────────────────────────────────────────
with right:
    st.markdown("#### Live Output")
    output_area = st.empty()
    output_area.markdown("""
<div style="color:#2a2a40; font-family:'Space Mono',monospace; font-size:0.82rem; 
     padding:3rem 1rem; text-align:center; border:1px dashed #1a1a2a; border-radius:14px;">
    Results will stream here as each agent completes its work.
</div>
""", unsafe_allow_html=True)

# ── Pipeline runner ───────────────────────────────────────────────────────────
if run_btn and topic.strip():
    st.session_state.running = True
    st.session_state.state = {}
    st.session_state.error = None
    done_steps = set()
    results_html = ""

    def update_output(html):
        output_area.markdown(html, unsafe_allow_html=True)

    try:
        # ── Step 0: Search ──
        render_steps(0, done_steps)
        search_agent = build_search_agent()
        search_result = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
        })
        st.session_state.state["search_results"] = search_result["messages"][-1].content
        done_steps.add(0)
        render_steps(1, done_steps)

        results_html = f"""
<div class="panel-header">🔍 &nbsp;Search Results</div>
<div class="result-panel">{st.session_state.state['search_results']}</div>
"""
        update_output(results_html)

        # ── Step 1: Reader ──
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{st.session_state.state['search_results'][:800]}"
            )]
        })
        st.session_state.state["scraped_content"] = reader_result["messages"][-1].content
        done_steps.add(1)
        render_steps(2, done_steps)

        results_html += f"""
<br>
<div class="panel-header">📄 &nbsp;Scraped Content</div>
<div class="result-panel">{st.session_state.state['scraped_content']}</div>
"""
        update_output(results_html)

        # ── Step 2: Writer ──
        research_combined = (
            f"SEARCH RESULTS:\n{st.session_state.state['search_results']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{st.session_state.state['scraped_content']}"
        )
        st.session_state.state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined,
        })
        done_steps.add(2)
        render_steps(3, done_steps)

        results_html += f"""
<br>
<div class="panel-header">✍️ &nbsp;Generated Report</div>
<div class="final-report">{st.session_state.state['report']}</div>
"""
        update_output(results_html)

        # ── Step 3: Critic ──
        st.session_state.state["feedback"] = critic_chain.invoke({
            "report": st.session_state.state["report"]
        })
        done_steps.add(3)
        render_steps(-1, done_steps)

        results_html += f"""
<br>
<div class="panel-header">🧐 &nbsp;Critic Feedback</div>
<div class="result-panel">{st.session_state.state['feedback']}</div>
"""
        update_output(results_html)

    except Exception as e:
        st.session_state.error = str(e)
        st.error(f"Pipeline error: {e}")

    finally:
        st.session_state.running = False

# ── Download button if report exists ─────────────────────────────────────────
if st.session_state.state and st.session_state.state.get("report"):
    with left:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        report_text = (
            f"# Research Report: {st.session_state.get('topic_input', '')}\n\n"
            f"## Report\n{st.session_state.state.get('report', '')}\n\n"
            f"## Critic Feedback\n{st.session_state.state.get('feedback', '')}"
        )
        st.download_button(
            label="⬇  Download Report",
            data=report_text,
            file_name="research_report.md",
            mime="text/markdown",
        )