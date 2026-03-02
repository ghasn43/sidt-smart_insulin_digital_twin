"""
Page 1: Simulate Patient glucose dynamics.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

# Setup path
backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

from backend.core.models import Patient, SimulationResult
from backend.physiology.simulator import PatientSimulator
from backend.core.metrics import calculate_metrics, assess_control_quality
from backend.core.plotting import plot_glucose_profile, plot_insulin_delivery, plot_daily_patterns
from backend.core.io import DataManager

st.set_page_config(page_title="Simulate Patient", page_icon="📊", layout="wide")
st.title("📊 Patient Glucose Simulation")

# Sidebar for patient input
st.sidebar.markdown("## Patient Profile")

col1, col2 = st.sidebar.columns(2)
with col1:
    age = st.number_input("Age (years)", 18, 90, 35)
    weight_kg = st.number_input("Weight (kg)", 30, 200, 75)
with col2:
    height_cm = st.number_input("Height (cm)", 140, 220, 175)
    insulin_sens = st.slider("Insulin Sensitivity (mg/dL per unit)", 20, 60, 40)

col1, col2 = st.sidebar.columns(2)
with col1:
    basal_rate = st.number_input("Basal Insulin (units/hr)", 0.5, 5.0, 1.5, step=0.1)
    carb_ratio = st.number_input("Carb Ratio (g per unit)", 5, 20, 12)
with col2:
    dawn_phenom = st.checkbox("Dawn Phenomenon", False)
    dawn_mag = st.number_input("Dawn Magnitude (mg/dL)", 0, 100, 20) if dawn_phenom else 0

# Create patient object
patient = Patient(
    patient_id=f"PT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    age=age,
    weight_kg=weight_kg,
    height_cm=height_cm,
    insulin_sensitivity=insulin_sens,
    basal_insulin_rate=basal_rate,
    carb_ratio=carb_ratio,
    dawn_phenomenon=dawn_phenom,
    dawn_magnitude=dawn_mag
)

st.sidebar.markdown("---")
st.sidebar.markdown("## Meal Schedule")

# Meal input
meals = []
meal_times = st.sidebar.multiselect(
    "Meal Times",
    ["Breakfast (7AM)", "Lunch (12PM)", "Dinner (6PM)", "Snack (3PM)"],
    default=["Breakfast (7AM)", "Lunch (12PM)", "Dinner (6PM)"]
)

if "Breakfast (7AM)" in meal_times:
    breakfast_carbs = st.sidebar.number_input("Breakfast Carbs (g)", 30, 100, 60, key="breakfast")
    meals.append((7.0, breakfast_carbs))

if "Lunch (12PM)" in meal_times:
    lunch_carbs = st.sidebar.number_input("Lunch Carbs (g)", 30, 100, 75, key="lunch")
    meals.append((12.0, lunch_carbs))

if "Dinner (6PM)" in meal_times:
    dinner_carbs = st.sidebar.number_input("Dinner Carbs (g)", 30, 100, 80, key="dinner")
    meals.append((18.0, dinner_carbs))

if "Snack (3PM)" in meal_times:
    snack_carbs = st.sidebar.number_input("Snack Carbs (g)", 10, 30, 20, key="snack")
    meals.append((15.0, snack_carbs))

st.sidebar.markdown("---")
st.sidebar.markdown("## Insulin Injections")

# Insulin input
injections = []
st.sidebar.write("Define mealtime bolus doses (units):")
for time_str, carbs in meals:
    dose = st.sidebar.number_input(
        f"Bolus at {int(time_str)}:00",
        0.0, 20.0,
        carbs / patient.carb_ratio,
        step=0.5,
        key=f"bolus_{time_str}"
    )
    if dose > 0:
        injections.append((time_str, dose))

st.sidebar.markdown("---")

# Run simulation
if st.sidebar.button("▶️ Run Simulation", use_container_width=True):
    with st.spinner("Running simulation..."):
        # Initialize simulator
        simulator = PatientSimulator(patient)
        
        # Run simulation
        start_datetime = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        timestamps, glucose, insulin, carbs = simulator.simulate_day(
            start_datetime=start_datetime,
            initial_glucose=120,
            carb_schedule=meals,
            insulin_schedule=injections
        )
        
        # Create result object
        result = SimulationResult(
            patient=patient,
            timestamps=timestamps,
            glucose_mg_dl=glucose,
            insulin_units=insulin,
            carb_intake=carbs,
        )
        
        # Calculate metrics
        result = calculate_metrics(result)
        
        # Store in session state
        st.session_state.simulation_result = result
        st.session_state.timestamps = timestamps
        st.session_state.glucose = glucose
        st.session_state.insulin = insulin
        st.session_state.carbs = carbs
        
        st.success("Simulation complete!")

# Display results
if 'simulation_result' in st.session_state:
    result = st.session_state.simulation_result
    
    st.markdown("---")
    st.markdown("## Simulation Results")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Mean Glucose", f"{result.mean_glucose:.0f} mg/dL")
    with col2:
        st.metric("Time in Range", f"{result.time_in_range_70_180:.1f}%")
    with col3:
        st.metric("Glucose Variability", f"{result.glucose_variability:.1f}%")
    with col4:
        st.metric("Below 70 mg/dL", f"{result.time_below_70:.1f}%")
    
    # Control quality assessment
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Control Quality Assessment")
        assessment = assess_control_quality(result)
        for metric, category in assessment.items():
            st.info(f"**{metric.title()}**: {category}")
    
    with col2:
        st.markdown("### Key Statistics")
        stats = {
            'Std Dev': f"{result.std_glucose:.1f} mg/dL",
            'HyperGlycemic Index': f"{result.hyperglycemic_index:.1f} mg/dL",
            'HypoGlycemic Index': f"{result.hypoglycemic_index:.1f} mg/dL",
            'Time >180': f"{result.time_above_180:.1f}%",
        }
        for label, value in stats.items():
            st.text(f"{label}: {value}")
    
    # Plots
    st.markdown("---")
    st.markdown("### Visualizations")
    
    tab1, tab2, tab3 = st.tabs(["Glucose Profile", "Insulin & Carbs", "Daily Patterns"])
    
    with tab1:
        fig = plot_glucose_profile(st.session_state.timestamps, st.session_state.glucose)
        st.pyplot(fig)
    
    with tab2:
        fig = plot_insulin_delivery(st.session_state.timestamps, st.session_state.insulin, st.session_state.carbs)
        st.pyplot(fig)
    
    with tab3:
        fig = plot_daily_patterns(st.session_state.glucose, st.session_state.timestamps)
        st.pyplot(fig)
    
    # Export options
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Simulation"):
            manager = DataManager()
            manager.save_simulation(result, f"sim_{patient.patient_id}")
            st.success(f"Saved simulation for {patient.patient_id}")
    
    with col2:
        if st.button("📥 Export to CSV"):
            from backend.core.io import export_to_csv
            filepath = f"simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            export_to_csv(result, filepath)
            st.success(f"Exported to {filepath}")
    
    with col3:
        if st.button("📋 Copy Metrics"):
            metrics_text = f"""
            Mean Glucose: {result.mean_glucose:.1f} mg/dL
            Time in Range (70-180): {result.time_in_range_70_180:.1f}%
            Time Below 70: {result.time_below_70:.1f}%
            Time Above 180: {result.time_above_180:.1f}%
            Glucose Variability: {result.glucose_variability:.1f}%
            """
            st.code(metrics_text)

else:
    st.info("👈 Configure patient parameters and click 'Run Simulation' to begin")
