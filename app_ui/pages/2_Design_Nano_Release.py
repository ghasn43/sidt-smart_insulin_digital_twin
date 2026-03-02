"""
Page 2: Design Nanoparticle Release Systems
"""

import streamlit as st
import sys
from pathlib import Path
import numpy as np

backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

from backend.nano.release_models import NanoFormulation, NanoReleaseModeler
from backend.core.plotting import plot_glucose_profile
import matplotlib.pyplot as plt

st.set_page_config(page_title="Design Nano Release", page_icon="💊", layout="wide")
st.title("💊 Nanoparticle Release Design")

st.markdown("""
Design and optimize insulin-loaded nanoparticles with custom release profiles.
""")

# Sidebar inputs
st.sidebar.markdown("## Nanoparticle Design")

nano_size = st.sidebar.slider("Particle Diameter (nm)", 50, 500, 200, step=20)
drug_load = st.sidebar.slider("Drug Loading (%)", 5, 50, 20, step=1)
release_mech = st.sidebar.selectbox("Release Mechanism", 
    ["sustained", "degradation", "enzymatic", "osmotic"])

st.sidebar.markdown("## Formulation Parameters")
particle_count = st.sidebar.number_input("Total Particles (×10⁹)", 1, 100, 10)
dose_units = st.sidebar.number_input("Total Insulin Dose (units)", 10, 1000, 100, step=10)

# Mechanism-specific parameters
st.sidebar.markdown("## Mechanism Parameters")

if release_mech == "sustained":
    release_rate = st.sidebar.slider("Release Rate (% per hour)", 1, 20, 5)
elif release_mech == "degradation":
    deg_rate = st.sidebar.slider("Degradation Rate (% per hour)", 0.5, 5, 1.5, step=0.1)
    burst = st.sidebar.slider("Burst Release (%)", 0, 50, 20)
elif release_mech == "enzymatic":
    enzyme_conc = st.sidebar.slider("Enzyme Concentration", 0.1, 5.0, 1.0, step=0.1)
elif release_mech == "osmotic":
    osmotic_pressure = st.sidebar.slider("Osmotic Pressure (atm)", 1, 20, 10)

simulation_days = st.sidebar.number_input("Simulation Duration (days)", 1, 30, 7)

st.sidebar.markdown("---")

# Run simulation
if st.sidebar.button("▶️ Simulate Release", use_container_width=True):
    modeler = NanoReleaseModeler()
    
    # Prepare parameters
    params = {
        'dose_units': dose_units,
        'days': simulation_days,
        'mechanism': release_mech,
    }
    
    if release_mech == "sustained":
        params['release_rate_percent_per_hour'] = release_rate
    elif release_mech == "degradation":
        params['degradation_rate'] = deg_rate
        params['burst_release'] = burst
    elif release_mech == "enzymatic":
        params['enzyme_concentration'] = enzyme_conc
    elif release_mech == "osmotic":
        params['osmotic_pressure_difference'] = osmotic_pressure
    
    with st.spinner("Simulating release profile..."):
        time_hours, release = modeler.simulate_release_profile(**params)
        metrics = modeler.compute_metrics(time_hours, release)
        
        st.session_state.time_hours = time_hours
        st.session_state.release = release
        st.session_state.metrics = metrics
        st.success("Release profile simulated!")

# Display results
if 'release' in st.session_state:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Released (units)", f"{st.session_state.metrics['total_released_units']:.1f}")
    with col2:
        st.metric("Burst Release (%)", f"{st.session_state.metrics['burst_release_percent']:.1f}")
    with col3:
        st.metric("Median Release Time (hrs)", f"{st.session_state.metrics['median_release_time_hours']:.1f}")
    
    st.markdown("---")
    
    # Release profile plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Cumulative release
    cumulative = np.cumsum(st.session_state.release)
    ax1.plot(st.session_state.time_hours, cumulative, 'b-', linewidth=2)
    ax1.fill_between(st.session_state.time_hours, 0, cumulative, alpha=0.3)
    ax1.set_xlabel('Time (hours)')
    ax1.set_ylabel('Cumulative Insulin Released (units)')
    ax1.set_title('Cumulative Release Profile')
    ax1.grid(True, alpha=0.3)
    
    # Instantaneous release
    ax2.plot(st.session_state.time_hours, st.session_state.release, 'r-', linewidth=2)
    ax2.fill_between(st.session_state.time_hours, 0, st.session_state.release, alpha=0.3, color='red')
    ax2.set_xlabel('Time (hours)')
    ax2.set_ylabel('Insulin Release Rate (units/hr)')
    ax2.set_title('Instantaneous Release Rate')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Formulation summary
    st.markdown("### Formulation Summary")
    summary = f"""
    - **Particle Size**: {nano_size} nm diameter
    - **Drug Loading**: {drug_load}%
    - **Total Particles**: {particle_count}×10⁹
    - **Total Dose**: {dose_units} units
    - **Release Mechanism**: {release_mech.capitalize()}
    - **Simulation Duration**: {simulation_days} days
    """
    st.markdown(summary)
    
    if st.button("💾 Save Design"):
        st.success("Design saved!")

else:
    st.info("👈 Configure nanoparticle parameters and click 'Simulate Release'")
