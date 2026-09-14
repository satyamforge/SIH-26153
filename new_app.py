import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib
import os
import glob
import time


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NETRA - Network Attack Forecasting",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# IMPORT LIVE SIMULATOR
# ============================================================

try:
    from live_capture import LiveTrafficSimulator
except Exception as e:
    LiveTrafficSimulator = None


# ============================================================
# HEADER
# ============================================================

st.title("🛡️ NETRA")

st.subheader(
    "AI-Based Network Attack Forecasting System"
)

st.markdown(
    "NETRA analyzes network traffic using machine learning "
    "and forecasts future attack risk before an attack occurs."
)

st.divider()


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = "model/attack_detector.pkl"
FEATURE_PATH = "model/features.pkl"
DATASET_FOLDER = "dataset"


# ============================================================
# CHECK MODEL
# ============================================================

if not os.path.exists(MODEL_PATH):

    st.error(
        "❌ Trained model not found.\n\n"
        "Please run train.py first."
    )

    st.stop()


if not os.path.exists(FEATURE_PATH):

    st.error(
        "❌ Model feature file not found.\n\n"
        "Please run train.py first."
    )

    st.stop()


# ============================================================
# LOAD MODEL
# ============================================================

@st.cache_resource
def load_model():

    model = joblib.load(MODEL_PATH)
    features = joblib.load(FEATURE_PATH)

    return model, features


model, features = load_model()


# ============================================================
# FIND DATASETS
# ============================================================

csv_files = glob.glob(
    os.path.join(
        DATASET_FOLDER,
        "*.csv"
    )
)

if not csv_files:

    st.error(
        "❌ No CSV files found inside the dataset folder."
    )

    st.stop()


file_names = [
    os.path.basename(file)
    for file in csv_files
]


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🛡️ NETRA")

st.sidebar.markdown(
    "### Monitoring Mode"
)


mode = st.sidebar.radio(
    "Select Mode",
    [
        "📊 Dataset Analysis",
        "🟢 Simulated Live Monitoring"
    ]
)


# ============================================================
# HELPER FUNCTION
# RISK LEVEL
# ============================================================

def get_risk_level(probability):

    if probability >= 80:
        return "CRITICAL"

    elif probability >= 60:
        return "HIGH"

    elif probability >= 30:
        return "MEDIUM"

    else:
        return "LOW"


# ============================================================
# HELPER FUNCTION
# TREND
# ============================================================

def get_trend(history):

    if len(history) < 2:
        return "➡️ Stable"

    recent = history[
        "Attack_Probability"
    ].tail(5)

    if len(recent) < 2:
        return "➡️ Stable"

    change = (
        recent.iloc[-1]
        -
        recent.iloc[0]
    )

    if change > 0.01:
        return "📈 Increasing"

    elif change < -0.01:
        return "📉 Decreasing"

    else:
        return "➡️ Stable"


# ============================================================
# MODE 1
# DATASET ANALYSIS
# ============================================================

