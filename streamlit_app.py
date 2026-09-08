import streamlit as st
import subprocess
import sys
from pathlib import Path

from src.pipeline import query_rag, collection
from app.tickets import (
    initialize_ticket_database,
    create_ticket
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Lumen Chat",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
INGEST_SCRIPT = BASE_DIR / "ingest_data.py"


# ============================================================
# INITIALIZE TICKET DATABASE
# ============================================================

initialize_ticket_database()


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "show_dataset" not in st.session_state:
    st.session_state.show_dataset = False

if "show_enquiry" not in st.session_state:
    st.session_state.show_enquiry = False


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

html, body, [data-testid="stAppViewContainer"] {
    background: #090c12 !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

.block-container {
    max-width: 1000px !important;
    padding-top: 0 !important;
    padding-bottom: 100px !important;
}


/* =========================
   NAVIGATION
   ========================= */

.lumen-nav {
    height: 72px;
    border-bottom: 1px solid #272c35;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 42px;
}

.lumen-logo {
    font-size: 22px;
    font-weight: 700;
    color: #f4f5f7;
    letter-spacing: -0.5px;
}

.lumen-logo span {
    color: #e5ad32;
}

.nav-label {
    color: #858c98;
    font-size: 11px;
    letter-spacing: 4px;
    font-weight: 500;
}


/* =========================
   HERO
   ========================= */

.eyebrow {
    color: #e5ad32;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 5px;
    margin-bottom: 25px;
}

.hero-title {
    color: #f1f2f4;
    font-size: clamp(42px, 6vw, 68px);
    font-weight: 500;
    line-height: 1.08;
    letter-spacing: -3px;
    max-width: 850px;
    margin-bottom: 26px;
}

.hero-description {
    color: #969ca8;
    font-size: 16px;
    line-height: 1.7;
    max-width: 720px;
    margin-bottom: 28px;
}


/* =========================
   BUTTONS
   ========================= */

.stButton > button {
    background: #151921 !important;
    color: #e5e7eb !important;
    border: 1px solid #2b313b !important;
    border-radius: 12px !important;
    min-height: 42px !important;
}

.stButton > button:hover {
    border-color: #e5ad32 !important;
    color: #e5ad32 !important;
}


/* =========================
   SUGGESTION BUTTONS
   ========================= */

.suggestion button {
    border-radius: 24px !important;
    text-align: left !important;
    padding-left: 18px !important;
}


/* =========================
   PANELS
   ========================= */

.panel {
    background: #11151d;
    border: 1px solid #292f39;
    border-radius: 18px;
    padding: 25px;
    margin-top: 25px;
    margin-bottom: 25px;
}

.panel-title {
    color: #f0f1f3;
    font-size: 21px;
    font-weight: 600;
}

.panel-description {
    color: #9298a4;
    font-size: 14px;
    line-height: 1.6;
    margin-top: 8px;
}


/* =========================
   DATASET STATS
   ========================= */

.stat-card {
    background: #151921;
    border: 1px solid #292f39;
    border-radius: 14px;
    padding: 18px;
}

.stat-number {
    color: #e5ad32;
    font-size: 28px;
    font-weight: 600;
}

.stat-label {
    color: #858c98;
    font-size: 11px;
    letter-spacing: 1px;
    margin-top: 3px;
}


/* =========================
   CHAT
   ========================= */

[data-testid="stChatMessage"] {
    background: transparent !important;
}

[data-testid="stChatMessageContent"] {
    color: #e8e9ed !important;
    line-height: 1.7;
}


/* =========================
   CHAT INPUT
   ========================= */

[data-testid="stChatInput"] {
    background: #11151d !important;
    border: 1px solid #2b313b !important;
    border-radius: 18px !important;
}

[data-testid="stChatInput"] textarea {
    color: #e8eaee !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #737985 !important;
}


/* =========================
   TICKET
   ========================= */

.ticket-success {
    background: #151c19;
    border: 1px solid #30463a;
    border-radius: 14px;
    padding: 20px;
    margin-top: 20px;
}

.ticket-id {
    color: #e5ad32;
    font-size: 22px;
    font-weight: 700;
    margin-top: 8px;
}


/* =========================
   SOURCE
   ========================= */

.source-text {
    color: #707783;
    font-size: 12px;
    margin-top: 8px;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# NAVIGATION
# ============================================================

nav1, nav2 = st.columns([7, 2])

with nav1:

    st.markdown(
        '<div class="lumen-logo">Lumen <span>chat</span></div>',
        unsafe_allow_html=True
    )

with nav2:

    st.markdown(
        '<div class="nav-label">RETRIEVAL SYSTEM</div>',
        unsafe_allow_html=True
    )


# ============================================================
# NAVIGATION BUTTONS
# ============================================================

col_space, dataset_col, enquiry_col = st.columns(
    [6.5, 1.5, 1.5]
)


with dataset_col:

    if st.button(
        "Datasets",
        use_container_width=True
    ):

        st.session_state.show_dataset = (
            not st.session_state.show_dataset
        )

        st.session_state.show_enquiry = False

        st.rerun()


with enquiry_col:

    if st.button(
        "Enquiry",
        use_container_width=True
    ):

        st.session_state.show_enquiry = (
            not st.session_state.show_enquiry
        )

        st.session_state.show_dataset = False

        st.rerun()


# ============================================================
# DATASET PANEL
# ============================================================

if st.session_state.show_dataset:

    st.markdown(
        """
        <div class="panel">
        <div class="panel-title">Knowledge Base</div>
        <div class="panel-description">
        Manage the FAQ dataset used by the RAG system.
        Initialize it once or reload it whenever the dataset changes.
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    count = collection.count()

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            f"""
            <div class="stat-card">
            <div class="stat-number">{count}</div>
            <div class="stat-label">FAQ DOCUMENTS</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            """
            <div class="stat-card">
            <div class="stat-number">ChromaDB</div>
            <div class="stat-label">VECTOR DATABASE</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            """
            <div class="stat-card">
            <div class="stat-number">MiniLM</div>
            <div class="stat-label">EMBEDDING MODEL</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    init_col, reload_col = st.columns(2)

    # --------------------------------------------------------
    # INITIALIZE
    # --------------------------------------------------------

    with init_col:

        if st.button(
            "Initialize Dataset",
            use_container_width=True
        ):

            if collection.count() > 0:

                st.info(
                    "Dataset is already initialized."
                )

            else:

                with st.spinner(
                    "Initializing dataset..."
                ):

                    result = subprocess.run(
                        [
                            sys.executable,
                            str(INGEST_SCRIPT)
                        ],
                        capture_output=True,
                        text=True,
                        cwd=str(BASE_DIR)
                    )

                if result.returncode == 0:

                    st.success(
                        "Dataset initialized successfully."
                    )

                    st.rerun()

                else:

                    st.error(
                        "Dataset initialization failed."
                    )

                    st.code(result.stderr)


    # --------------------------------------------------------
    # RELOAD
    # --------------------------------------------------------

    with reload_col:

        if st.button(
            "Reload Dataset",
            use_container_width=True
        ):

            with st.spinner(
                "Reloading dataset..."
            ):

                result = subprocess.run(
                    [
                        sys.executable,
                        str(INGEST_SCRIPT)
                    ],
                    capture_output=True,
                    text=True,
                    cwd=str(BASE_DIR)
                )

            if result.returncode == 0:

                st.success(
                    "Dataset reloaded successfully."
                )

                st.rerun()

            else:

                st.error(
                    "Dataset reload failed."
                )

                st.code(result.stderr)


# ============================================================
# ENQUIRY PANEL
# ============================================================

if st.session_state.show_enquiry:

    st.markdown(
        """
        <div class="panel">
        <div class="panel-title">Raise an enquiry</div>
        <div class="panel-description">
        Can't find the answer in the knowledge base?
        Submit your question and a support ticket will be created.
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("enquiry_form"):

        name = st.text_input(
            "Name",
            placeholder="Your name"
        )

        email = st.text_input(
            "Email",
            placeholder="your@email.com"
        )

        question = st.text_area(
            "Question",
            placeholder="Describe what you need help with...",
            height=130
        )

        priority = st.selectbox(
            "Priority",
            [
                "Normal",
                "High",
                "Urgent"
            ]
        )

        submitted = st.form_submit_button(
            "Raise Ticket"
        )

        if submitted:

            if not email.strip():

                st.error(
                    "Please enter your email."
                )

            elif not question.strip():

                st.error(
                    "Please enter your question."
                )

            else:

                ticket_id = create_ticket(
                    customer_name=name,
                    customer_email=email,
                    question=question,
                    priority=priority
                )

                st.markdown(
                    f"""
                    <div class="ticket-success">
                    Your enquiry has been submitted successfully.
                    <div class="ticket-id">{ticket_id}</div>
                    Keep this ticket ID for future reference.
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# ============================================================
# HERO
# ============================================================

if not st.session_state.messages:

    st.markdown(
        '<div class="eyebrow">RETRIEVAL · GROUNDED · CITED</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero-title">
        Ask anything. Answers come<br>
        from your datasets — not thin air.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero-description">
        Your question is matched against your datasets,
        and only the closest entries are used to write
        the answer. Every response is grounded in your
        knowledge base.
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # SUGGESTIONS
    # ========================================================

    st.markdown(
        '<div class="suggestion-title">TRY ASKING</div>',
        unsafe_allow_html=True
    )

    s1, s2 = st.columns(2)

    selected_question = None

    with s1:

        if st.button(
            "What topics does my data cover?",
            use_container_width=True
        ):

            selected_question = (
                "What topics does my data cover?"
            )

        if st.button(
            "What should I know before getting started?",
            use_container_width=True
        ):

            selected_question = (
                "What should I know before getting started?"
            )


    with s2:

        if st.button(
            "Summarise the key points for me",
            use_container_width=True
        ):

            selected_question = (
                "Summarise the key points for me"
            )


    if selected_question:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": selected_question
            }
        )

        st.rerun()


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

prompt = st.chat_input(
    "Ask a question..."
)


if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):

        st.markdown(prompt)


    with st.chat_message("assistant"):

        with st.spinner(
            "Searching your knowledge base..."
        ):

            answer, sources = query_rag(prompt)

        st.markdown(answer)

        if sources:

            st.markdown(
                f"""
                <div class="source-text">
                Grounded in {len(sources)} retrieved dataset source(s).
                </div>
                """,
                unsafe_allow_html=True
            )


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    st.rerun()