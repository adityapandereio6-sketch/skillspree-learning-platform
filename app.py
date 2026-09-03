import streamlit as st
import pandas as pd

from spreedb import SpreeDB


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="SpreeDB | Interactive Database",
    page_icon="🗄️",
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
        background: radial-gradient(
            circle at 50% 0%,
            #172554 0%,
            #020617 55%
        );
    }

    .hero {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 20px;
        padding: 32px;
        text-align: center;
        margin-bottom: 25px;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
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
        margin-top: 10px;
    }

    .card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 0.8rem;
        text-transform: uppercase;
        font-weight: 700;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 1.6rem;
        font-weight: 800;
        margin-top: 6px;
    }

    .status-active {
        background: #065f46;
        color: white;
        padding: 6px 14px;
        border-radius: 999px;
        font-weight: 700;
        display: inline-block;
    }

    .status-idle {
        background: #334155;
        color: white;
        padding: 6px 14px;
        border-radius: 999px;
        font-weight: 700;
        display: inline-block;
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
    """Convert database dictionary into a DataFrame."""
    if not db.db:
        return pd.DataFrame(columns=["Key", "Value"])

    return pd.DataFrame(
        [
            {"Key": key, "Value": value}
            for key, value in db.db.items()
        ]
    )


def transition_dataframe():
    """Convert Markov transitions into a DataFrame."""
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
                    "Probability (%)": round(probability, 1),
                }
            )

    return pd.DataFrame(rows)


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:

    st.title("🗄️ SpreeDB")

    st.caption(
        "Interactive in-memory database engine"
    )

    st.divider()

    st.subheader("📊 Database Statistics")

    st.metric(
        "Stored Keys",
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
        "Markov States",
        len(db.cache.transitions),
    )

    st.divider()

    st.subheader("🔄 Transaction Status")

    if db.transaction_stack:

        st.markdown(
            '<span class="status-active">ACTIVE TRANSACTION</span>',
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            '<span class="status-idle">NO ACTIVE TRANSACTION</span>',
            unsafe_allow_html=True,
        )

    st.divider()

    st.caption(
        "Python • Transactions • "
        "Predictive Cache • Persistence"
    )


# =============================================================================
# HERO HEADER
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
# TOP METRICS
# =============================================================================

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "🗄️ Keys",
    len(db.db),
)

m2.metric(
    "🔢 Unique Values",
    len(db.value_counts),
)

m3.metric(
    "🔄 Transactions",
    len(db.transaction_stack),
)

m4.metric(
    "🧠 Cache States",
    len(db.cache.transitions),
)


st.divider()


# =============================================================================
# DATABASE OPERATIONS
# =============================================================================

left, right = st.columns([1, 1.2])


with left:

    st.subheader("⚡ Database Operations")

    operation = st.selectbox(
        "Select Operation",
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
            "Key",
            placeholder="username",
            key="set_key",
        )

        value = st.text_input(
            "Value",
            placeholder="Aditya",
            key="set_value",
        )

        if st.button(
            "💾 Execute SET",
            use_container_width=True,
        ):

            if key.strip():

                db.set(
                    key.strip(),
                    value,
                )

                st.success(
                    f"SET successful → {key} = {value}"
                )

            else:

                st.error(
                    "Please enter a key."
                )


    # -------------------------------------------------------------------------
    # GET
    # -------------------------------------------------------------------------

    elif operation == "GET":

        key = st.text_input(
            "Key",
            placeholder="username",
            key="get_key",
        )

        if st.button(
            "🔍 Execute GET",
            use_container_width=True,
        ):

            if key.strip():

                value = db.get(
                    key.strip()
                )

                if value is None:

                    st.warning(
                        "(nil) — Key not found"
                    )

                else:

                    st.success(
                        f"Value → {value}"
                    )

                prediction = db.cache.predict(
                    key.strip()
                )

                if prediction:

                    st.info(
                        f"🧠 Predictive Cache: "
                        f"Next likely key → '{prediction}'"
                    )

            else:

                st.error(
                    "Please enter a key."
                )


    # -------------------------------------------------------------------------
    # UNSET
    # -------------------------------------------------------------------------

    elif operation == "UNSET":

        key = st.text_input(
            "Key",
            placeholder="username",
            key="unset_key",
        )

        if st.button(
            "🗑️ Execute UNSET",
            use_container_width=True,
        ):

            if key.strip():

                db.unset(
                    key.strip()
                )

                st.success(
                    f"UNSET completed → {key}"
                )

            else:

                st.error(
                    "Please enter a key."
                )


    # -------------------------------------------------------------------------
    # COUNT
    # -------------------------------------------------------------------------

    elif operation == "COUNT":

        value = st.text_input(
            "Value to Count",
            placeholder="developer",
            key="count_value",
        )

        if st.button(
            "🔢 Execute COUNT",
            use_container_width=True,
        ):

            count = db.count(
                value
            )

            st.success(
                f"COUNT('{value}') → {count}"
            )


# =============================================================================
# DATABASE STATE
# =============================================================================

with right:

    st.subheader("📊 Live Database State")

    df = database_dataframe()

    if df.empty:

        st.info(
            "Database is currently empty."
        )

    else:

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    st.subheader(
        "📈 O(1) Value Frequency Index"
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
            "No value frequencies yet."
        )


st.divider()


# =============================================================================
# TRANSACTION CONTROL
# =============================================================================

st.subheader(
    "🔄 Nested Transaction Control"
)

t1, t2, t3 = st.columns(3)


with t1:

    if st.button(
        "▶️ BEGIN",
        use_container_width=True,
    ):

        db.begin()

        st.success(
            f"Transaction started "
            f"(Level {len(db.transaction_stack)})"
        )


with t2:

    if st.button(
        "✅ COMMIT",
        use_container_width=True,
    ):

        try:

            db.commit()

            st.success(
                "Transaction committed successfully."
            )

        except ValueError:

            st.error(
                "NO ACTIVE TRANSACTION"
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

        except ValueError:

            st.error(
                "NO ACTIVE TRANSACTION"
            )


st.divider()


# =============================================================================
# MARKOV CACHE TELEMETRY
# =============================================================================

st.subheader(
    "🧠 Markov Chain Predictive Cache Telemetry"
)

transition_df = transition_dataframe()

if transition_df.empty:

    st.info(
        "No access transitions recorded yet. "
        "Perform multiple GET operations to train the predictive cache."
    )

else:

    st.dataframe(
        transition_df,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "The predictive cache learns sequential GET access patterns "
        "and recommends the most probable next key."
    )


st.divider()


# =============================================================================
# DEMO SCENARIO
# =============================================================================

st.subheader(
    "🧪 Run Demonstration Scenario"
)

st.write(
    "Automatically populate the database and train "
    "the Markov Chain predictive cache."
)


if st.button(
    "🚀 Run SpreeDB Demo",
    use_container_width=True,
):

    # Reset database

    st.session_state.db = SpreeDB()

    db = st.session_state.db


    # Populate database

    db.set(
        "alice",
        "developer",
    )

    db.set(
        "bob",
        "developer",
    )

    db.set(
        "charlie",
        "manager",
    )


    # Train predictive cache

    db.get("alice")
    db.get("bob")

    db.get("alice")
    db.get("bob")

    db.get("alice")
    db.get("charlie")


    st.success(
        "Demo completed successfully!"
    )

    st.rerun()


# =============================================================================
# FOOTER
# =============================================================================

st.divider()

st.caption(
    "SpreeDB • Python In-Memory Database • "
    "Nested Transactions • O(1) Frequency Index • "
    "Markov Predictive Cache"
)