if mode == "📊 Dataset Analysis":

    st.sidebar.divider()

    st.sidebar.subheader(
        "Dataset Settings"
    )

    selected_file = st.sidebar.selectbox(
        "Select CIC-IDS2017 Traffic",
        file_names
    )

    analyze_button = st.sidebar.button(
        "🔍 Analyze Dataset",
        use_container_width=True
    )


    # --------------------------------------------------------
    # DATASET ANALYSIS FUNCTION
    # --------------------------------------------------------

    def analyze_dataset(file_path):

        df = pd.read_csv(
            file_path,
            low_memory=False
        )

        df.columns = df.columns.str.strip()


        # Limit data so the dashboard stays fast
        MAX_ROWS = 30000


        if len(df) > MAX_ROWS:

            max_start = (
                len(df) - MAX_ROWS
            )

            start = np.random.randint(
                0,
                max_start + 1
            )

            df = df.iloc[
                start:start + MAX_ROWS
            ].copy()


        # ----------------------------------------------------
        # CREATE MODEL FEATURES
        # ----------------------------------------------------

        X = pd.DataFrame(
            index=df.index
        )


        for feature in features:

            if feature in df.columns:

                X[feature] = pd.to_numeric(
                    df[feature],
                    errors="coerce"
                )

            else:

                X[feature] = 0


        # Clean invalid values
        X = X.replace(
            [np.inf, -np.inf],
            np.nan
        )

        X = X.fillna(0)


        # ----------------------------------------------------
        # MACHINE LEARNING PREDICTION
        # ----------------------------------------------------

        probabilities = model.predict_proba(
            X
        )[:, 1]


        # ----------------------------------------------------
        # CREATE TRAFFIC WINDOWS
        # ----------------------------------------------------

        WINDOW_SIZE = 1000

        records = []


        for i in range(
            0,
            len(probabilities),
            WINDOW_SIZE
        ):

            window = probabilities[
                i:i + WINDOW_SIZE
            ]

            if len(window) == 0:
                continue


            records.append({

                "Attack_Probability":
                    window.mean(),

                "Max_Attack_Probability":
                    window.max(),

                "Traffic_Count":
                    len(window)

            })


        history = pd.DataFrame(
            records
        )


        # ----------------------------------------------------
        # FORECAST
        # ----------------------------------------------------

        recent = history[
            "Attack_Probability"
        ].tail(15).values


        if len(recent) >= 2:

            x = np.arange(
                len(recent)
            )

            slope, intercept = np.polyfit(
                x,
                recent,
                1
            )

            future_x = np.arange(
                len(recent),
                len(recent) + 5
            )

            forecast = (
                intercept
                +
                slope * future_x
            )

        else:

            forecast = np.repeat(
                recent[-1],
                5
            )


        forecast = np.clip(
            forecast,
            0,
            1
        )


        # ----------------------------------------------------
        # TIME
        # ----------------------------------------------------

        current_time = (
            pd.Timestamp.now()
            .floor("min")
        )


        history["Minute"] = [

            current_time
            -
            pd.Timedelta(
                minutes=len(history) - i
            )

            for i in range(
                len(history)
            )

        ]


        future_times = [

            current_time
            +
            pd.Timedelta(
                minutes=i + 1
            )

            for i in range(5)

        ]


        future = pd.DataFrame({

            "Minute":
                future_times,

            "Forecast_Attack_Probability":
                forecast

        })


        return (
            history,
            future,
            len(df)
        )


    # --------------------------------------------------------
    # SESSION STATE
    # --------------------------------------------------------

    if "dataset_history" not in st.session_state:

        st.session_state.dataset_history = None


    if "dataset_future" not in st.session_state:

        st.session_state.dataset_future = None


    if "dataset_source" not in st.session_state:

        st.session_state.dataset_source = None


    if "dataset_rows" not in st.session_state:

        st.session_state.dataset_rows = 0


    # --------------------------------------------------------
    # ANALYZE BUTTON
    # --------------------------------------------------------

    if analyze_button:

        file_path = os.path.join(
            DATASET_FOLDER,
            selected_file
        )


        with st.spinner(
            "🤖 NETRA is analyzing network traffic..."
        ):

            (
                history,
                future,
                rows
            ) = analyze_dataset(
                file_path
            )


        st.session_state.dataset_history = history

        st.session_state.dataset_future = future

        st.session_state.dataset_source = selected_file

        st.session_state.dataset_rows = rows


        st.success(
            "✅ Dataset analyzed successfully!"
        )


    # --------------------------------------------------------
    # NO DATA YET
    # --------------------------------------------------------

    if st.session_state.dataset_history is None:

        st.info(
            "👈 Select a CIC-IDS2017 traffic file "
            "and click **Analyze Dataset**."
        )

        st.stop()


    history = (
        st.session_state.dataset_history
    )

    future = (
        st.session_state.dataset_future
    )

    source_name = (
        st.session_state.dataset_source
    )


# ============================================================
# MODE 2
# SIMULATED LIVE MONITORING
# ============================================================

