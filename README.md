# Student Performance Data Curator

A Streamlit web app to upload, clean, explore and download student performance data.

## Features

- Upload a CSV of student marks and attendance
- Preview data, check shape, dtypes and missing values
- Remove duplicate rows (persists across interactions)
- View statistical summary
- Visualize average marks vs attendance distribution
- Visualize average marks by subject
- See top 5 performing students
- Download the cleaned dataset as CSV

## Expected CSV format

The app expects the following columns:

| Column | Description |
|---|---|
| Student_ID | Unique student identifier |
| Name | Student name |
| Math | Math score |
| Science | Science score |
| English | English score |
| Attendance | Attendance percentage |

A sample file, `student_performance.csv`, is included in this repo for testing.

## Running locally

```bash
git clone <your-repo-url>
cd <your-repo-folder>
pip install -r requirements.txt
streamlit run app.py
```

## Deploying on Streamlit Community Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click "New app", select this repo, branch, and set the main file to `app.py`.
4. Deploy.
