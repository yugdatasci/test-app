import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple
from pathlib import Path
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Investor Risk Profiling Tool (Risk-O-Meter Demo)",
    page_icon="📈",
    layout="wide"
)

DB_PATH = Path("riskometer.db")

# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class Question:
    id: str
    category: str
    text: str
    options: List[str]
    # higher weight => more influence on total risk score
    weight: float = 1.0


@dataclass
class RiskProfile:
    name: str
    min_score: float
    max_score: float
    description: str


# ============================================================
# QUESTIONS & PROFILES DEFINITION
# ============================================================

QUESTIONS: List[Question] = [
    Question(
        id="horizon",
        category="Investment Horizon",
        text="How long can you stay invested without needing this money?",
        options=[
            "Less than 1 year",
            "1–3 years",
            "3–5 years",
            "5–10 years",
            "More than 10 years",
        ],
        weight=1.3,
    ),
    Question(
        id="income_stability",
        category="Income Stability",
        text="How stable is your primary source of income?",
        options=[
            "Very unstable (frequent gaps/uncertainty)",
            "Somewhat unstable",
            "Neutral / can vary",
            "Mostly stable",
            "Very stable (secure job/business)",
        ],
        weight=1.2,
    ),
    Question(
        id="experience",
        category="Market Experience",
        text="How experienced are you with equity / market investments?",
        options=[
            "No experience",
            "Very limited (just starting)",
            "Some experience (1–3 years)",
            "Experienced (3–7 years)",
            "Highly experienced (7+ years)",
        ],
        weight=1.0,
    ),
    Question(
        id="loss_tolerance",
        category="Loss Tolerance",
        text="How would you react if your investment fell by 20% in a year?",
        options=[
            "Immediately sell everything – I can’t tolerate it",
            "Sell part of it and move to safer options",
            "Wait for some time and then decide",
            "Stay invested and review later",
            "Invest more – see it as an opportunity",
        ],
        weight=1.5,
    ),
    Question(
        id="goal",
        category="Goals",
        text="What best describes your main investment goal?",
        options=[
            "Capital protection (no loss)",
            "Slightly better than FD returns",
            "Balanced growth & safety",
            "High growth with some risk",
            "Maximum growth – I accept high risk",
        ],
        weight=1.4,
    ),
    Question(
        id="liquidity",
        category="Liquidity Need",
        text="How often might you need to withdraw a part of this investment?",
        options=[
            "Very frequently (monthly)",
            "Sometimes (few times a year)",
            "Occasionally (once a year)",
            "Rarely",
            "Almost never",
        ],
        weight=1.0,
    ),
    Question(
        id="news_reaction",
        category="Behavioural Reaction",
        text="If media/news predicts a market crash, what will you likely do?",
        options=[
            "Exit all risky investments",
            "Reduce risky investments significantly",
            "Reduce a bit, but stay mostly invested",
            "Do nothing, stay with the plan",
            "Consider adding more if valuation is attractive",
        ],
        weight=1.3,
    ),
]

# option index (0–4) -> base points
BASE_POINTS = [1, 2, 3, 4, 5]

RISK_PROFILES: List[RiskProfile] = [
    RiskProfile(
        "Conservative",
        0,
        20,
        "You prioritise capital protection and low volatility. A debt-heavy portfolio "
        "and capital preservation strategies are suitable."
    ),
    RiskProfile(
        "Moderately Conservative",
        20.1,
        28,
        "You accept limited risk for slightly better returns. A mix of high-quality debt "
        "with some diversified equity exposure is appropriate."
    ),
    RiskProfile(
        "Moderate",
        28.1,
        36,
        "You balance risk and return. A well-diversified portfolio with a meaningful equity "
        "component alongside debt and gold fits you."
    ),
    RiskProfile(
        "Moderately Aggressive",
        36.1,
        43,
        "You can tolerate volatility in pursuit of higher long-term growth. An equity-heavy "
        "portfolio with some allocation to stabilising assets is suitable."
    ),
    RiskProfile(
        "Aggressive",
        43.1,
        50,
        "You have high risk tolerance and typically a long investment horizon. A predominantly "
        "equity-oriented portfolio, including thematic or small-cap exposure, may be suitable."
    ),
]

