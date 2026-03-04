import streamlit as st
import json
# ---- simple login gate (prototype only) ----
PASSWORD = "blueprintdemo"   # change this if you want

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Blueprint* Access")

    password = st.text_input("Enter password", type="password")

    if st.button("Login"):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")

    st.stop()
# --------------------------------------------
from engine.allocator import allocate
from engine.rationale import generate

# load evidence citations
with open("data/evidence.json") as f:
    EVIDENCE = json.load(f)

# page config and style
st.set_page_config(page_title="Blueprint Budget Allocation Tool", layout="wide")

st.markdown(
    """
    <style>
    body {
        background-color: #D8FF00;
        color: black;
    }
    .stApp {
        background-color: #D8FF00;
    }
    .title {
        font-size: 4rem;
        font-weight: bold;
    }
    .subtitle {
        font-size: 1.5rem;
        margin-bottom: 2rem;
    }
    .input-panel {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# header
st.markdown("<div class='title'>BLUEPRINT*</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Independent media effectiveness for modern marketers</div>", unsafe_allow_html=True)

# layout columns: left for inputs, right for results
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("<div class='input-panel'>", unsafe_allow_html=True)
    st.header("Inputs")

    # quick examples
    example = st.selectbox(
        "Example scenario",
        ["Custom", "Budget £25k / 3m / Performance", "Budget £120k / 6m / Awareness", "Budget £600k / 12m / Growth"],
    )
    if example != "Custom":
        if example.startswith("Budget £25k"):
            total_budget = 25000
            duration = 3
            objective = "Performance"
        elif example.startswith("Budget £120k"):
            total_budget = 120000
            duration = 6
            objective = "Awareness"
        else:
            total_budget = 600000
            duration = 12
            objective = "Growth"
    else:
        total_budget = st.number_input("Total Marketing Budget (£)", min_value=0.0, value=50000.0, step=1000.0)
        duration = st.number_input("Campaign Duration (months)", min_value=1, value=6, step=1)
        objective = st.selectbox("Objective", ["Awareness", "Growth", "Performance"])

    if example == "Custom":
        business_type = st.selectbox("Business Type", ["Ecommerce", "Local Service", "DTC", "Other"])
        risk_tolerance = st.selectbox("Risk Tolerance", ["Low", "Medium", "High"])
    else:
        business_type = st.selectbox("Business Type", ["Ecommerce", "Local Service", "DTC", "Other"], index=0)
        risk_tolerance = st.selectbox("Risk Tolerance", ["Low", "Medium", "High"], index=1)

    generate_button = st.button("Generate Media Allocation")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if generate_button:
        allocations, monthly_budget = allocate(total_budget, duration, objective, business_type, risk_tolerance)
        # build table data
        import pandas as pd

        # assemble dataframe with both formatted and numeric values
        rows = []
        for ch, v in allocations.items():
            rows.append(
                {
                    "Channel": ch,
                    "% Allocation": v["pct"] * 100,  # numeric for chart
                    "Total Budget": f"£{v['total']:.0f}",
                    "Monthly Budget": f"£{v['monthly']:.0f}",
                }
            )
        df = pd.DataFrame(rows)

        st.subheader("Recommended Media Allocation")
        # show formatted table with percent strings
        df_display = df.copy()
        df_display["% Allocation"] = df_display["% Allocation"].map(lambda x: f"{x:.1f}%")
        st.table(df_display)

        # bar chart uses numeric percent field
        st.bar_chart(df.set_index('Channel')["% Allocation"])

        # rationale
        rationale = generate(objective, business_type, risk_tolerance, list(allocations.keys()))
        st.subheader("Strategic Rationale")
        for b in rationale:
            st.markdown(f"- {b}")

        # evidence
        st.subheader("Evidence Base")
        for e in EVIDENCE:
            st.markdown(f"- {e}")
    else:
        st.markdown("<em>Click 'Generate Media Allocation' to see results.</em>", unsafe_allow_html=True)