else:

    # --------------------------------------------------------
    # LIVE MODE INFORMATION
    # --------------------------------------------------------

    st.sidebar.success(
        "🟢 LIVE SIMULATION ACTIVE"
    )

    st.sidebar.markdown(
        "CIC-IDS2017 traffic is being replayed "
        "continuously as simulated live traffic."
    )


    # --------------------------------------------------------
    # CHECK LIVE SIMULATOR
    # --------------------------------------------------------

    if LiveTrafficSimulator is None:

        st.error(
            "❌ live_capture.py could not be loaded."
        )

        st.stop()


    # --------------------------------------------------------
    # CREATE LIVE SIMULATOR
    # --------------------------------------------------------

    if "live_simulator" not in st.session_state:

        try:

            st.session_state.live_simulator = (
                LiveTrafficSimulator(
                    dataset_folder=DATASET_FOLDER,
                    model_path=MODEL_PATH,
                    feature_path=FEATURE_PATH,
                    batch_size=1000
                )
            )

        except Exception as e:

            st.error(
                f"❌ Could not start live simulation: {e}"
            )

            st.stop()


    simulator = (
        st.session_state.live_simulator
    )


    # --------------------------------------------------------
    # LIVE HISTORY
    # --------------------------------------------------------

    if "live_history" not in st.session_state:

        st.session_state.live_history = []


    if "live_total_flows" not in st.session_state:

        st.session_state.live_total_flows = 0


    if "live_batch_number" not in st.session_state:

        st.session_state.live_batch_number = 0


    # --------------------------------------------------------
    # GET NEXT TRAFFIC BATCH
    # --------------------------------------------------------

    (
        probabilities,
        traffic_count,
        source_name
    ) = simulator.get_next_batch()


    # --------------------------------------------------------
    # CURRENT BATCH STATISTICS
    # --------------------------------------------------------

    current_probability = (
        probabilities.mean()
    )


    max_probability = (
        probabilities.max()
    )


    # --------------------------------------------------------
    # ADD TO LIVE HISTORY
    # --------------------------------------------------------

    st.session_state.live_history.append({

        "Time":
            pd.Timestamp.now(),

        "Attack_Probability":
            current_probability,

        "Max_Attack_Probability":
            max_probability,

        "Traffic_Count":
            traffic_count

    })


    # Keep only the most recent 30 windows
    st.session_state.live_history = (
        st.session_state.live_history[-30:]
    )


    # Update statistics
    st.session_state.live_total_flows += (
        traffic_count
    )


    st.session_state.live_batch_number += 1


    # Convert to dataframe
    live_df = pd.DataFrame(
        st.session_state.live_history
    )


    # --------------------------------------------------------
    # FORECAST
    # --------------------------------------------------------

    recent = live_df[
        "Attack_Probability"
    ].tail(15).values


    if len(recent) >= 2:

        x = np.arange(
            len(recent)
        )

        slope, intercept = np.polyfit(
            x,
            recent,
            1
        )

        future_x = np.arange(
            len(recent),
            len(recent) + 5
        )

        forecast_values = (
            intercept
            +
            slope * future_x
        )

    else:

        forecast_values = np.repeat(
            recent[-1],
            5
        )


    forecast_values = np.clip(
        forecast_values,
        0,
        1
    )


    # --------------------------------------------------------
    # FUTURE TIME
    # --------------------------------------------------------

    now = pd.Timestamp.now()


    future_times = [

        now
        +
        pd.Timedelta(
            minutes=i + 1
        )

        for i in range(5)

    ]


    future = pd.DataFrame({

        "Minute":
            future_times,

        "Forecast_Attack_Probability":
            forecast_values

    })


    # Convert live history
    history = live_df.rename(
        columns={
            "Time": "Minute"
        }
    )


# ============================================================
# CALCULATE CURRENT RISK
# ============================================================

current_risk = (
    history[
        "Attack_Probability"
    ].iloc[-1]
    *
    100
)


# ============================================================
# CALCULATE FORECAST RISK
# ============================================================

forecast_risk = (
    future[
        "Forecast_Attack_Probability"
    ].max()
    *
    100
)


# ============================================================
# RISK LEVEL
# ============================================================

risk_level = get_risk_level(
    forecast_risk
)


# ============================================================
# TREND
# ============================================================

trend = get_trend(
    history
)


# ============================================================
# LIVE STATUS
# ============================================================

if mode == "🟢 Simulated Live Monitoring":

    st.success(
        "🟢 NETRA LIVE MONITORING ACTIVE"
    )

    st.caption(
        f"📡 Simulated traffic source: "
        f"{source_name}  |  "
        f"Batch #{st.session_state.live_batch_number}"
    )

else:

    st.caption(
        f"📡 Dataset source: {source_name}"
    )


