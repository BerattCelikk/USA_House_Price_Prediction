import streamlit as st
import pandas as pd
import numpy as np
import joblib
import time

# 1. Page Configuration
st.set_page_config(
    page_title="House Price Predictor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .prediction-text {
        font-size: 24px;
        font-weight: bold;
        color: #2e7d32;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Load Pre-trained Assets
@st.cache_resource
def load_assets():
    """Load the machine learning model, scaler, and feature list."""
    try:
        model = joblib.load('house_prediction_model.pkl')
        scaler = joblib.load('scaler.pkl')
        feature_names = joblib.load('features.pkl')
        return model, scaler, feature_names
    except FileNotFoundError:
        return None, None, None

model, scaler, feature_names = load_assets()

# 3. Sidebar - User Inputs
st.sidebar.image("https://img.icons8.com/fluency/96/home.png", width=100)
st.sidebar.title("Configuration")
st.sidebar.info("Adjust the sliders below to define house characteristics.")

def get_user_input():
    # Primary Features (Direct Inputs)
    income = st.sidebar.slider("Avg. Area Income ($)", 20000, 110000, 68000, help="Annual income of the residents in the area.")
    house_age = st.sidebar.slider("Avg. House Age", 1, 10, 5, help="Average age of houses in the neighborhood.")
    rooms = st.sidebar.slider("Number of Rooms", 2, 12, 7)
    bedrooms = st.sidebar.slider("Number of Bedrooms", 1, 8, 4)
    population = st.sidebar.slider("Area Population", 200, 70000, 35000)

    # Secondary Features (Feature Engineering)
    # These must match the logic used in your Jupyter Notebook
    income_age_interact = income * house_age
    income_per_room = income / rooms
    rooms_per_bedroom = rooms / bedrooms

    # Create Dictionary matching the training feature set
    data = {
        'Avg. Area Income': income,
        'Avg. Area House Age': house_age,
        'Avg. Area Number of Rooms': rooms,
        'Avg. Area Number of Bedrooms': bedrooms,
        'Area Population': population,
        'Income_Age_Interact': income_age_interact,
        'Income_per_Room': income_per_room,
        'Rooms_per_Bedroom': rooms_per_bedroom
    }
    
    # Ensure columns are in the exact order the model expects
    return pd.DataFrame(data, index=[0])

# Get inputs
input_df = get_user_input()

# 4. Main Application Layout
st.title("AI-Powered House Price Predictor")
st.write("Leveraging **Gradient Boosting Regression** to estimate property values with **90.41% accuracy**.")

if model is None:
    st.error("Model assets (.pkl files) not found. Please run your Jupyter Notebook first to export the model.")
else:
    # App Tabs
    tab1, tab2 = st.tabs(["Prediction", "Model Insights"])

    with tab1:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Selected Parameters")
            # Displaying only the 5 main features for a cleaner UI
            st.table(input_df.iloc[:, :5].T.rename(columns={0: 'Value'}))

        with col2:
            st.subheader("Valuation Result")
            if st.button("Calculate Property Value"):
                with st.spinner('AI is analyzing market trends...'):
                    time.sleep(1) # Visual effect
                    
                    # Preprocessing & Prediction
                    scaled_input = scaler.transform(input_df)
                    prediction = model.predict(scaled_input)[0]
                    
                    # Output
                    st.success("Analysis Complete!")
                    st.markdown(f"<p class='prediction-text'>Estimated Value: ${prediction:,.2f}</p>", unsafe_allow_html=True)
                    
                    # Secondary Metric
                    st.metric(label="Market Valuation", value=f"${prediction/1e6:.3f} M", delta="USD")
                    

    with tab2:
        st.subheader("Feature Importance Analysis")
        st.write("The chart below shows which factors have the most significant impact on the final price according to our model.")
        
        # Calculate feature importance
        importances = model.feature_importances_
        imp_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances}).sort_values(by='Importance', ascending=True)
        
        st.bar_chart(data=imp_df, x='Feature', y='Importance', color="#007bff")
        st.info("**Insight:** Income and House Age interaction is the strongest predictor in this dataset.")

# 5. Footer
st.divider()
