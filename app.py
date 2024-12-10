import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dca import dca_exponential, dca_harmonic, dca_hyperbolic
from adt import ProductionData
from analysis import measure_execution_time, calculate_error_metrics, descriptive_statistics, analyze_prediction_accuracy
from fpdf import FPDF

#judul aplikasi
st.title("Simulasi Produksi Minyak - Metode DCA")

#inisialisasi ADT
data_storage = ProductionData()

#upload file dataset
uploaded_file = st.file_uploader("Upload file CSV", type=["csv"])
if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.write("Data Input:", data)

    #input parameter untuk DCA
    st.sidebar.header("Parameter DCA")
    method = st.sidebar.selectbox("Metode DCA", ["Eksponensial", "Harmonik", "Hiperbolik"])
    qi = st.sidebar.number_input("Produksi awal (qi)", min_value=0.0, value=500.0, step=10.0)
    b = st.sidebar.number_input("Decline rate (b)", min_value=0.0, value=0.02, step=0.01)
    n = 1.0
    if method == "Hiperbolik":
        n = st.sidebar.number_input("Hyperbolic factor (n)", min_value=0.1, value=1.0, step=0.1)

    future_days = 30  

    #hitung produksi berdasarkan metode DCA
    t = np.append(data['Day'], range(data['Day'].max() + 1, data['Day'].max() + future_days + 1))
    if method == "Eksponensial":
        production_pred, exec_time = measure_execution_time(dca_exponential, qi, b, t)
    elif method == "Harmonik":
        production_pred, exec_time = measure_execution_time(dca_harmonic, qi, b, t)
    elif method == "Hiperbolik":
        production_pred, exec_time = measure_execution_time(dca_hyperbolic, qi, b, t, n)

    #metrik error
    error_metrics = calculate_error_metrics(data['Production (bbl/day)'], production_pred[:len(data)])
    st.write("**Metrik Error:**")
    st.write(f"MAE: {error_metrics['MAE']:.2f}")
    st.write(f"MSE: {error_metrics['MSE']:.2f}")
    st.write(f"RMSE: {error_metrics['RMSE']:.2f}")

    #statistik deskriptif
    stats = descriptive_statistics(data['Production (bbl/day)'])
    st.write("**Statistik Deskriptif Data Produksi:**")
    st.json(stats)

    #perbandingan data aktual vs prediksi
    comparison = analyze_prediction_accuracy(data['Production (bbl/day)'], production_pred[:len(data)])
    st.write("**Perbandingan Produksi Aktual dan Prediksi:**")
    st.dataframe(comparison)

    #tambahan produksi untuk mempertahankan target produksi
    target_production = st.sidebar.number_input("Target Produksi (bbl/day)", min_value=0.0, value=500.0, step=10.0)
    shortfall = target_production - production_pred[-future_days:]
    additional_production = [max(0, s) for s in shortfall]

    #visualisasi grafik
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Day'], y=data['Production (bbl/day)'], mode='lines+markers', name='Produksi Aktual'))
    fig.add_trace(go.Scatter(x=t, y=production_pred, mode='lines', name='Produksi Prediksi DCA'))
    fig.update_layout(title="Grafik Produksi Minyak", xaxis_title="Hari", yaxis_title="Produksi (bbl/day)")
    st.plotly_chart(fig)

    #prediksi produksi masa depan
    future_data = pd.DataFrame({
        'Hari': t[-future_days:],
        'Produksi Prediksi DCA': production_pred[-future_days:],
        'Tambahan Produksi Diperlukan': additional_production
    })
    st.write("**Prediksi Produksi ke Depan (30 hari):**")
    st.write(future_data)

    #laporan PDF
    if st.button("Generate PDF Report"):
        class PDFReport(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, "Laporan Analisis Produksi Minyak", border=False, ln=True, align='C')

            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Halaman {self.page_no()}', 0, 0, 'C')

        pdf = PDFReport()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, "Ringkasan Prediksi Produksi", ln=True)
        pdf.ln(10)
        pdf.multi_cell(0, 10, f"Metode DCA: {method}\nProduksi Awal (qi): {qi} bbl/day\nDecline Rate (b): {b}\n"
                               f"Hyperbolic Factor (n): {n if method == 'Hiperbolik' else 'N/A'}\n"
                               f"Prediksi Produksi Selama 30 Hari: {production_pred[-future_days:].mean():.2f} bbl/day\n"
                               f"Tambahan Produksi Dibutuhkan: {sum(additional_production):.2f} bbl.")
        pdf_path = "Production_Report_DCA.pdf"
        pdf.output(pdf_path)

        with open(pdf_path, "rb") as pdf_file:
            st.download_button("Unduh Laporan PDF", data=pdf_file, file_name="Production_Report_DCA.pdf")