SAMPLE_ALLOCATION: Dict[str, Dict[str, int]] = {
    "Conservative": {"Debt": 80, "Equity": 15, "Gold/Alt": 5},
    "Moderately Conservative": {"Debt": 60, "Equity": 35, "Gold/Alt": 5},
    "Moderate": {"Debt": 40, "Equity": 50, "Gold/Alt": 10},
    "Moderately Aggressive": {"Debt": 25, "Equity": 65, "Gold/Alt": 10},
    "Aggressive": {"Debt": 10, "Equity": 80, "Gold/Alt": 10},
}


# ============================================================
# DATABASE LAYER
# ============================================================

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user_id TEXT,
            name TEXT,
            age INTEGER,
            invest_amount REAL,
            total_score REAL,
            profile TEXT,
            risk_percent REAL,
            details_json TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_assessment(
    user_id: str,
    name: str,
    age: int,
    invest_amount: float,
    total_score: float,
    profile: str,
    risk_percent: float,
    details: Dict,
):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO assessments (
            timestamp, user_id, name, age, invest_amount,
            total_score, profile, risk_percent, details_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(),
            user_id,
            name,
            age,
            invest_amount,
            total_score,
            profile,
            risk_percent,
            json.dumps(details),
        ),
    )
    conn.commit()
    conn.close()


def load_assessments(user_id: str = None) -> pd.DataFrame:
    conn = get_conn()
    query = "SELECT * FROM assessments"
    params = ()
    if user_id:
        query += " WHERE user_id = ?"
        params = (user_id,)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


# ============================================================
# RISK ENGINE
# ============================================================

def compute_scores(
    answers: Dict[str, str]
) -> Tuple[float, float, Dict[str, float], Dict[str, Dict[str, float]]]:
    """
    answers: mapping question_id -> chosen_option_text
    returns:
        weighted_total,
        max_possible_score,
        category_avg (for charts),
        question_scores (for debugging / report)
    """
    weighted_total = 0.0
    max_possible = 0.0

    category_scores: Dict[str, List[float]] = {}
    question_scores: Dict[str, Dict[str, float]] = {}

    for q in QUESTIONS:
        chosen = answers.get(q.id)
        if chosen is None:
            continue
        try:
            idx = q.options.index(chosen)
        except ValueError:
            idx = 0
        base = BASE_POINTS[idx]
        score = base * q.weight

        weighted_total += score
        max_possible += BASE_POINTS[-1] * q.weight  # 5 * weight

        category_scores.setdefault(q.category, []).append(score)
        question_scores[q.id] = {
            "category": q.category,
            "question": q.text,
            "choice": chosen,
            "base_points": base,
            "weight": q.weight,
            "weighted_score": score,
        }

    category_avg = {
        cat: sum(vals) / len(vals) for cat, vals in category_scores.items()
    }

    return weighted_total, max_possible, category_avg, question_scores


def classify_profile(score: float) -> RiskProfile:
    for p in RISK_PROFILES:
        if p.min_score <= score <= p.max_score:
            return p
    # Fallback to nearest profile
    return sorted(RISK_PROFILES, key=lambda x: abs((x.min_score + x.max_score) / 2 - score))[0]


# ============================================================
# REPORT GENERATION
# ============================================================

