from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


DATA_PATH = Path(__file__).with_name(
    "social_media_screentime_mental_health_2026.csv"
)
CHART_COLORS = ["#2563EB", "#14B8A6", "#F59E0B", "#8B5CF6", "#F43F5E", "#0EA5E9"]

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


st.title("🔬 Detailed Analysis")
st.write(
    "Explore how screen habits, sleep, and wellbeing measures vary together. "
    "Use the filters to focus the analysis on a group of participants."
)

st.sidebar.subheader("Detailed analysis filters")
selected_genders = st.sidebar.multiselect(
    "Gender",
    options=sorted(df["gender"].dropna().unique().tolist()),
    default=sorted(df["gender"].dropna().unique().tolist()),
)
selected_regions = st.sidebar.multiselect(
    "Region",
    options=sorted(df["region"].dropna().unique().tolist()),
    default=sorted(df["region"].dropna().unique().tolist()),
)
selected_wellbeing = st.sidebar.multiselect(
    "Wellbeing band",
    options=sorted(df["wellbeing_band"].dropna().unique().tolist()),
    default=sorted(df["wellbeing_band"].dropna().unique().tolist()),
)

age_min = int(df["age"].min())
age_max = int(df["age"].max())
age_range = st.sidebar.slider(
    "Age range",
    min_value=age_min,
    max_value=age_max,
    value=(age_min, age_max),
)
screen_min = float(df["daily_screen_hours"].min())
screen_max = float(df["daily_screen_hours"].max())
screen_range = st.sidebar.slider(
    "Daily screen time (hours)",
    min_value=screen_min,
    max_value=screen_max,
    value=(screen_min, screen_max),
    step=0.5,
)

filtered_df = df.loc[
    df["gender"].isin(selected_genders)
    & df["region"].isin(selected_regions)
    & df["wellbeing_band"].isin(selected_wellbeing)
    & df["age"].between(*age_range)
    & df["daily_screen_hours"].between(*screen_range)
].copy()

if filtered_df.empty:
    st.warning("No participants match these filters. Adjust the selections to continue.")
    st.stop()

st.caption(f"Analysis includes {len(filtered_df):,} of {len(df):,} participants.")

metric_columns = st.columns(4)
metric_columns[0].metric(
    "Average screen time", f"{filtered_df['daily_screen_hours'].mean():.1f} hrs/day"
)
metric_columns[1].metric(
    "Average sleep", f"{filtered_df['avg_sleep_hours'].mean():.1f} hrs/night"
)
metric_columns[2].metric(
    "Average anxiety", f"{filtered_df['anxiety_score_0to27'].mean():.1f} / 27"
)
metric_columns[3].metric(
    "Average self-esteem", f"{filtered_df['self_esteem_1to10'].mean():.1f} / 10"
)

st.divider()
st.subheader("Screen time and sleep")
scatter_data = filtered_df
if len(scatter_data) > 5000:
    scatter_data = scatter_data.sample(n=5000, random_state=42)
    st.caption("The scatter plot samples 5,000 participants for readability.")

scatter = px.scatter(
    scatter_data,
    x="daily_screen_hours",
    y="avg_sleep_hours",
    color="wellbeing_band",
    hover_data=["age", "gender", "region"],
    labels={
        "daily_screen_hours": "Daily screen time (hours)",
        "avg_sleep_hours": "Average sleep (hours)",
        "wellbeing_band": "Wellbeing band",
    },
    title="Daily Screen Time vs. Average Sleep",
    color_discrete_sequence=CHART_COLORS,
    opacity=0.68,
)
scatter.update_traces(marker=dict(size=8, line=dict(width=0)))
style_figure(scatter)
st.plotly_chart(scatter, use_container_width=True)

st.subheader("Wellbeing differences")
wellbeing_summary = (
    filtered_df.groupby("wellbeing_band", observed=True)
    .agg(
        participants=("participant_id", "count"),
        screen_time=("daily_screen_hours", "mean"),
        sleep=("avg_sleep_hours", "mean"),
        anxiety=("anxiety_score_0to27", "mean"),
        self_esteem=("self_esteem_1to10", "mean"),
    )
    .reset_index()
)

summary_chart = wellbeing_summary.melt(
    id_vars="wellbeing_band",
    value_vars=["screen_time", "sleep", "anxiety", "self_esteem"],
    var_name="measure",
    value_name="average",
)
summary_chart["measure"] = summary_chart["measure"].map(
    {
        "screen_time": "Screen time (hours)",
        "sleep": "Sleep (hours)",
        "anxiety": "Anxiety (out of 27)",
        "self_esteem": "Self-esteem (out of 10)",
    }
)
wellbeing_fig = px.bar(
    summary_chart,
    x="wellbeing_band",
    y="average",
    color="measure",
    barmode="group",
    title="Average measures by wellbeing band",
    labels={"wellbeing_band": "Wellbeing band", "average": "Average score"},
    color_discrete_sequence=CHART_COLORS,
)
style_figure(wellbeing_fig)
st.plotly_chart(wellbeing_fig, use_container_width=True)
st.caption(
    "Measures use different scales, so compare each color across wellbeing bands "
    "rather than comparing the height of different colors."
)

st.subheader("Associations between wellbeing measures")
correlation_columns = {
    "Screen time (hours)": "daily_screen_hours",
    "Sleep (hours)": "avg_sleep_hours",
    "Anxiety": "anxiety_score_0to27",
    "Low mood": "low_mood_score_0to27",
    "Self-esteem": "self_esteem_1to10",
    "Life satisfaction": "life_satisfaction_1to10",
    "Loneliness": "loneliness_1to10",
    "FOMO": "fomo_1to10",
}
correlation_data = filtered_df[list(correlation_columns.values())].rename(
    columns={value: key for key, value in correlation_columns.items()}
)
correlation_matrix = correlation_data.corr()
heatmap = px.imshow(
    correlation_matrix,
    text_auto=".2f",
    color_continuous_scale="RdBu",
    color_continuous_midpoint=0,
    zmin=-1,
    zmax=1,
    aspect="auto",
    title="Correlation matrix",
    labels={"x": "Measure", "y": "Measure", "color": "Correlation"},
)
style_figure(heatmap)
st.plotly_chart(heatmap, use_container_width=True)
st.caption(
    "Correlation describes association in this dataset; it does not establish "
    "that one measure causes another."
)

if len(filtered_df) >= 2:
    screen_sleep_corr = filtered_df[
        ["daily_screen_hours", "avg_sleep_hours"]
    ].corr().iloc[0, 1]
    screen_anxiety_corr = filtered_df[
        ["daily_screen_hours", "anxiety_score_0to27"]
    ].corr().iloc[0, 1]
    if pd.notna(screen_sleep_corr) and pd.notna(screen_anxiety_corr):
        st.info(
            "In the selected participants, screen time has a "
            f"{'positive' if screen_sleep_corr > 0 else 'negative'} association "
            f"with sleep (r = {screen_sleep_corr:.2f}) and a "
            f"{'positive' if screen_anxiety_corr > 0 else 'negative'} association "
            f"with anxiety (r = {screen_anxiety_corr:.2f}). These are descriptive "
            "relationships, not evidence of cause and effect."
        )

with st.expander("View the filtered participant data"):
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
