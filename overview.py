from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

pio.templates.default = "plotly_white"

chart_colors = ["#2563EB", "#14B8A6", "#F59E0B", "#8B5CF6", "#F43F5E", "#0EA5E9"]


# Load dataset
df = pd.read_csv(Path(__file__).with_name("social_media_screentime_mental_health_2026.csv"))


def style_figure(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Segoe UI, sans-serif", size=13, color="#334155"),
        title=dict(x=0.02, xanchor="left", font=dict(size=21, color="#0F172A")),
        margin=dict(l=24, r=24, t=76, b=24),
        hoverlabel=dict(bgcolor="#0F172A", font_color="#FFFFFF"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )
    fig.update_xaxes(showgrid=False, linecolor="#E2E8F0", ticks="outside")
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E2E8F0",
        zerolinecolor="#CBD5E1",
        ticks="outside",
    )
    return fig


# Sidebar navigation
st.sidebar.title("📂 Dashboard Navigation")
page = st.sidebar.radio("Go to:", 
                        ["Overview 🗂️",
                         "Screen Time Trends 📱📈",
                         "Mental Health Trends 🧠💭",
                         "Correlation Analysis 🔗📊",
                         "Demographics 👥🌍"])
# KPI Cards (Overview)
if page == "Overview 🗂️":
    st.title("🌌 Social Media & Mental Health Dashboard")
     
    daily_screen_hours = df["daily_screen_hours"].mean()
    self_esteem_1to10 = df["self_esteem_1to10"].mean()
    avg_sleep_hours = df["avg_sleep_hours"].mean()
    anxiety_score_0to27 = df["anxiety_score_0to27"].mean()
    low_mood_score_0to27 = df["low_mood_score_0to27"].mean()
    participant_id = len(df)

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("📱 Avg. Screen Time", f"{daily_screen_hours:.2f} hrs")
    col2.metric("😊 Avg. Self-Esteem", f"{self_esteem_1to10:.2f}")
    col3.metric("😴 Avg. Sleep Hours", f"{avg_sleep_hours:.2f} hrs")
    col4.metric("😟 Avg. Anxiety Score", f"{anxiety_score_0to27:.2f}")
    col5.metric("😔 Avg. Low Mood Score", f"{low_mood_score_0to27:.2f}")
    col6.metric("👥 Total Participants", participant_id)

 
 
# Screen Time Trends
elif page == "Screen Time Trends 📱📈":
    st.header("📱📈 Screen Time Trends")
    screen_time_by_age = (
        df.groupby("age", as_index=False, observed=True)["daily_screen_hours"]
        .mean()
    )
    fig = px.bar(
        screen_time_by_age,
        x="age",
        y="daily_screen_hours",
        title="Average Daily Screen Time by Age",
        labels={"age": "Age", "daily_screen_hours": "Hours per day"},
        color_discrete_sequence=[chart_colors[0]],
    )
    fig.update_traces(
        marker_line_width=0,
        opacity=0.92,
        hovertemplate="<b>%{x}</b><br>Average screen time: %{y:.1f} hrs/day<extra></extra>",
    )
    style_figure(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.write("Compare average daily screen time across age groups.")

# Mental Health Trends
elif page == "Mental Health Trends 🧠💭":
    st.header("🧠💭 Mental Health Trends")
    self_esteem_by_age = (
        df.groupby("age", as_index=False, observed=True)["self_esteem_1to10"]
        .mean()
    )
    fig = px.bar(
        self_esteem_by_age,
        x="age",
        y="self_esteem_1to10",
        title="Average Self-Esteem by Age",
        labels={"age": "Age", "self_esteem_1to10": "Self-esteem (out of 10)"},
        color_discrete_sequence=[chart_colors[1]],
    )
    fig.update_traces(
        marker_line_width=0,
        opacity=0.92,
        hovertemplate="<b>%{x}</b><br>Average self-esteem: %{y:.1f}/10<extra></extra>",
    )
    style_figure(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.write("Compare average self-esteem scores across age groups.")

# Correlation Analysis
elif page == "Correlation Analysis 🔗📊":
    st.header("🔗📊 Correlation: Screen Time vs Self-Esteem")
    fig = px.box(df, x="daily_screen_hours", y="self_esteem_1to10", 
                     color="gender",
                     title="Correlation Between Screen Time & Self-Esteem",
                     color_discrete_sequence=chart_colors)
    fig.update_traces(opacity=0.8, marker_size=5)
    style_figure(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.write("👉This box plot illustrates the relationship between daily screen time and self-esteem scores, segmented by gender. It provides insights into how social media usage may influence self-perception.")

    st.header("🔗📊 Correlation: Screen Time vs Anxiety")
    fig = px.histogram(df, x="daily_screen_hours", y="anxiety_score_0to27", nbins=20,
                         color="gender",
                         title="Correlation Between Screen Time & Anxiety",
                         color_discrete_sequence=chart_colors)
    fig.update_traces(opacity=0.78, marker_line_width=0.5, marker_line_color="#FFFFFF")
    style_figure(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.write("👉This histogram shows the distribution of anxiety scores across different levels of daily screen time, segmented by gender.")

    st.header("🔗📊 Correlation: Screen Time vs Low Mood")
    fig = px.histogram(df, x="daily_screen_hours", y="low_mood_score_0to27", nbins=20,
                         color="gender",
                         title="Correlation Between Screen Time & Low Mood",
                         color_discrete_sequence=chart_colors)
    fig.update_traces(opacity=0.78, marker_line_width=0.5, marker_line_color="#FFFFFF")
    style_figure(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.write("👉This histogram shows the distribution of low mood scores across different levels of daily screen time, segmented by gender.")

# Demographics
elif page == "Demographics 👥🌍":
    st.header("👥🌍 Demographics Breakdown")
    fig = px.pie(df, names="gender", 
                 title="Gender Distribution",
                 color_discrete_sequence=chart_colors,
                 hole=0.48)
    fig.update_traces(textinfo="percent", textposition="inside")
    style_figure(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.write("👉This chart shows the distribution of participants across different gender groups.")


    fig = px.pie(df, names="age", 
                 title="Age Group Distribution",
                 color_discrete_sequence=chart_colors,
                 hole=0.48)
    fig.update_traces(textinfo="percent", textposition="inside")
    style_figure(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.write("👉This chart shows the distribution of participants across different age groups.")

    fig = px.pie(df, names="occupation", 
                      title="Occupation Distribution",
                      color_discrete_sequence=chart_colors,
                      hole=0.48)
    fig.update_traces(textinfo="percent", textposition="inside")
    style_figure(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.write("👉This chart shows the distribution of participants across different occupations.")

    fig = px.pie(df, names="region", 
                     title="Region Distribution",
                     color_discrete_sequence=chart_colors,
                     hole=0.48)
    fig.update_traces(textinfo="percent", textposition="inside")
    style_figure(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.write("👉This chart shows the distribution of participants across different regions.")
