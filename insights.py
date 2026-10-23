from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


DATA_PATH = Path(__file__).with_name(
    "social_media_screentime_mental_health_2026.csv"
)
CHART_COLORS = ["#2563EB", "#14B8A6", "#F59E0B", "#8B5CF6", "#F43F5E"]
df = pd.read_csv(DATA_PATH)


def style_figure(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Segoe UI, sans-serif", size=13, color="#334155"),
        title=dict(x=0.02, xanchor="left", font=dict(size=20, color="#0F172A")),
        margin=dict(l=24, r=24, t=72, b=24),
        hoverlabel=dict(bgcolor="#0F172A", font_color="#FFFFFF"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=False, linecolor="#E2E8F0", ticks="outside")
    fig.update_yaxes(showgrid=True, gridcolor="#E2E8F0", ticks="outside")
    return fig


st.title("💡 Insights & Recommendations")
st.write(
    "A data-led summary of screen-time patterns and how they vary alongside "
    "sleep and wellbeing measures. Findings are descriptive and should not be "
    "interpreted as evidence that screen time causes a health outcome."
)

screen_time_cutoff = df["daily_screen_hours"].quantile(0.75)
df["screen_time_group"] = df["daily_screen_hours"].ge(screen_time_cutoff).map(
    {True: "Highest screen-time quartile", False: "Other participants"}
)
high_use = df.loc[df["screen_time_group"] == "Highest screen-time quartile"]
other_use = df.loc[df["screen_time_group"] == "Other participants"]

if high_use.empty or other_use.empty:
    st.warning("There are not enough screen-time values to compare participant groups.")
    st.stop()

high_sleep = high_use["avg_sleep_hours"].mean()
other_sleep = other_use["avg_sleep_hours"].mean()
sleep_difference = high_sleep - other_sleep
high_anxiety = high_use["anxiety_score_0to27"].mean()
other_anxiety = other_use["anxiety_score_0to27"].mean()
anxiety_difference = high_anxiety - other_anxiety
high_at_risk_share = high_use["wellbeing_band"].eq("At-risk").mean() * 100
other_at_risk_share = other_use["wellbeing_band"].eq("At-risk").mean() * 100
at_risk_difference = high_at_risk_share - other_at_risk_share

metric_columns = st.columns(4)
metric_columns[0].metric("Participants", f"{len(df):,}")
metric_columns[1].metric(
    "Highest-use cutoff", f"{screen_time_cutoff:.1f} hrs/day"
)
metric_columns[2].metric(
    "Avg. screen time in highest quartile",
    f"{high_use['daily_screen_hours'].mean():.1f} hrs/day",
)
metric_columns[3].metric(
    "Using screen-time limits",
    f"{df['uses_screen_time_limits'].eq('Yes').mean():.0%}",
)

st.divider()
st.subheader("What stands out in this dataset?")

insight_columns = st.columns(3)
with insight_columns[0]:
    st.markdown("#### 🌙 Sleep")
    st.metric(
        "High-use group vs others",
        f"{sleep_difference:+.1f} hrs/night",
        help="Difference in average sleep hours; negative means less sleep in the highest-use group.",
    )
    st.caption(
        f"Highest-use group: {high_sleep:.1f} hrs/night · "
        f"Other participants: {other_sleep:.1f} hrs/night"
    )

with insight_columns[1]:
    st.markdown("#### 🧠 Anxiety score")
    st.metric(
        "High-use group vs others",
        f"{anxiety_difference:+.1f} points",
        help="Difference in mean anxiety score, on the dataset's 0–27 scale.",
    )
    st.caption(
        f"Highest-use group: {high_anxiety:.1f}/27 · "
        f"Other participants: {other_anxiety:.1f}/27"
    )

with insight_columns[2]:
    st.markdown("#### 💬 Wellbeing band")
    st.metric(
        "At-risk share difference",
        f"{at_risk_difference:+.1f} pp",
        help="Percentage-point difference in the share labelled At-risk.",
    )
    st.caption(
        f"Highest-use group: {high_at_risk_share:.1f}% · "
        f"Other participants: {other_at_risk_share:.1f}%"
    )

st.subheader("Wellbeing mix by screen-time group")
wellbeing_order = (
    df["wellbeing_band"].value_counts().index.tolist()
)
wellbeing_mix = (
    df.groupby(["screen_time_group", "wellbeing_band"], observed=True)
    .size()
    .rename("participants")
    .reset_index()
)
wellbeing_mix["share"] = wellbeing_mix.groupby(
    "screen_time_group", observed=True
)["participants"].transform(lambda counts: counts / counts.sum() * 100)

mix_chart = px.bar(
    wellbeing_mix,
    x="screen_time_group",
    y="share",
    color="wellbeing_band",
    barmode="stack",
    category_orders={"wellbeing_band": wellbeing_order},
    color_discrete_sequence=CHART_COLORS,
    title="Share of participants in each wellbeing band",
    labels={
        "screen_time_group": "Screen-time group",
        "share": "Participants (%)",
        "wellbeing_band": "Wellbeing band",
    },
    hover_data={"participants": True, "share": ":.1f"},
)
mix_chart.update_yaxes(range=[0, 100], ticksuffix="%")
style_figure(mix_chart)
st.plotly_chart(mix_chart, use_container_width=True)

st.subheader("Recommendations to consider")
if sleep_difference < -0.2:
    sleep_recommendation = (
        "The highest-use group reports less sleep on average. Consider a small "
        "screen-free wind-down pilot before bedtime, then measure whether sleep "
        "habits change. This comparison does not show that screen use caused "
        "the difference."
    )
elif sleep_difference > 0.2:
    sleep_recommendation = (
        "The highest-use group reports more sleep on average in this dataset. "
        "Avoid assuming screen time is reducing sleep; explore timing of use "
        "and other factors before choosing an intervention."
    )
else:
    sleep_recommendation = (
        "Average sleep is similar between the groups. Focus on individual "
        "bedtime routines and monitor sleep alongside screen habits rather "
        "than assuming a group-wide relationship."
    )

if at_risk_difference > 5:
    wellbeing_recommendation = (
        "The highest-use group has a larger share labelled At-risk. Make "
        "wellbeing resources easy to find and offer supportive, non-judgmental "
        "check-ins; the band is not a diagnosis."
    )
else:
    wellbeing_recommendation = (
        "The At-risk share is not notably higher in the highest-use group. "
        "Keep wellbeing support accessible to everyone rather than targeting "
        "people based on screen time alone."
    )

limit_rate = df["uses_screen_time_limits"].eq("Yes").mean()
limit_recommendation = (
    "Fewer than half of participants report using screen-time limits. Offer optional "
    "settings guidance—such as notification controls or app timers—and let "
    "participants choose whether those tools fit their needs."
    if limit_rate < 0.5
    else
    "At least half of participants report using screen-time limits. Evaluate "
    "which strategies they find helpful and share those approaches without "
    "treating a limit as a substitute for wellbeing support."
)

recommendation_columns = st.columns(3)
with recommendation_columns[0]:
    st.markdown("#### 1. Support healthy routines")
    st.write(sleep_recommendation)
with recommendation_columns[1]:
    st.markdown("#### 2. Keep support accessible")
    st.write(wellbeing_recommendation)
with recommendation_columns[2]:
    st.markdown("#### 3. Make tools optional")
    st.write(limit_recommendation)

st.info(
    "These are population-level observations from this dataset, not clinical "
    "guidance. Group differences may reflect other factors, and results should "
    "not be used to diagnose or judge individuals."
)

with st.expander("How these insights are calculated"):
    st.markdown(
        f"""
        - **Highest screen-time quartile:** participants at or above the 75th
          percentile cutoff of **{screen_time_cutoff:.2f} hours/day**.
        - **Comparison group:** all remaining participants.
        - **Sleep and anxiety differences:** mean for the highest-use group
          minus mean for the comparison group.
        - **At-risk share difference:** percentage-point difference between
          groups, using the dataset's `wellbeing_band` label.
        - Percentages and averages are calculated from the full dataset each
          time the page loads.
        """
    )
