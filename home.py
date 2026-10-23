from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="Social Media Screen Time & Mental Health",
    page_icon="📊",
   layout="wide",
)

overview_page = st.Page(
    "overview.py",
    title="Overview",
    icon="📊",
)

detailed_analysis_page = st.Page(
    "detailed_analysis.py",
    title="Detailed Analysis",
    icon="🔬",
)

insights_page = st.Page(
    "insights.py",
    title="Insights & Recommendations",
    icon="💡",
)


def render_home() -> None:
    illustration = Path(__file__).with_name("screen_time_mental_health.svg").read_text(
        encoding="utf-8"
    )
    st.image(
        illustration,
        caption="How screen time and social media can connect with mental wellbeing",
        use_container_width=True,
    )

    st.markdown(
        """
        <style>
        .hero {
            padding: 2.5rem;
            border-radius: 1rem;
            background: linear-gradient(120deg, #172554, #1d4ed8);
            color: white;
            margin: 0.5rem 0 1.5rem;
        }
        .hero p {
            color: #dbeafe;
            font-size: 1.1rem;
            max-width: 52rem;
        }
        </style>
        <div class="hero">
            <h1>Social Media &amp; Mental Health</h1>
            <p>
                Explore how daily screen time relates to sleep, self-esteem,
                anxiety, and mood across different groups.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.page_link(
        overview_page,
        label="Open the dashboard overview",
        icon="📊",
    )
    st.page_link(
        detailed_analysis_page,
        label="Explore detailed analysis",
        icon="🔬",
    )
    st.page_link(
        insights_page,
        label="View insights and recommendations",
        icon="💡",
    )

    st.subheader("Explore the dashboard")
    st.write(
        "Use the Overview page to see participant-level summary metrics and "
        "interactive charts. The sidebar lets you move between screen time, "
        "mental health, correlation, and demographic analyses."
    )

    sections = st.columns(4)
    section_details = (
        ("📱 Screen time", "Compare daily screen use across age groups."),
        ("🧠 Mental health", "Explore self-esteem and wellbeing measures."),
        ("🔗 Correlations", "Examine screen time alongside health scores."),
        ("👥 Demographics", "See participant distributions by group."),
    )
    for column, (title, description) in zip(sections, section_details):
        with column:
            st.markdown(f"#### {title}")
            st.caption(description)


home_page = st.Page(
    render_home,
    title="Home",
    icon="🏠",
    default=True,
)

current_page = st.navigation(
    [home_page, overview_page, detailed_analysis_page, insights_page]
)
current_page.run()
