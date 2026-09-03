import streamlit as st
import pandas as pd

from spreedb import SpreeDB


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="NEXA Triage | Operations Console",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# CUSTOM CSS
# =============================================================================

st.markdown(
    """
<style>

.stApp {
    background:
        radial-gradient(circle at 80% 0%, #172554 0%, transparent 35%),
        radial-gradient(circle at 10% 20%, #0f172a 0%, transparent 40%),
        #020617;
}

/* Remove excessive top spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0b1120;
    border-right: 1px solid rgba(255,255,255,0.08);
}

.sidebar-brand {
    font-size: 1.7rem;
    font-weight: 800;
    color: #f8fafc;
    margin-bottom: 4px;
}

.sidebar-subtitle {
    color: #94a3b8;
    font-size: 0.85rem;
}

/* Hero */
.hero {
    background:
        linear-gradient(
            135deg,
            rgba(15,23,42,0.96),
            rgba(15,23,42,0.72)
        );
    border: 1px solid rgba(96,165,250,0.20);
    border-radius: 22px;
    padding: 42px 32px;
    text-align: center;
    margin-bottom: 26px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.25);
}

.hero-title {
    font-size: 3rem;
    font-weight: 850;
    letter-spacing: -1px;
    background: linear-gradient(
        90deg,
        #60a5fa,
        #22d3ee,
        #a78bfa
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 1.05rem;
    margin-top: 12px;
}

/* Section headings */
.section-title {
    font-size: 1.45rem;
    font-weight: 800;
    color: #f8fafc;
    margin-bottom: 4px;
}

.section-description {
    color: #94a3b8;
    font-size: 0.9rem;
    margin-bottom: 18px;
}

/* Cards */
.panel {
    background: rgba(15,23,42,0.72);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 18px;
}

/* Status pills */
.status-active {
    background: rgba(16,185,129,0.15);
    color: #6ee7b7;
    border: 1px solid rgba(16,185,129,0.25);
    padding: 7px 14px;
    border-radius: 999px;
    font-weight: 700;
    display: inline-block;
}

.status-idle {
    background: rgba(100,116,139,0.15);
    color: #cbd5e1;
    border: 1px solid rgba(148,163,184,0.20);
    padding: 7px 14px;
    border-radius: 999px;
    font-weight: 700;
    display: inline-block;
}

/* Operational labels */
.signal-label {
    color: #64748b;
    font-size: 0.72rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.signal-value {
    color: #f8fafc;
    font-size: 1.4rem;
    font-weight: 800;
    margin-top: 4px;
}

/* Footer */
.footer {
    text-align: center;
    color: #64748b;
    font-size: 0.8rem;
    padding: 12px;
}

</style>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# INITIALIZE DATABASE
# =============================================================================

if "db" not in st.session_state:
    st.session_state.db = SpreeDB()

db = st.session_state.db


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def database_dataframe():
    """Convert database contents into a DataFrame."""

    if not db.db:
        return pd.DataFrame(columns=["Key", "Value"])

    return pd.DataFrame(
        [
            {
                "Key": key,
                "Value": value,
            }
            for key, value in db.db.items()
        ]
    )


def transition_dataframe():
    """Convert Markov transition telemetry into a DataFrame."""

    rows = []

    for source, destinations in db.cache.transitions.items():

        total = sum(destinations.values())

        for destination, count in destinations.items():

            probability = (
                (count / total) * 100
                if total > 0
                else 0
            )

            rows.append(
                {
                    "From Key": source,
                    "To Key": destination,
                    "Transitions": count,
                    "Probability (%)": round(
                        probability,
                        1,
                    ),
                }
            )

    return pd.DataFrame(rows)


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:

    st.markdown(
        """
<div class="sidebar-brand">
🛡️ NEXA TRIAGE
</div>

<div class="sidebar-subtitle">
Operational Intelligence Console
</div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown("### 📡 System Telemetry")

    st.metric(
        "Active Records",
        len(db.db),
    )

    st.metric(
        "Unique Values",
        len(db.value_counts),
    )

    st.metric(
        "Transaction Depth",
        len(db.transaction_stack),
    )

    st.metric(
        "Learned Access States",
        len(db.cache.transitions),
    )

    st.divider()

    st.markdown("### 🔐 Transaction Status")

    if db.transaction_stack:

        st.markdown(
            '<span class="status-active">● ACTIVE</span>',
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            '<span class="status-idle">● STANDBY</span>',
            unsafe_allow_html=True,
        )

    st.divider()

    st.caption(
        "NEXA Triage Operations Console"
    )

    st.caption(
        "Operational state powered by "
        "the SpreeDB persistence layer."
    )


# =============================================================================
# HERO
# =============================================================================

st.markdown(
    """
<div class="hero">
<div class="hero-title">
NEXA TRIAGE OPERATIONAL CONTROL
</div>

<div class="hero-subtitle">
Deterministic RAG Routing •
Local Llama 3 Grounding •
Regex Risk Engine
</div>
</div>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# SYSTEM OVERVIEW
# =============================================================================

st.markdown(
    """
<div class="section-title">
📡 Operational Overview
</div>

<div class="section-description">
Current runtime state and internal intelligence telemetry.
</div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        "🗂️ Records",
        len(db.db),
    )

with m2:
    st.metric(
        "🔢 Unique Values",
        len(db.value_counts),
    )

with m3:
    st.metric(
        "🔄 Transactions",
        len(db.transaction_stack),
    )

with m4:
    st.metric(
        "🧠 Learned States",
        len(db.cache.transitions),
    )


st.divider()


# =============================================================================
# OPERATIONAL CONTROL
# =============================================================================

left, right = st.columns([0.9, 1.1])


# =============================================================================
# LEFT — CONTROL CENTER
# =============================================================================

with left:

    st.markdown(
        """
<div class="section-title">
⚡ Control Center
</div>

<div class="section-description">
Execute deterministic data operations against the active runtime state.
</div>
        """,
        unsafe_allow_html=True,
    )

    operation = st.selectbox(
        "Operation",
        [
            "SET",
            "GET",
            "UNSET",
            "COUNT",
        ],
    )


    # -------------------------------------------------------------------------
    # SET
    # -------------------------------------------------------------------------

    if operation == "SET":

        key = st.text_input(
            "Record Key",
            placeholder="customer_id",
            key="set_key",
        )

        value = st.text_input(
            "Record Value",
            placeholder="priority",
            key="set_value",
        )

        if st.button(
            "💾 WRITE RECORD",
            use_container_width=True,
        ):

            if key.strip():

                db.set(
                    key.strip(),
                    value,
                )

                st.success(
                    f"Record written successfully: "
                    f"{key.strip()}"
                )

            else:

                st.error(
                    "A record key is required."
                )


    # -------------------------------------------------------------------------
    # GET
    # -------------------------------------------------------------------------

    elif operation == "GET":

        key = st.text_input(
            "Record Key",
            placeholder="customer_id",
            key="get_key",
        )

        if st.button(
            "🔍 READ RECORD",
            use_container_width=True,
        ):

            if key.strip():

                clean_key = key.strip()

                value = db.get(
                    clean_key
                )

                if value is None:

                    st.warning(
                        "No record found for this key."
                    )

                else:

                    st.success(
                        f"Resolved value → {value}"
                    )

                prediction = db.cache.predict(
                    clean_key
                )

                if prediction:

                    st.info(
                        f"🧠 Access prediction → "
                        f"'{prediction}'"
                    )

            else:

                st.error(
                    "A record key is required."
                )


    # -------------------------------------------------------------------------
    # UNSET
    # -------------------------------------------------------------------------

    elif operation == "UNSET":

        key = st.text_input(
            "Record Key",
            placeholder="customer_id",
            key="unset_key",
        )

        if st.button(
            "🗑️ REMOVE RECORD",
            use_container_width=True,
        ):

            if key.strip():

                db.unset(
                    key.strip()
                )

                st.success(
                    f"Record removed: {key.strip()}"
                )

            else:

                st.error(
                    "A record key is required."
                )


    # -------------------------------------------------------------------------
    # COUNT
    # -------------------------------------------------------------------------

    elif operation == "COUNT":

        value = st.text_input(
            "Value",
            placeholder="high_priority",
            key="count_value",
        )

        if st.button(
            "🔢 COUNT MATCHES",
            use_container_width=True,
        ):

            count = db.count(
                value
            )

            st.success(
                f"Matching records → {count}"
            )


# =============================================================================
# RIGHT — LIVE STATE
# =============================================================================

with right:

    st.markdown(
        """
<div class="section-title">
📊 Live Operational State
</div>

<div class="section-description">
Current contents of the active in-memory state.
</div>
        """,
        unsafe_allow_html=True,
    )

    df = database_dataframe()

    if df.empty:

        st.info(
            "Runtime state is currently empty."
        )

    else:

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown(
        """
<div class="section-title">
📈 Value Frequency Index
</div>

<div class="section-description">
O(1) frequency lookup maintained by the database engine.
</div>
        """,
        unsafe_allow_html=True,
    )

    if db.value_counts:

        frequency_df = pd.DataFrame(
            [
                {
                    "Value": value,
                    "Count": count,
                }
                for value, count
                in db.value_counts.items()
            ]
        )

        st.dataframe(
            frequency_df,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No indexed values available."
        )


st.divider()


# =============================================================================
# TRANSACTION CONTROL
# =============================================================================

st.markdown(
    """
<div class="section-title">
🔄 Transaction Control
</div>

<div class="section-description">
Manage nested state changes using BEGIN, COMMIT and ROLLBACK semantics.
</div>
    """,
    unsafe_allow_html=True,
)

t1, t2, t3 = st.columns(3)


with t1:

    if st.button(
        "▶️ BEGIN",
        use_container_width=True,
    ):

        db.begin()

        st.success(
            f"Transaction level "
            f"{len(db.transaction_stack)} started."
        )

        st.rerun()


with t2:

    if st.button(
        "✅ COMMIT",
        use_container_width=True,
    ):

        try:

            db.commit()

            st.success(
                "Transaction committed."
            )

            st.rerun()

        except ValueError:

            st.error(
                "No active transaction."
            )


with t3:

    if st.button(
        "↩️ ROLLBACK",
        use_container_width=True,
    ):

        try:

            db.rollback()

            st.warning(
                "Transaction rolled back."
            )

            st.rerun()

        except ValueError:

            st.error(
                "No active transaction."
            )


st.divider()


# =============================================================================
# ACCESS PATTERN INTELLIGENCE
# =============================================================================

st.markdown(
    """
<div class="section-title">
🧠 Access Pattern Intelligence
</div>

<div class="section-description">
Markov-chain telemetry learned from sequential record retrieval.
</div>
    """,
    unsafe_allow_html=True,
)

transition_df = transition_dataframe()

if transition_df.empty:

    st.info(
        "No access transitions recorded yet. "
        "Execute multiple READ operations to generate telemetry."
    )

else:

    st.dataframe(
        transition_df,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "The predictive cache records sequential GET access "
        "patterns and identifies the most probable next key."
    )


st.divider()


# =============================================================================
# DEMONSTRATION / SYSTEM TEST
# =============================================================================

st.markdown(
    """
<div class="section-title">
🧪 System Demonstration
</div>

<div class="section-description">
Populate a controlled test scenario and demonstrate the predictive runtime.
</div>
    """,
    unsafe_allow_html=True,
)


if st.button(
    "🚀 RUN SYSTEM DEMO",
    use_container_width=True,
):

    # Reset runtime

    st.session_state.db = SpreeDB()

    db = st.session_state.db


    # Populate controlled records

    db.set(
        "customer_alpha",
        "high_priority",
    )

    db.set(
        "customer_beta",
        "normal_priority",
    )

    db.set(
        "customer_gamma",
        "high_priority",
    )


    # Generate access-pattern telemetry

    db.get("customer_alpha")
    db.get("customer_beta")

    db.get("customer_alpha")
    db.get("customer_beta")

    db.get("customer_alpha")
    db.get("customer_gamma")


    st.success(
        "System demonstration completed."
    )

    st.rerun()


# =============================================================================
# FOOTER
# =============================================================================

st.divider()

st.markdown(
    """
<div class="footer">
NEXA TRIAGE • Operational Intelligence Console
<br>
Deterministic Routing • Local Grounding • Risk Analysis
</div>
    """,
    unsafe_allow_html=True,
)