# ============================================================
# TOP METRICS
# ============================================================

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

    if mode == "🟢 Simulated Live Monitoring":

        st.metric(
            "Live Traffic Flows",
            f"{st.session_state.live_total_flows:,}"
        )

    else:

        st.metric(
            "Traffic Windows",
            f"{len(history):,}"
        )


st.divider()


# ============================================================
# TREND DISPLAY
# ============================================================

trend_col1, trend_col2 = st.columns(2)


with trend_col1:

    st.metric(
        "Attack Risk Trend",
        trend
    )


with trend_col2:

    maximum_risk = (
        history[
            "Max_Attack_Probability"
        ].max()
        *
        100
    )

    st.metric(
        "Maximum Detected Risk",
        f"{maximum_risk:.2f}%"
    )


# ============================================================
# ALERT
# ============================================================

if risk_level == "CRITICAL":

    st.error(
        "🚨 CRITICAL ALERT: High probability "
        "of network attack predicted in the "
        "forecast window."
    )

elif risk_level == "HIGH":

    st.warning(
        "⚠️ HIGH RISK: Network attack probability "
        "is increasing."
    )

elif risk_level == "MEDIUM":

    st.warning(
        "⚠️ MEDIUM RISK: Monitor network traffic "
        "closely."
    )

else:

    st.success(
        "🟢 LOW RISK: No significant attack "
        "activity forecast."
    )


# ============================================================
# GRAPH
# ============================================================

st.header(
    "📈 Attack Risk Forecast"
)


fig = go.Figure()


# Observed traffic
fig.add_trace(
    go.Scatter(

        x=history[
            "Minute"
        ],

        y=history[
            "Attack_Probability"
        ] * 100,

        mode="lines+markers",

        name="Observed Risk"

    )
)


# Forecast
fig.add_trace(
    go.Scatter(

        x=future[
            "Minute"
        ],

        y=future[
            "Forecast_Attack_Probability"
        ] * 100,

        mode="lines+markers",

        name="Forecast Risk",

        line=dict(
            dash="dash"
        )

    )
)


# High risk threshold
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


# ============================================================
# FIVE-MINUTE FORECAST
# ============================================================

st.header(
    "🔮 Next 5 Minutes Forecast"
)


forecast_display = future.copy()


forecast_display[
    "Forecast_Attack_Probability"
] = (

    forecast_display[
        "Forecast_Attack_Probability"
    ]
    *
    100

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


# ============================================================
# NETWORK STATISTICS
# ============================================================

st.header(
    "📊 Network Traffic Statistics"
)


stat1, stat2, stat3 = st.columns(3)


with stat1:

    if mode == "🟢 Simulated Live Monitoring":

        st.metric(
            "Total Simulated Flows",
            f"{st.session_state.live_total_flows:,}"
        )

    else:

        st.metric(
            "Analyzed Traffic Flows",
            f"{st.session_state.dataset_rows:,}"
        )


with stat2:

    current_window_flows = (
        history[
            "Traffic_Count"
        ].iloc[-1]
    )

    st.metric(
        "Current Traffic Window",
        f"{current_window_flows:,}"
    )


with stat3:

    st.metric(
        "Model Features",
        f"{len(features)}"
    )


# ============================================================
# LIVE MONITORING INFORMATION
# ============================================================

if mode == "🟢 Simulated Live Monitoring":

    st.divider()

    st.subheader(
        "📡 Live Simulation Status"
    )

    live_col1, live_col2, live_col3 = (
        st.columns(3)
    )


    with live_col1:

        st.write(
            "🟢 **Status:** ACTIVE"
        )


    with live_col2:

        st.write(
            f"📦 **Batch:** "
            f"{st.session_state.live_batch_number}"
        )


    with live_col3:

        st.write(
            f"📡 **Source:** "
            f"{source_name}"
        )


    st.caption(
        "The dashboard automatically receives "
        "the next CIC-IDS2017 traffic batch every "
        "2 seconds."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "NETRA | AI-Based Network Attack Forecasting | "
    "Smart India Hackathon 2026 Prototype"
)


# ============================================================
# AUTOMATIC REFRESH
# ============================================================

if mode == "🟢 Simulated Live Monitoring":

    time.sleep(2)

    st.rerun()

