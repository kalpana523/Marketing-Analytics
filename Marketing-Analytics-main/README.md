🚀 Marketing Campaign Intelligence Dashboard

A full-stack data analytics project that simulates, cleans, visualizes, and automates reporting for multi-channel marketing campaigns. Built with Python and Streamlit.

👉 Live Link ->https://marketing-analytics-tyzrf7wtuxspzrhupx2fhd.streamlit.app/

📖 Project Overview

This application serves as a comprehensive tool for marketing data analysis. It addresses the common challenge of fragmented campaign data by providing a unified interface to:

Generate realistic synthetic data (simulating 5+ digital channels).

Clean "dirty" data using an automated pipeline (handling duplicates, nulls, and formatting errors).

Visualize performance via interactive dashboards (ROI, CTR, Spend Efficiency).

Automate reporting by generating download-ready CSV summaries.

This project demonstrates end-to-end data engineering and analysis skills, from data creation to stakeholder reporting.

✨ Key Features

Data Simulation Engine: Generates realistic datasets with baked-in seasonality, weekend trends, and channel-specific logic (e.g., higher CPC for LinkedIn, higher volume for Facebook).

Interactive Data Cleaning: A module that allows users to intentionally inject noise (duplicates, errors) and then run a cleaning pipeline to fix it in real-time.

Dynamic Dashboards: Built with Plotly for interactive zooming and filtering on metrics like ROI, Conversion Rates, and CPC.

Automated Reporting: One-click generation of monthly executive summary reports, reducing manual analysis time.

🛠️ Tech Stack

Python: Core logic and data processing.

Streamlit: Web application framework and frontend UI.

Pandas: Data manipulation and aggregation.

Plotly: Interactive data visualization.

NumPy: Statistical operations and synthetic data generation.

⚙️ Installation & Setup

To run this project locally, follow these steps:

Clone the repository

git clone [https://github.com/asmit124/Marketing-Analytics.git](https://github.com/asmit124/Marketing-Analytics.git)
cd Marketing-Analytics


Install dependencies

pip install -r requirements.txt


Run the application

streamlit run app.py


📂 Project Structure

├── app.py                 # Main Streamlit application
├── generate_dataset.py    # Standalone script for generating large datasets
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation


📊 Dashboard Modules

ROI Analysis: compares return on investment across Facebook, Google Ads, LinkedIn, etc.

Channel Performance: A scatter plot analyzing the correlation between Click-Through Rate (CTR) and Conversion Rate.

Time Series: Weekly trends for revenue and spend to identify seasonal spikes.

Data Cleaning: A dedicated tab to view raw vs. processed data health (nulls, duplicates).

Created by Asmit Singh - 2025
