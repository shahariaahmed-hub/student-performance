import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Student Performance Data Curator",
    layout="wide"
)

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
# Title
# -----------------------------
st.title("Student Performance Data Curator")
st.caption("Upload, clean, explore and download student performance data — all in one place.")

# -----------------------------
# Upload CSV
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload Student Performance CSV",
    type=["csv"]
)

# Load a fresh file into session_state only when a new file is uploaded
if uploaded_file is not None:
    if st.session_state.df is None or st.session_state.get("_last_file") != uploaded_file.name:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.session_state.duplicates_removed = False
        st.session_state._last_file = uploaded_file.name

if st.session_state.df is not None:
    df = st.session_state.df

    # -----------------------------
    # Dataset Preview
    # -----------------------------
    st.subheader("Dataset Preview")
    st.dataframe(df, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Students", df.shape[0])
    col2.metric("Total Columns", df.shape[1])
    col3.metric("Duplicate Rows", int(df.duplicated().sum()))

    # -----------------------------
    # Dataset Information
    # -----------------------------
    with st.expander("Dataset Information"):
        st.write("**Column Data Types**")
        st.write(df.dtypes.astype(str))

        st.write("**Missing Values**")
        st.write(df.isnull().sum())

    # -----------------------------
    # Remove Duplicates (now persists!)
    # -----------------------------
    st.subheader("Data Cleaning")

    if st.session_state.duplicates_removed:
        st.success("Duplicate rows have already been removed from this dataset.")
    else:
        if df.duplicated().sum() == 0:
            st.info("No duplicate rows found — nothing to clean here.")
        else:
            if st.button("Remove Duplicates"):
                st.session_state.df = df.drop_duplicates().reset_index(drop=True)
                st.session_state.duplicates_removed = True
                st.rerun()

    df = st.session_state.df  # refresh reference after any cleaning

    # -----------------------------
    # Statistical Summary
    # -----------------------------
    st.subheader("Statistical Summary")
    st.dataframe(df.describe(), use_container_width=True)

    # -----------------------------
    # Derived Column: Average
    # -----------------------------
    missing_subjects = [c for c in SUBJECT_COLUMNS if c not in df.columns]
    if missing_subjects:
        st.warning(
            f"Expected subject columns {SUBJECT_COLUMNS} but couldn't find "
            f"{missing_subjects} in this file. Skipping charts that depend on them."
        )
    else:
        df["Average"] = df[SUBJECT_COLUMNS].mean(axis=1)
        st.session_state.df = df

        # -----------------------------
        # Histogram: Average Marks & Attendance
        # -----------------------------
        st.subheader("Distribution: Average Marks vs Attendance")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(df["Average"], bins=8, alpha=0.7, edgecolor="black", label="Average Marks")
        if "Attendance" in df.columns:
            ax.hist(df["Attendance"], bins=8, alpha=0.5, edgecolor="black", label="Attendance")
        ax.set_title("Average Marks and Attendance Distribution")
        ax.set_xlabel("Marks / Attendance")
        ax.set_ylabel("Number of Students")
        ax.legend()
        st.pyplot(fig)

        # -----------------------------
        # Average Marks by Subject
        # (fixed: only actual subjects, no Student_ID or Attendance noise)
        # -----------------------------
        st.subheader("Average Marks by Subject")
        subject_averages = df[SUBJECT_COLUMNS].mean()
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        subject_averages.plot(kind="bar", ax=ax2, color="#4C72B0", edgecolor="black")
        ax2.set_title("Average Marks by Subject")
        ax2.set_ylabel("Average Marks")
        ax2.set_xticklabels(subject_averages.index, rotation=0)
        st.pyplot(fig2)

        # -----------------------------
        # Top Performers
        # -----------------------------
        if "Name" in df.columns:
            st.subheader("Top 5 Performers")
            top_students = df.sort_values("Average", ascending=False).head(5)
            display_cols = ["Name", "Average"] + [c for c in ["Attendance"] if c in df.columns]
            st.table(top_students[display_cols].reset_index(drop=True))

    # -----------------------------
    # Download Cleaned Dataset
    # -----------------------------
    st.subheader("Download")
    st.download_button(
        label="Download Cleaned Dataset",
        data=df.to_csv(index=False),
        file_name="cleaned_student_performance.csv",
        mime="text/csv"
    )

else:
    st.info("Please upload a student_performance.csv file to get started.")
