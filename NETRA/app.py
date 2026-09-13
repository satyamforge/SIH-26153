
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="NETRA - Network Attack Forecasting",
    page_icon="🛡️",
    layout="wide"
)

# ==========================================
# TITLE
# ==========================================

st.title("🛡️ NETRA")
st.subheader("AI-Based Network Attack Forecasting System")

st.markdown(
    "NETRA analyzes network traffic using machine learning "
    "and forecasts future attack risk before an attack occurs."
)

st.divider()

# ==========================================
# LOAD FORECAST DATA
# ==========================================

history_file = "forecast_history.csv"
future_file = "forecast_future.csv"

if not os.path.exists(history_file) or not os.path.exists(future_file):

    st.error(
        "Forecast data not found. Please run forecast.py first."
    )

    st.stop()

history = pd.read_csv(history_file)
future = pd.read_csv(future_file)

# ==========================================
# CURRENT RISK
# ==========================================

current_risk = (
    history["Attack_Probability"].iloc[-1] * 100
)

forecast_risk = (
    future["Forecast_Attack_Probability"].max() * 100
)

# Determine risk
if forecast_risk >= 80:
    risk_level = "CRITICAL"
elif forecast_risk >= 60:
    risk_level = "HIGH"
elif forecast_risk >= 30:
    risk_level = "MEDIUM"
else:
    risk_level = "LOW"

# Trend
if len(history) >= 5:

    recent_values = history[
        "Attack_Probability"
    ].tail(5)

    change = (
        recent_values.iloc[-1]
        - recent_values.iloc[0]
    )

    if change > 0.01:
        trend = "📈 Increasing"
    elif change < -0.01:
        trend = "📉 Decreasing"
    else:
        trend = "➡️ Stable"

else:

    trend = "➡️ Stable"

# ==========================================
# TOP METRICS
# ==========================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Current Attack Risk",
        f"{current_risk:.2f}%"
    )

with col2:

    st.metric(
        "5-Minute Forecast",
        f"{forecast_risk:.2f}%"
    )

with col3:

    st.metric(
        "Risk Level",
        risk_level
    )

with col4:

    st.metric(
        "Traffic Windows",
        f"{len(history):,}"
    )

st.divider()

# ==========================================
# ALERT
# ==========================================

if risk_level == "CRITICAL":

    st.error(
        "🚨 CRITICAL ALERT: High probability of network attack detected in the forecast window."
    )

elif risk_level == "HIGH":

    st.warning(
        "⚠️ HIGH RISK: Network attack probability is increasing."
    )

elif risk_level == "MEDIUM":

    st.warning(
        "⚠️ MEDIUM RISK: Monitor network traffic closely."
    )

else:

    st.success(
        "🟢 LOW RISK: No significant attack activity forecast."
    )

# ==========================================
# FORECAST GRAPH
# ==========================================

st.header("📈 Attack Risk Forecast")

fig = go.Figure()

# Historical risk

fig.add_trace(
    go.Scatter(
        x=history["Minute"],
        y=history["Attack_Probability"] * 100,
        mode="lines",
        name="Observed Risk"
    )
)

# Future forecast

fig.add_trace(
    go.Scatter(
        x=future["Minute"],
        y=future["Forecast_Attack_Probability"] * 100,
        mode="lines+markers",
        name="Forecast Risk",
        line=dict(dash="dash")
    )
)

fig.add_hline(
    y=60,
    line_dash="dot",
    annotation_text="High Risk Threshold"
)

fig.update_layout(
    xaxis_title="Time",
    yaxis_title="Attack Probability (%)",
    yaxis=dict(
        range=[0, 100]
    ),
    height=500,
    hovermode="x unified"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================
# FORECAST TABLE
# ==========================================

st.header("🔮 Next 5 Minutes Forecast")

forecast_display = future.copy()

forecast_display[
    "Forecast_Attack_Probability"
] = (
    forecast_display[
        "Forecast_Attack_Probability"
    ] * 100
).round(2)

forecast_display = forecast_display[
    [
        "Minute",
        "Forecast_Attack_Probability"
    ]
]

forecast_display.columns = [
    "Time",
    "Predicted Attack Risk (%)"
]

st.dataframe(
    forecast_display,
    use_container_width=True,
    hide_index=True
)

# ==========================================
# TRAFFIC STATISTICS
# ==========================================

st.header("📊 Network Traffic Statistics")

stat1, stat2, stat3 = st.columns(3)

with stat1:

    total_windows = len(history)

    st.metric(
        "Analyzed Traffic Windows",
        f"{total_windows:,}"
    )

with stat2:

    total_flows = history[
        "Traffic_Count"
    ].sum()

    st.metric(
        "Analyzed Network Flows",
        f"{total_flows:,}"
    )

with stat3:

    max_risk = (
        history[
            "Max_Attack_Probability"
        ].max() * 100
    )

    st.metric(
        "Maximum Detected Risk",
        f"{max_risk:.2f}%"
    )

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "NETRA | AI-Based Network Attack Forecasting | "
    "Smart India Hackathon 2026 Prototype"
)

