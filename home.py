import streamlit as st

st.set_page_config(page_title="Healthcare Assistant App", layout="centered")

# Sidebar Navigation
st.sidebar.title("🩺 Healthcare Navigation")
app_mode = st.sidebar.selectbox(
    "Select Page",
    [
        "Home - About the Project",
        "Disease Prediction",
        "Health Dashboard",
        "Disease & Doctor Recommendation"
    ]
)

# Home / About the Project
if app_mode == "Home - About the Project":
    st.header("Healthcare Recommendation System")
    st.markdown("""
    ### Intelligent Disease Prediction & Health Assistant

    This system uses AI to:
    - Predict diseases from given symptoms
    - Recommend the right medical specialist
    - Present a visual health dashboard
    - Provide detailed disease info and report generation

    #### 🔧 Technologies Used:
    - Machine Learning Models (Random Forest, Naive Bayes, etc.)
    - Streamlit for Web Interface
    - ReportLab for PDF Generation
    - Matplotlib & Seaborn for Dashboards

   
    """)

# Disease Prediction Page
elif app_mode == "Disease Prediction":
    exec(open("health.py", encoding="utf-8").read())

# Health Dashboard Page
elif app_mode == "Health Dashboard":
    exec(open("health_dashboard.py", encoding="utf-8").read())

# Disease and Doctor Recommendation Page
elif app_mode == "Disease & Doctor Recommendation":
    exec(open("disease_doctor.py", encoding="utf-8").read())
