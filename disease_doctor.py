import streamlit as st
import pandas as pd
from collections import Counter
from sklearn.preprocessing import LabelEncoder
from sklearn import metrics, tree, svm
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from fpdf import FPDF
import base64

# Load datasets
dis_sym_data = pd.read_csv("Original_Dataset.csv")
doc_data = pd.read_csv("Doctor_Versus_Disease.csv", encoding='latin1', names=['Disease', 'Specialist'])
des_data = pd.read_csv("Disease_Description.csv")

# Step 1: Prepare binary symptom columns
columns_to_check = [col for col in dis_sym_data.columns if col != 'Disease']
symptoms_list = list(set(dis_sym_data.iloc[:, 1:].values.flatten()))
symptoms_list = [s for s in symptoms_list if pd.notna(s)]

for symptom in symptoms_list:
    dis_sym_data[symptom] = dis_sym_data.iloc[:, 1:].apply(lambda row: int(symptom in row.values), axis=1)

dis_sym_data_v1 = dis_sym_data.drop(columns=columns_to_check)
dis_sym_data_v1 = dis_sym_data_v1.loc[:, dis_sym_data_v1.columns.notna()]
dis_sym_data_v1.columns = dis_sym_data_v1.columns.str.strip()

# Encode labels
le = LabelEncoder()
dis_sym_data_v1['Disease'] = le.fit_transform(dis_sym_data_v1['Disease'])
X = dis_sym_data_v1.drop(columns="Disease")
y = dis_sym_data_v1['Disease']

# Train models
algorithms = {
    'Logistic Regression': LogisticRegression(),
    'Decision Tree': tree.DecisionTreeClassifier(),
    'Random Forest': RandomForestClassifier(),
    'SVM': svm.SVC(probability=True),
    'NaiveBayes': GaussianNB(),
    'K-Nearest Neighbors': KNeighborsClassifier(),
}
for model in algorithms.values():
    model.fit(X, y)


# PDF Report Generator
def generate_pdf_report(symptoms, result_df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Disease Prediction Report", ln=True, align='C')

    pdf.cell(200, 10, txt="Symptoms Provided: " + ", ".join(symptoms), ln=True)

    for i, row in result_df.iterrows():
        pdf.cell(200, 10, txt=f"{row['Disease']} - {row['Chances']:.2f}% chance", ln=True)
        pdf.cell(200, 10, txt=f"Specialist: {row['Specialist']}", ln=True)
        if pd.notna(row['Description']):
            pdf.multi_cell(0, 10, txt=f"Description: {row['Description']}", align='L')
        pdf.cell(200, 10, txt="--------------------------------------", ln=True)

    return pdf.output(dest='S').encode('latin-1')


# Streamlit UI
st.title("Disease Predictor & Doctor Recommender")
st.write("Enter your symptoms to predict possible diseases and recommended specialists.")

selected_symptoms = st.multiselect("Select Symptoms", symptoms_list)

if st.button("Predict Disease"):
    test_data = {col: 1 if col in selected_symptoms else 0 for col in X.columns}
    test_df = pd.DataFrame(test_data, index=[0])

    predicted = []
    for model_name, model in algorithms.items():
        pred = model.predict(test_df)
        disease = le.inverse_transform(pred)[0]
        predicted.append(disease)

    disease_counts = Counter(predicted)
    percentage_per_disease = {disease: (count / 6) * 100 for disease, count in disease_counts.items()}
    result_df = pd.DataFrame({
        "Disease": list(percentage_per_disease.keys()),
        "Chances": list(percentage_per_disease.values())
    })
    result_df = result_df.merge(doc_data, on='Disease', how='left')
    result_df = result_df.merge(des_data, on='Disease', how='left')

    st.subheader("Prediction Results")
    st.dataframe(result_df)

    # Generate PDF and download
    report_data = generate_pdf_report(selected_symptoms, result_df)
    b64 = base64.b64encode(report_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Disease_Prediction_Report.pdf">📄 Download Report as PDF</a>'
    st.markdown(href, unsafe_allow_html=True)
