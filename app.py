import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Student Performance Data Curator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Custom Styling
# -----------------------------
st.markdown(
    """
    <style>
    .main {
        background-color: #f7f9fc;
    }
    .block-container {
        padding-top: 2rem;
    }
    .app-header {
        padding: 1.5rem 2rem;
        background: linear-gradient(90deg, #1f3c88 0%, #4C72B0 100%);
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .app-header h1 {
        margin: 0;
        font-size: 1.8rem;
    }
    .app-header p {
        margin: 0.3rem 0 0 0;
        opacity: 0.9;
        font-size: 0.95rem;
    }
    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e6e9ef;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    section[data-testid="stSidebar"] {
        background-color: #1f3c88;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]
plt.rcParams.update({
    "axes.facecolor": "#ffffff",
    "figure.facecolor": "#ffffff",
    "axes.edgecolor": "#dddddd",
    "axes.grid": True,
    "grid.color": "#eeeeee",
    "font.size": 10
})

# -----------------------------
# Session State Setup
# -----------------------------
# We keep the working dataframe in session_state so that button
# clicks (like removing duplicates) actually stick between reruns,
# instead of resetting every time Streamlit re-executes the script.
if "df" not in st.session_state:
    st.session_state.df = None
if "duplicates_removed" not in st.session_state:
    st.session_state.duplicates_removed = False

SUBJECT_COLUMNS = ["Math", "Science", "English"]
ID_COLUMNS = ["Student_ID"]

# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <div class="app-header">
        <h1>Student Performance Data Curator</h1>
        <p>Upload, clean, explore and download student performance data — all in one place.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Sidebar: Upload + About
# -----------------------------
with st.sidebar:
    st.header("Upload Data")
    uploaded_file = st.file_uploader(
        "Student Performance CSV",
        type=["csv"]
    )
    st.markdown("---")
    st.markdown(
        "**Expected columns**\n\n"
        "- Student_ID\n"
        "- Name\n"
        "- Math\n"
        "- Science\n"
        "- English\n"
        "- Attendance"
    )

# Load a fresh file into session_state only when a new file is uploaded
if uploaded_file is not None:
    if st.session_state.df is None or st.session_state.get("_last_file") != uploaded_file.name:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.session_state.duplicates_removed = False
        st.session_state._last_file = uploaded_file.name

if st.session_state.df is not None:
    df = st.session_state.df

    overview_tab, cleaning_tab, insights_tab, download_tab = st.tabs(
        ["Overview", "Data Cleaning", "Insights", "Download"]
    )

    # -----------------------------
    # Overview Tab
    # -----------------------------
    with overview_tab:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Students", df.shape[0])
        col2.metric("Total Columns", df.shape[1])
        col3.metric("Duplicate Rows", int(df.duplicated().sum()))

        st.subheader("Dataset Preview")
        st.dataframe(df, use_container_width=True)

        with st.expander("Column Data Types & Missing Values"):
            info_col1, info_col2 = st.columns(2)
            with info_col1:
                st.write("**Data Types**")
                st.write(df.dtypes.astype(str))
            with info_col2:
                st.write("**Missing Values**")
                st.write(df.isnull().sum())

        st.subheader("Statistical Summary")
        st.dataframe(df.describe(), use_container_width=True)

    # -----------------------------
    # Data Cleaning Tab
    # -----------------------------
    with cleaning_tab:
        st.subheader("Duplicate Rows")

        if st.session_state.duplicates_removed:
            st.success("Duplicate rows have already been removed from this dataset.")
        elif df.duplicated().sum() == 0:
            st.info("No duplicate rows found — nothing to clean here.")
        else:
            st.warning(f"{int(df.duplicated().sum())} duplicate row(s) found.")
            if st.button("Remove Duplicates", type="primary"):
                st.session_state.df = df.drop_duplicates().reset_index(drop=True)
                st.session_state.duplicates_removed = True
                st.rerun()

    df = st.session_state.df  # refresh reference after any cleaning

    # -----------------------------
    # Insights Tab
    # -----------------------------
    with insights_tab:
        missing_subjects = [c for c in SUBJECT_COLUMNS if c not in df.columns]
        if missing_subjects:
            st.warning(
                f"Expected subject columns {SUBJECT_COLUMNS} but couldn't find "
                f"{missing_subjects} in this file. Skipping charts that depend on them."
            )
        else:
            df["Average"] = df[SUBJECT_COLUMNS].mean(axis=1)
            st.session_state.df = df

            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                st.subheader("Average Marks vs Attendance")
                fig, ax = plt.subplots(figsize=(6, 4.5))
                ax.hist(df["Average"], bins=8, alpha=0.75, color=PALETTE[0],
                        edgecolor="white", label="Average Marks")
                if "Attendance" in df.columns:
                    ax.hist(df["Attendance"], bins=8, alpha=0.65, color=PALETTE[1],
                            edgecolor="white", label="Attendance")
                ax.set_xlabel("Marks / Attendance")
                ax.set_ylabel("Number of Students")
                ax.legend(frameon=False)
                ax.spines[["top", "right"]].set_visible(False)
                st.pyplot(fig)

            with chart_col2:
                st.subheader("Average Marks by Subject")
                subject_averages = df[SUBJECT_COLUMNS].mean()
                fig2, ax2 = plt.subplots(figsize=(6, 4.5))
                subject_averages.plot(kind="bar", ax=ax2, color=PALETTE[:len(SUBJECT_COLUMNS)],
                                       edgecolor="white")
                ax2.set_ylabel("Average Marks")
                ax2.set_xticklabels(subject_averages.index, rotation=0)
                ax2.spines[["top", "right"]].set_visible(False)
                st.pyplot(fig2)

            if "Name" in df.columns:
                st.subheader("Top 5 Performers")
                top_students = df.sort_values("Average", ascending=False).head(5)
                display_cols = ["Name", "Average"] + [c for c in ["Attendance"] if c in df.columns]
                st.dataframe(
                    top_students[display_cols].reset_index(drop=True),
                    use_container_width=True
                )

    # -----------------------------
    # Download Tab
    # -----------------------------
    with download_tab:
        st.subheader("Download Cleaned Dataset")
        st.write("Your current dataset — including any cleaning applied — is ready to download.")
        st.download_button(
            label="Download Cleaned Dataset (CSV)",
            data=df.to_csv(index=False),
            file_name="cleaned_student_performance.csv",
            mime="text/csv",
            type="primary"
        )

else:
    st.info("Upload a student_performance.csv file from the sidebar to get started.")
