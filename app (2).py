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
# Custom Styling — gives the app a real "software dashboard" feel
# instead of the default plain Streamlit look
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background-color: #f4f6fb;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }

    /* Top app bar */
    .app-topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1.1rem 1.8rem;
        background: #ffffff;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
        border: 1px solid #eaedf5;
        margin-bottom: 1.6rem;
    }
    .app-topbar .brand {
        display: flex;
        align-items: center;
        gap: 0.7rem;
    }
    .app-topbar .brand-mark {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        background: linear-gradient(135deg, #2b3a91 0%, #4C72B0 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 800;
        font-size: 1.1rem;
    }
    .app-topbar h1 {
        margin: 0;
        font-size: 1.3rem;
        font-weight: 800;
        color: #1a1d29;
    }
    .app-topbar p {
        margin: 0;
        font-size: 0.82rem;
        color: #7b8194;
    }
    .app-topbar .status-pill {
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
        background: #eaf7ef;
        color: #1e824c;
        border: 1px solid #cdeedb;
    }

    /* Section panels */
    .panel-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1a1d29;
        margin: 0.2rem 0 1rem 0;
    }
    .panel-subtitle {
        font-size: 0.85rem;
        color: #7b8194;
        margin: -0.6rem 0 1rem 0;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #eaedf5;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
    }
    div[data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #7b8194;
    }

    div[data-testid="stTabs"] button {
        font-weight: 600;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #171b2e;
    }
    section[data-testid="stSidebar"] * {
        color: #e6e8f0 !important;
    }
    section[data-testid="stSidebar"] .stFileUploader label {
        color: #ffffff !important;
        font-weight: 600;
    }
    section[data-testid="stSidebar"] .stRadio label {
        font-weight: 500;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #eaedf5;
        border-radius: 10px;
        overflow: hidden;
    }

    .grade-badge {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.78rem;
    }

    .footer-note {
        text-align: center;
        color: #9aa0b4;
        font-size: 0.78rem;
        margin-top: 2.2rem;
    }

    /* Home welcome banner */
    .welcome-banner {
        background: linear-gradient(120deg, #1f2a5c 0%, #2b3a91 55%, #4C72B0 100%);
        border-radius: 16px;
        padding: 2.2rem 2rem;
        color: white;
        margin-bottom: 1.8rem;
    }
    .welcome-banner h2 {
        margin: 0 0 0.3rem 0;
        font-size: 1.6rem;
        font-weight: 800;
    }
    .welcome-banner p {
        margin: 0;
        opacity: 0.85;
        font-size: 0.95rem;
    }

    /* Icon tiles */
    .tile-icon {
        width: 46px;
        height: 46px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 800;
        font-size: 1.05rem;
        margin-bottom: 0.7rem;
    }
    .tile-title {
        font-weight: 700;
        font-size: 0.98rem;
        color: #1a1d29;
        margin-bottom: 0.2rem;
    }
    .tile-desc {
        font-size: 0.8rem;
        color: #7b8194;
        margin-bottom: 0.8rem;
        min-height: 2.4rem;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2", "#937860", "#DA8BC3", "#8C8C8C"]
plt.rcParams.update({
    "axes.facecolor": "#ffffff",
    "figure.facecolor": "#ffffff",
    "axes.edgecolor": "#dddddd",
    "axes.grid": True,
    "grid.color": "#eeeeee",
    "font.size": 10
})

NON_SUBJECT_COLUMNS = ["Student_ID", "Class", "Section", "Attendance", "Average"]
PASS_THRESHOLD = 40


def get_subject_columns(dataframe: pd.DataFrame) -> list:
    """Any numeric column that isn't an ID, Class, Section, Attendance, or the
    derived Average is treated as a subject — so the app supports any number
    of subjects automatically."""
    numeric_cols = dataframe.select_dtypes(include="number").columns
    return [c for c in numeric_cols if c not in NON_SUBJECT_COLUMNS]


def assign_grade(average: float) -> str:
    if average >= 90:
        return "A+"
    elif average >= 80:
        return "A"
    elif average >= 70:
        return "B"
    elif average >= 60:
        return "C"
    elif average >= 50:
        return "D"
    else:
        return "F"


GRADE_COLORS = {
    "A+": "#1e824c", "A": "#3d9b6e", "B": "#4C72B0",
    "C": "#DD8452", "D": "#c9932f", "F": "#C44E52"
}

# -----------------------------
# Session State Setup
# -----------------------------
if "df" not in st.session_state:
    st.session_state.df = None
if "duplicates_removed" not in st.session_state:
    st.session_state.duplicates_removed = False
if "page" not in st.session_state:
    st.session_state.page = "Home"

# -----------------------------
# Top App Bar
# -----------------------------
status_label = "Ready" if st.session_state.df is None else "Data Loaded"
st.markdown(
    f"""
    <div class="app-topbar">
        <div class="brand">
            <div class="brand-mark">SP</div>
            <div>
                <h1>Student Performance Data Curator</h1>
                <p>Upload, clean, analyze and report on student performance data</p>
            </div>
        </div>
        <div class="status-pill">{status_label}</div>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Sidebar: Navigation + Upload
# -----------------------------
with st.sidebar:
    st.markdown("### Navigation")
    nav_options = ["Home", "Dashboard", "Student Directory", "Analytics", "Reports"]
    page = st.radio(
        "Go to",
        nav_options,
        index=nav_options.index(st.session_state.page),
        label_visibility="collapsed"
    )
    st.session_state.page = page
    st.markdown("---")
    st.markdown("### Data Source")
    uploaded_file = st.file_uploader("Student Performance CSV", type=["csv"])
    st.markdown("---")
    st.markdown("### Schema")
    st.markdown(
        "- Student_ID\n"
        "- Name\n"
        "- Class / Section (optional)\n"
        "- Subject columns (any number)\n"
        "- Attendance"
    )
    st.markdown("---")
    st.caption("Built with Streamlit")

# Load a fresh file into session_state only when a new file is uploaded
if uploaded_file is not None:
    if st.session_state.df is None or st.session_state.get("_last_file") != uploaded_file.name:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.session_state.duplicates_removed = False
        st.session_state._last_file = uploaded_file.name

# -----------------------------
# Main Content
# -----------------------------
if st.session_state.df is None:
    st.markdown(
        """
        <div class="welcome-banner">
            <h2>Welcome</h2>
            <p>Upload a student_performance.csv file from the sidebar to unlock the dashboard, directory, analytics and reports.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    tiles = [
        ("DB", "#2b3a91", "Dashboard", "Class KPIs, subject averages and grade distribution"),
        ("SD", "#DD8452", "Student Directory", "Search, filter and browse the full student list"),
        ("AN", "#55A868", "Analytics", "Distributions, subject comparison and data cleaning"),
        ("RP", "#C44E52", "Reports", "Download the cleaned dataset and class summary"),
    ]
    cols = st.columns(4)
    for col, (initials, color, title, desc) in zip(cols, tiles):
        with col:
            with st.container(border=True):
                st.markdown(
                    f'<div class="tile-icon" style="background:{color};">{initials}</div>'
                    f'<div class="tile-title">{title}</div>'
                    f'<div class="tile-desc">{desc}</div>',
                    unsafe_allow_html=True
                )
    st.info("No data loaded yet — use the uploader in the sidebar to get started.")
else:
    df = st.session_state.df
    subject_columns = get_subject_columns(df)

    if subject_columns:
        df["Average"] = df[subject_columns].mean(axis=1).round(1)
        df["Grade"] = df["Average"].apply(assign_grade)
        df["Status"] = df["Average"].apply(lambda a: "Pass" if a >= PASS_THRESHOLD else "Fail")
        st.session_state.df = df

    # =========================================================
    # HOME PAGE
    # =========================================================
    if page == "Home":
        student_count = df.shape[0]
        avg_line = f"{df['Average'].mean():.1f} average score" if subject_columns else "no subject data yet"
        st.markdown(
            f"""
            <div class="welcome-banner">
                <h2>Welcome back</h2>
                <p>{student_count} students loaded &middot; {avg_line}. Choose a section below to continue.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        tiles = [
            ("DB", "#2b3a91", "Dashboard", "Class KPIs, subject averages and grade distribution", "Dashboard"),
            ("SD", "#DD8452", "Student Directory", "Search, filter and browse the full student list", "Student Directory"),
            ("AN", "#55A868", "Analytics", "Distributions, subject comparison and data cleaning", "Analytics"),
            ("RP", "#C44E52", "Reports", "Download the cleaned dataset and class summary", "Reports"),
        ]

        cols = st.columns(4)
        for col, (initials, color, title, desc, target_page) in zip(cols, tiles):
            with col:
                with st.container(border=True):
                    st.markdown(
                        f'<div class="tile-icon" style="background:{color};">{initials}</div>'
                        f'<div class="tile-title">{title}</div>'
                        f'<div class="tile-desc">{desc}</div>',
                        unsafe_allow_html=True
                    )
                    if st.button("Open", key=f"tile_{target_page}", use_container_width=True):
                        st.session_state.page = target_page
                        st.rerun()

        if subject_columns and "Name" in df.columns:
            st.markdown('<p class="panel-title">Quick Look: Top 5 Performers</p>', unsafe_allow_html=True)
            top_students = df.sort_values("Average", ascending=False).head(5)
            display_cols = ["Name", "Average", "Grade"] + \
                ([c for c in ["Attendance"] if c in df.columns])
            st.dataframe(top_students[display_cols].reset_index(drop=True), use_container_width=True)

    # =========================================================
    # DASHBOARD PAGE
    # =========================================================
    elif page == "Dashboard":
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Total Students", df.shape[0])
        if subject_columns:
            k2.metric("Class Average", f"{df['Average'].mean():.1f}")
            pass_rate = (df["Status"] == "Pass").mean() * 100
            k3.metric("Pass Rate", f"{pass_rate:.0f}%")
        if "Attendance" in df.columns:
            k4.metric("Avg Attendance", f"{df['Attendance'].mean():.0f}%")
        if subject_columns and "Name" in df.columns:
            top_row = df.sort_values("Average", ascending=False).iloc[0]
            k5.metric("Top Performer", top_row["Name"])

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns([1.3, 1])

        with col1:
            st.markdown('<p class="panel-title">Average Marks by Subject</p>', unsafe_allow_html=True)
            if subject_columns:
                subject_averages = df[subject_columns].mean().sort_values(ascending=False)
                bar_colors = [PALETTE[i % len(PALETTE)] for i in range(len(subject_averages))]
                fig, ax = plt.subplots(figsize=(8, 4.2))
                bars = ax.bar(subject_averages.index, subject_averages.values,
                               color=bar_colors, edgecolor="white")
                ax.set_ylabel("Average Marks")
                ax.set_ylim(0, 100)
                ax.spines[["top", "right"]].set_visible(False)
                ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=9)
                plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
                fig.tight_layout()
                st.pyplot(fig)

        with col2:
            st.markdown('<p class="panel-title">Grade Distribution</p>', unsafe_allow_html=True)
            if subject_columns:
                grade_counts = df["Grade"].value_counts().reindex(
                    ["A+", "A", "B", "C", "D", "F"]
                ).dropna()
                fig2, ax2 = plt.subplots(figsize=(5, 4.2))
                colors = [GRADE_COLORS[g] for g in grade_counts.index]
                ax2.pie(
                    grade_counts.values,
                    labels=grade_counts.index,
                    colors=colors,
                    autopct="%1.0f%%",
                    startangle=90,
                    wedgeprops={"edgecolor": "white", "linewidth": 1.5}
                )
                ax2.axis("equal")
                st.pyplot(fig2)

        st.markdown('<p class="panel-title">Top 5 Performers</p>', unsafe_allow_html=True)
        if subject_columns and "Name" in df.columns:
            top_students = df.sort_values("Average", ascending=False).head(5)
            display_cols = ["Name", "Average", "Grade"] + \
                ([c for c in ["Attendance"] if c in df.columns])
            st.dataframe(top_students[display_cols].reset_index(drop=True), use_container_width=True)

    # =========================================================
    # STUDENT DIRECTORY PAGE
    # =========================================================
    elif page == "Student Directory":
        st.markdown('<p class="panel-title">Student Directory</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="panel-subtitle">Search and filter the full student list</p>',
            unsafe_allow_html=True
        )

        filter_col1, filter_col2, filter_col3 = st.columns(3)
        with filter_col1:
            search_name = st.text_input("Search by name")
        with filter_col2:
            if "Section" in df.columns:
                sections = ["All"] + sorted(df["Section"].dropna().unique().tolist())
                section_filter = st.selectbox("Section", sections)
            else:
                section_filter = "All"
        with filter_col3:
            if subject_columns:
                grade_filter = st.selectbox("Grade", ["All", "A+", "A", "B", "C", "D", "F"])
            else:
                grade_filter = "All"

        filtered = df.copy()
        if search_name and "Name" in filtered.columns:
            filtered = filtered[filtered["Name"].str.contains(search_name, case=False, na=False)]
        if section_filter != "All" and "Section" in filtered.columns:
            filtered = filtered[filtered["Section"] == section_filter]
        if grade_filter != "All" and "Grade" in filtered.columns:
            filtered = filtered[filtered["Grade"] == grade_filter]

        st.dataframe(filtered, use_container_width=True)
        st.caption(f"Showing {len(filtered)} of {len(df)} students")

        with st.expander("Column Data Types & Missing Values"):
            info_col1, info_col2 = st.columns(2)
            with info_col1:
                st.write("**Data Types**")
                st.write(df.dtypes.astype(str))
            with info_col2:
                st.write("**Missing Values**")
                st.write(df.isnull().sum())

    # =========================================================
    # ANALYTICS PAGE
    # =========================================================
    elif page == "Analytics":
        tab1, tab2, tab3 = st.tabs(["Distributions", "Subject Comparison", "Data Cleaning"])

        with tab1:
            if subject_columns:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<p class="panel-title">Average Marks Distribution</p>', unsafe_allow_html=True)
                    fig, ax = plt.subplots(figsize=(6, 4))
                    ax.hist(df["Average"], bins=8, color=PALETTE[0], edgecolor="white")
                    ax.set_xlabel("Average Marks")
                    ax.set_ylabel("Number of Students")
                    ax.spines[["top", "right"]].set_visible(False)
                    st.pyplot(fig)
                with col2:
                    if "Attendance" in df.columns:
                        st.markdown('<p class="panel-title">Attendance Distribution</p>', unsafe_allow_html=True)
                        fig2, ax2 = plt.subplots(figsize=(6, 4))
                        ax2.hist(df["Attendance"], bins=8, color=PALETTE[1], edgecolor="white")
                        ax2.set_xlabel("Attendance (%)")
                        ax2.set_ylabel("Number of Students")
                        ax2.spines[["top", "right"]].set_visible(False)
                        st.pyplot(fig2)

                if "Attendance" in df.columns:
                    st.markdown('<p class="panel-title">Attendance vs Average Marks</p>', unsafe_allow_html=True)
                    fig3, ax3 = plt.subplots(figsize=(10, 4.2))
                    ax3.scatter(df["Attendance"], df["Average"], color=PALETTE[2],
                                edgecolor="white", s=70, alpha=0.85)
                    ax3.set_xlabel("Attendance (%)")
                    ax3.set_ylabel("Average Marks")
                    ax3.spines[["top", "right"]].set_visible(False)
                    st.pyplot(fig3)

        with tab2:
            if subject_columns:
                st.markdown('<p class="panel-title">Subject-wise Score Spread</p>', unsafe_allow_html=True)
                fig4, ax4 = plt.subplots(figsize=(10, 4.5))
                box_data = [df[s] for s in subject_columns]
                bp = ax4.boxplot(box_data, labels=subject_columns, patch_artist=True)
                for patch, color in zip(bp["boxes"], PALETTE):
                    patch.set_facecolor(color)
                    patch.set_alpha(0.7)
                ax4.set_ylabel("Marks")
                ax4.spines[["top", "right"]].set_visible(False)
                plt.setp(ax4.get_xticklabels(), rotation=20, ha="right")
                fig4.tight_layout()
                st.pyplot(fig4)

        with tab3:
            st.markdown('<p class="panel-title">Duplicate Rows</p>', unsafe_allow_html=True)
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

            st.markdown('<p class="panel-title">Statistical Summary</p>', unsafe_allow_html=True)
            st.dataframe(df.describe(), use_container_width=True)

    # =========================================================
    # REPORTS PAGE
    # =========================================================
    elif page == "Reports":
        st.markdown('<p class="panel-title">Download Cleaned Dataset</p>', unsafe_allow_html=True)
        st.write("Your current dataset — including Average, Grade, and Status columns — is ready to export.")
        st.download_button(
            label="Download Full Report (CSV)",
            data=df.to_csv(index=False),
            file_name="cleaned_student_performance.csv",
            mime="text/csv",
            type="primary"
        )

        if subject_columns:
            st.markdown('<p class="panel-title">Class Summary</p>', unsafe_allow_html=True)
            summary_col1, summary_col2, summary_col3 = st.columns(3)
            summary_col1.metric("Class Average", f"{df['Average'].mean():.1f}")
            summary_col2.metric("Highest Average", f"{df['Average'].max():.1f}")
            summary_col3.metric("Lowest Average", f"{df['Average'].min():.1f}")

    st.markdown('<div class="footer-note">Student Performance Data Curator</div>', unsafe_allow_html=True)
