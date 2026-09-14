import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib
import os
import glob

st.set_page_config(
    page_title="NETRA - Network Attack Forecasting",
    page_icon="🛡️",
    layout="wide"
)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🛡️ NETRA")
st.subheader("AI-Based Network Attack Forecasting System")

st.markdown(
    "NETRA analyzes network traffic using machine learning "
    "and forecasts future attack risk before an attack occurs."
)

st.divider()

# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

MODEL_PATH = "model/attack_detector.pkl"
FEATURE_PATH = "model/features.pkl"

if not os.path.exists(MODEL_PATH):
    st.error("❌ Model not found. Please run train.py first.")
    st.stop()

model = joblib.load(MODEL_PATH)
features = joblib.load(FEATURE_PATH)

# --------------------------------------------------
# FIND DATASETS
# --------------------------------------------------

csv_files = glob.glob("dataset/*.csv")

if not csv_files:
    st.error("❌ No CSV files found inside dataset folder.")
    st.stop()

file_names = [os.path.basename(x) for x in csv_files]

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("⚙️ NETRA Controls")

source = st.sidebar.selectbox(
    "Select Traffic Source",
    ["🎲 Random Traffic Batch"] + file_names
)

st.sidebar.info(
    "Click the button below to generate a fresh "
    "AI analysis from network traffic."
)

run_analysis = st.sidebar.button(
    "🔄 Run New AI Analysis",
    use_container_width=True
)

# --------------------------------------------------
# ANALYSIS FUNCTION
# --------------------------------------------------

def analyze_traffic(file_path):

    df = pd.read_csv(file_path, low_memory=False)

    df.columns = df.columns.str.strip()

    # Keep a random CONTIGUOUS section of traffic.
    # This changes the result while preserving row order.
    MAX_ROWS = 30000

    if len(df) > MAX_ROWS:

        max_start = len(df) - MAX_ROWS

        start = np.random.randint(0, max_start + 1)

        df = df.iloc[start:start + MAX_ROWS].copy()

    # Create feature dataframe
    X = pd.DataFrame(index=df.index)

    for feature in features:

        if feature in df.columns:
            X[feature] = pd.to_numeric(
                df[feature],
                errors="coerce"
            )
        else:
            X[feature] = 0

    # Clean data
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(0)

    # AI prediction
    attack_probability = model.predict_proba(X)[:, 1]

    # --------------------------------------------------
    # CREATE TRAFFIC WINDOWS
    # --------------------------------------------------

    WINDOW_SIZE = 1000

    records = []

    for i in range(0, len(attack_probability), WINDOW_SIZE):

        window = attack_probability[i:i + WINDOW_SIZE]

        if len(window) == 0:
            continue

        records.append({
            "Attack_Probability": window.mean(),
            "Max_Attack_Probability": window.max(),
            "Traffic_Count": len(window)
        })

    history = pd.DataFrame(records)

    # --------------------------------------------------
    # FORECAST
    # --------------------------------------------------

    recent = history["Attack_Probability"].tail(15).values

    if len(recent) >= 2:

        x = np.arange(len(recent))

        slope, intercept = np.polyfit(
            x,
            recent,
            1
        )

        future_x = np.arange(
            len(recent),
            len(recent) + 5
        )

        forecast = intercept + slope * future_x

    else:

        forecast = np.repeat(
            recent[-1],
            5
        )

    forecast = np.clip(forecast, 0, 1)

    # Current time
    current_time = pd.Timestamp.now().floor("min")

    history["Minute"] = [
        current_time - pd.Timedelta(
            minutes=len(history) - i
        )
        for i in range(len(history))
    ]

    future_times = [
        current_time + pd.Timedelta(minutes=i + 1)
        for i in range(5)
    ]

    future = pd.DataFrame({
        "Minute": future_times,
        "Forecast_Attack_Probability": forecast
    })

    return history, future, len(df)


# --------------------------------------------------
# INITIAL STATE
# --------------------------------------------------

if "history" not in st.session_state:

    # Load old forecast as initial display
    if os.path.exists("forecast_history.csv") and \
       os.path.exists("forecast_future.csv"):

        st.session_state.history = pd.read_csv(
            "forecast_history.csv"
        )

        st.session_state.future = pd.read_csv(
            "forecast_future.csv"
        )

        st.session_state.source = "Previous analysis"

    else:

        st.session_state.history = None
        st.session_state.future = None
        st.session_state.source = None


# --------------------------------------------------
# RUN NEW ANALYSIS
# --------------------------------------------------

if run_analysis:

    # Random source
    if source == "🎲 Random Traffic Batch":

        selected_file = np.random.choice(csv_files)

    else:

        selected_file = os.path.join(
            "dataset",
            source
        )

    with st.spinner("🤖 NETRA is analyzing network traffic..."):

        history, future, rows = analyze_traffic(
            selected_file
        )

    st.session_state.history = history
    st.session_state.future = future
    st.session_state.source = os.path.basename(
        selected_file
    )

    st.session_state.rows = rows

    st.success(
        "✅ Fresh network traffic analyzed successfully!"
    )


# --------------------------------------------------
# CHECK DATA
# --------------------------------------------------

history = st.session_state.history
future = st.session_state.future

if history is None:

    st.info(
        "👈 Select a traffic source and click "
        "'Run New AI Analysis' to start."
    )

    st.stop()


# --------------------------------------------------
# CALCULATE RISK
# --------------------------------------------------

current_risk = (
    history["Attack_Probability"].iloc[-1] * 100
)

forecast_risk = (
    future["Forecast_Attack_Probability"].max() * 100
)

# Risk level

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


# --------------------------------------------------
# TOP METRICS
# --------------------------------------------------

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


# --------------------------------------------------
# SOURCE INFO
# --------------------------------------------------

st.caption(
    f"📡 Traffic Source: {st.session_state.source}"
)

# --------------------------------------------------
# ALERT
# --------------------------------------------------

if risk_level == "CRITICAL":

    st.error(
        "🚨 CRITICAL ALERT: High probability of "
        "network attack detected in the forecast window."
    )

elif risk_level == "HIGH":

    st.warning(
        "⚠️ HIGH RISK: Network attack probability "
        "is increasing."
    )

elif risk_level == "MEDIUM":

    st.warning(
        "⚠️ MEDIUM RISK: Monitor network traffic closely."
    )

else:

    st.success(
        "🟢 LOW RISK: No significant attack activity forecast."
    )


# --------------------------------------------------
# FORECAST GRAPH
# --------------------------------------------------

st.header("📈 Attack Risk Forecast")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=history["Minute"],
        y=history["Attack_Probability"] * 100,
        mode="lines",
        name="Observed Risk"
    )
)

fig.add_trace(
    go.Scatter(
        x=future["Minute"],
        y=future[
            "Forecast_Attack_Probability"
        ] * 100,
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
    yaxis=dict(range=[0, 100]),
    height=500,
    hovermode="x unified"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# --------------------------------------------------
# 5 MINUTE FORECAST
# --------------------------------------------------

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
    ["Minute", "Forecast_Attack_Probability"]
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


# --------------------------------------------------
# NETWORK STATISTICS
# --------------------------------------------------

st.header("📊 Network Traffic Statistics")

stat1, stat2, stat3 = st.columns(3)

with stat1:

    st.metric(
        "Analyzed Traffic Windows",
        f"{len(history):,}"
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


st.divider()

st.caption(
    "NETRA | AI-Based Network Attack Forecasting | "
    "Smart India Hackathon 2026 Prototype"
)