def build_text_report(
    name: str,
    age: int,
    invest_amount: float,
    total_score: float,
    max_score: float,
    profile: RiskProfile,
    risk_percent: float,
    category_avg: Dict[str, float],
    question_scores: Dict[str, Dict[str, float]],
) -> str:
    lines = []
    lines.append("Investor Risk Profiling Report (Risk-O-Meter Demo)")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Name          : {name or 'Not provided'}")
    lines.append(f"Age           : {age if age else 'Not provided'}")
    lines.append(f"Investment Amt: ₹{invest_amount:,.2f}")
    lines.append(f"Assessment On : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("Overall Risk Summary")
    lines.append("-" * 70)
    lines.append(f"Total Score   : {total_score:.2f} / {max_score:.2f}")
    lines.append(f"Risk Profile  : {profile.name}")
    lines.append(f"Risk Percent  : {risk_percent:.1f}% of maximum possible score")
    lines.append("")
    lines.append("Profile Interpretation")
    lines.append("-" * 70)
    lines.append(profile.description)
    lines.append("")
    lines.append("Category-wise Average Scores (higher = higher risk tolerance)")
    lines.append("-" * 70)
    for cat, avg in category_avg.items():
        lines.append(f"- {cat}: {avg:.2f}")
    lines.append("")
    lines.append("Question-wise Details")
    lines.append("-" * 70)
    for q in QUESTIONS:
        qs = question_scores.get(q.id)
        if not qs:
            continue
        lines.append(f"Question : {qs['question']}")
        lines.append(f"Category : {qs['category']}")
        lines.append(f"Answer   : {qs['choice']}")
        lines.append(
            f"Score    : base={qs['base_points']}  weight={qs['weight']}  "
            f"weighted={qs['weighted_score']:.2f}"
        )
        lines.append("-" * 40)
    lines.append("")
    lines.append("Disclaimer")
    lines.append("-" * 70)
    lines.append(
        "This report is generated by a prototype risk profiling model for academic/"
        "internship purposes. It does not constitute financial advice and should not be "
        "used as the sole basis for investment decisions."
    )
    return "\n".join(lines)


# ============================================================
# UI HELPERS
# ============================================================

def show_sample_allocation(profile_name: str):
    alloc = SAMPLE_ALLOCATION.get(profile_name)
    if not alloc:
        st.info("No sample allocation available for this profile.")
        return

    st.subheader("📊 Illustrative Asset Allocation (Non-Advice)")
    col1, col2 = st.columns([1, 1])

    with col1:
        st.write("**Indicative allocation split:**")
        for asset, pct in alloc.items():
            st.write(f"- **{asset}**: {pct}%")

    with col2:
        df_alloc = pd.DataFrame(
            {"Asset": list(alloc.keys()), "Percentage": list(alloc.values())}
        )
        fig = px.pie(df_alloc, names="Asset", values="Percentage", hole=0.45)
        fig.update_layout(showlegend=True)
        st.plotly_chart(fig, use_container_width=True)


def ensure_session_state():
    if "user_id" not in st.session_state:
        st.session_state.user_id = ""
    if "answers" not in st.session_state:
        st.session_state.answers = {}


# ============================================================
# MAIN PAGES
# ============================================================

def page_assessment():
    st.title("📈 Investor Risk Profiling Tool (Risk-O-Meter Demo)")

    st.caption(
        "Prototype built using Python & Streamlit for academic / internship purposes. "
        "**Not** an official RBI/SEBI tool."
    )

    with st.expander("👤 User Identification (for history & tracking)", expanded=True):
        st.session_state.user_id = st.text_input(
            "User ID / Email / Mobile (for identifying your assessments)",
            value=st.session_state.user_id,
            help="Used only locally to group your assessments; not sent to any server.",
        )

    with st.form("assessment_form"):
        st.subheader("Basic Details")
        name = st.text_input("Name (optional)")
        age = st.number_input("Age", min_value=18, max_value=100, value=25, step=1)
        invest_amount = st.number_input(
            "Approx. amount you plan to invest (₹)",
            min_value=0.0,
            step=10000.0,
            value=0.0,
        )

        st.markdown("---")
        st.subheader("📝 Risk Preference Questionnaire")

        answers: Dict[str, str] = {}
        for q in QUESTIONS:
            st.markdown(f"**{q.text}**")
            choice = st.radio(
                label=f"{q.id}_label",
                options=q.options,
                key=f"q_{q.id}",
                horizontal=True,
                label_visibility="collapsed",
            )
            answers[q.id] = choice
            st.markdown("")

        submitted = st.form_submit_button("🔍 Calculate My Risk Profile")

    if submitted:
        if not st.session_state.user_id.strip():
            st.warning("Please enter a User ID so that your history can be saved.")
            return

        total_score, max_score, category_avg, question_scores = compute_scores(answers)
        profile = classify_profile(total_score)
        risk_percent = round((total_score / max_score) * 100, 1)

        st.success(f"Assessment completed for **{name or 'Investor'}**.")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Risk Score", f"{total_score:.2f} / {max_score:.2f}")
        with col2:
            st.metric("Risk Profile", profile.name)
        with col3:
            st.metric("Risk Percentile", f"{risk_percent}%")

        st.markdown("### 🧩 Interpretation")
        st.write(profile.description)

        st.markdown("### 📊 Category-wise Risk Tolerance")
        df_cat = pd.DataFrame(
            {
                "Category": list(category_avg.keys()),
                "Average Score (weighted)": list(category_avg.values()),
            }
        )
        fig_bar = px.bar(
            df_cat,
            x="Category",
            y="Average Score (weighted)",
            range_y=[0, max(df_cat["Average Score (weighted)"]) + 1],
            text="Average Score (weighted)",
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig_bar, use_container_width=True)

        show_sample_allocation(profile.name)

        # Build report & download
        st.markdown("### 📄 Downloadable Risk Report")
        report_text = build_text_report(
            name=name,
            age=age,
            invest_amount=invest_amount,
            total_score=total_score,
            max_score=max_score,
            profile=profile,
            risk_percent=risk_percent,
            category_avg=category_avg,
            question_scores=question_scores,
        )
        st.download_button(
            label="⬇️ Download Text Report",
            data=report_text,
            file_name=f"risk_profile_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
        )

        # Save to DB
        detail_payload = {
            "name": name,
            "age": age,
            "invest_amount": invest_amount,
            "answers": answers,
            "category_avg": category_avg,
            "question_scores": question_scores,
        }
        save_assessment(
            user_id=st.session_state.user_id,
            name=name,
            age=age,
            invest_amount=invest_amount,
            total_score=total_score,
            profile=profile.name,
            risk_percent=risk_percent,
            details=detail_payload,
        )

        st.info("Your assessment has been stored locally in a SQLite database.")


def page_history():
    st.title("📚 Assessment History & Insights")

    user_filter = st.text_input(
        "Filter by User ID (leave blank for all)",
        value=st.session_state.user_id,
        help="Use the same ID you entered while taking the assessment.",
    )

    df_hist = load_assessments(user_filter.strip() or None)

    if df_hist.empty:
        st.warning("No assessments found for the given filter.")
        return

    with st.expander("Raw Assessment Records", expanded=False):
        st.dataframe(
            df_hist.sort_values("timestamp", ascending=False),
            use_container_width=True,
            height=300,
        )

    st.markdown("### 📈 Risk Score Over Time")
    fig_line = px.line(
        df_hist.sort_values("timestamp"),
        x="timestamp",
        y="total_score",
        color="user_id",
        markers=True,
        labels={"timestamp": "Date", "total_score": "Total Score"},
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("### 🧮 Profile Distribution")
    fig_pie = px.pie(
        df_hist,
        names="profile",
        title="Frequency of Each Risk Profile",
    )
    st.plotly_chart(fig_pie, use_container_width=True)


def page_admin():
    st.title("🛠️ Admin / Developer View (Local)")

    st.info(
        "This section is meant for debugging / demonstration purposes only. "
        "All data is stored locally in a SQLite database file."
    )

    if st.button("Show Database Path"):
        st.write(f"Database file: `{DB_PATH.resolve()}`")

    df_all = load_assessments(None)
    st.write(f"Total records: {len(df_all)}")

    if not df_all.empty:
        st.dataframe(df_all.tail(20), use_container_width=True, height=300)

    if st.button("⚠️ Delete ALL records (use carefully)"):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM assessments")
        conn.commit()
        conn.close()
        st.success("All records deleted. Refresh the page to see updated state.")


def page_about():
    st.title("ℹ️ About This Risk-O-Meter Demo")

    st.markdown("### 🎯 Objective")
    st.write(
        """
        This application is a **prototype investor risk profiling tool** developed as part of an
        internship / academic initiative. Its goals are to:
        
        - Demonstrate how **behavioural and financial inputs** can be combined
          to estimate an investor's **risk tolerance**.
        - Show how such tools can support **investor education**, **suitability assessment**,
          and **protection from mis-selling**.
        """
    )

    st.markdown("### 🧠 Policy Relevance")
    st.write(
        """
        - Retail investors sometimes invest in products **not aligned** with their true risk capacity.  
        - Misalignment can lead to **panic selling**, **wealth erosion**, and **stress on household balance sheets**.  
        - Tools like this can complement broader efforts in:
          - **Financial literacy**
          - **Consumer protection**
          - **Long-term financial stability**
        """
    )

    st.markdown("### 📐 Methodology (Simplified)")
    st.write(
        """
        1. The questionnaire covers dimensions like **investment horizon**, **income stability**,  
           **market experience**, **loss tolerance**, **liquidity needs**, and **behavioural reaction**.
        2. Each response is mapped to a base score from **1 (low risk tolerance) to 5 (high)**.
        3. Each question also has a **weight** reflecting its importance; the final score is
           a **weighted sum**.
        4. The total score is mapped to five broad profiles:
           - Conservative  
           - Moderately Conservative  
           - Moderate  
           - Moderately Aggressive  
           - Aggressive  
        5. For each profile, an **illustrative asset allocation** (Equity/Debt/Gold/Alternatives) is shown.
        
        > This scoring model is **illustrative** and does **not replicate** any official RBI/SEBI methodology.
        """
    )

    st.markdown("### ⚠️ Disclaimer")
    st.write(
        """
        - This tool is for **educational and demonstrative** purposes only.  
        - It is **not registered** as an investment advisory / research product.  
        - Outputs **must not** be treated as investment recommendations.  
        - Users should consult a **qualified financial advisor** before making decisions.
        """
    )

    st.markdown("### 🛠️ Tech Stack")
    st.write(
        "- Python\n"
        "- Streamlit (user interface)\n"
        "- Plotly (interactive charts)\n"
        "- SQLite (local database for assessments)\n"
        "- Dataclasses-based risk engine"
    )

    st.markdown("### 👨‍🎓 Project Information")
    st.write(
        """
        - **Student:** Yug Ajit Dubey  
        - **Programme:** BCA  
        - **Institution:** Shailendra Education Society  
        - **Context:** Prototype for internship / learning project related to risk profiling.
        """
    )


# ============================================================
# MAIN APP
# ============================================================

def main():
    init_db()
    ensure_session_state()

    with st.sidebar:
        st.title("📊 Risk-O-Meter Demo")
        page = st.radio(
            "Navigation",
            ["Risk Assessment", "History & Insights", "Admin / Dev", "About"],
        )
        st.markdown("---")
        st.caption(
            "Prototype tool. For academic demonstration only.\n"
            "All data is stored locally on this machine."
        )

    if page == "Risk Assessment":
        page_assessment()
    elif page == "History & Insights":
        page_history()
    elif page == "Admin / Dev":
        page_admin()
    elif page == "About":
        page_about()


if __name__ == "__main__":
    main()
