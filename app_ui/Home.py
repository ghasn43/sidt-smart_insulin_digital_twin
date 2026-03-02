"""
Home page for Smart Insulin Digital Twin.
Main Streamlit interface.
"""

import streamlit as st
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

st.set_page_config(
    page_title="Smart Insulin Digital Twin",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="main-header">
    🧬 Smart Insulin Digital Twin
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
    ## Advanced In Silico Optimization Platform for Insulin Delivery Systems

    Welcome to the Smart Insulin Digital Twin - a comprehensive platform for designing, 
    simulating, and optimizing personalized insulin delivery systems using AI and 
    computational biology.
    """)

# Main navigation
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="feature-box">
        <h3>📊 Simulate Patient</h3>
        <p>Simulate individualized glucose dynamics for specific patients</p>
        </div>
        """, unsafe_allow_html=True)
    if st.button("Go to Simulation", key="sim_btn"):
        st.switch_page("pages/1_Simulate_Patient.py")

with col2:
    st.markdown("""
        <div class="feature-box">
        <h3>💊 Design Nano Release</h3>
        <p>Engineer optimal nanoparticle formulations and release profiles</p>
        </div>
        """, unsafe_allow_html=True)
    if st.button("Go to Nano Design", key="nano_btn"):
        st.switch_page("pages/2_Design_Nano_Release.py")

with col3:
    st.markdown("""
        <div class="feature-box">
        <h3>🧪 Manufacturing DNA</h3>
        <p>Optimize insulin variant manufacturability and genetic design</p>
        </div>
        """, unsafe_allow_html=True)
    if st.button("Go to Manufacturing", key="mfg_btn"):
        st.switch_page("pages/3_Manufacturability_DNA.py")

# Second row of features
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="feature-box">
        <h3>🤖 AI Optimization</h3>
        <p>Run multi-objective optimization using ML algorithms</p>
        </div>
        """, unsafe_allow_html=True)
    if st.button("Go to Optimization", key="opt_btn"):
        st.switch_page("pages/4_AI_Optimize_System.py")

with col2:
    st.markdown("""
        <div class="feature-box">
        <h3>📈 Reports & Exports</h3>
        <p>Generate comprehensive reports and export results</p>
        </div>
        """, unsafe_allow_html=True)
    if st.button("Go to Reports", key="report_btn"):
        st.switch_page("pages/5_Reports_Exports.py")

with col3:
    st.markdown("""
        <div class="feature-box">
        <h3>ℹ️ About</h3>
        <p>Learn more about the platform and methodology</p>
        </div>
        """, unsafe_allow_html=True)

# Feature overview
st.markdown("---")
st.markdown("## Platform Features")

features_col1, features_col2 = st.columns(2)

with features_col1:
    st.markdown("""
    ### Core Capabilities
    - **Glucose Dynamics Simulation**: Bergman minimal model with individualized parameters
    - **Patient Profiling**: BMI, insulin sensitivity, carb ratio, dawn phenomenon
    - **Nanoparticle Design**: Size optimization, drug loading, release mechanisms
    - **Genetic Optimization**: Codon optimization, reverse translation, QC checks
    - **Control Algorithms**: PID, model predictive control, closed-loop simulation
    - **Risk Assessment**: Hypoglycemia, hyperglycemia, stability analysis
    """)

with features_col2:
    st.markdown("""
    ### Optimization Framework
    - **Multi-Objective**: Efficacy, safety, manufacturability, cost
    - **AI-Powered**: Optuna-based hyperparameter optimization
    - **Constraint Handling**: Hard and soft manufacturing constraints
    - **Sensitivity Analysis**: Parameter importance testing
    - **Scenario Testing**: Stress, exercise, cold exposure scenarios
    - **Report Generation**: Detailed metrics, visualizations, recommendations
    """)

# Getting started
st.markdown("---")
st.markdown("## Getting Started")

with st.expander("1️⃣ Run Your First Simulation"):
    st.write("""
    1. Go to the **Simulate Patient** page
    2. Enter patient parameters (age, weight, insulin sensitivity)
    3. Define a meal schedule and insulin dosing
    4. Click "Run Simulation" to see glucose dynamics
    5. Review metrics and control quality assessment
    """)

with st.expander("2️⃣ Design a Nanoformulation"):
    st.write("""
    1. Navigate to **Design Nano Release**
    2. Specify nanoparticle size and drug loading
    3. Choose a release mechanism (sustained, pulsatile, enzymatic)
    4. Simulate the release profile
    5. Compare against ideal delivery targets
    """)

with st.expander("3️⃣ Optimize Your Insulin Variant"):
    st.write("""
    1. Go to **AI Optimize System**
    2. Define the optimization objectives (efficacy, safety, cost)
    3. Set parameter bounds (dosing, delivery timing, etc)
    4. Run the optimization (100-1000 trials)
    5. Analyze results and export recommendations
    """)

# System requirements
st.sidebar.markdown("---")
st.sidebar.markdown("### About This Platform")
st.sidebar.info("""
    **Smart Insulin Digital Twin v1.0**
    
    Developed by: Research Group
    
    Contact: research@smartinsulin.org
    
    Last Updated: March 2026
""")

st.sidebar.markdown("### Documentation")
st.sidebar.link_button("📖 User Guide", "https://github.com/ghasn43/smartinsulin/wiki")
st.sidebar.link_button("🔬 Research Papers", "https://scholar.google.com")
st.sidebar.link_button("🐛 Report Issues", "https://github.com/ghasn43/smartinsulin/issues")

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats")
col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Model Version", "1.0")
with col2:
    st.metric("Simulations", "Ready")
