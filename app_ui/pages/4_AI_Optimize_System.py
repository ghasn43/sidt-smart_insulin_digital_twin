"""
Page 4: AI-Powered System Optimization
"""

import streamlit as st
import sys
from pathlib import Path
import json

backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

from backend.optimize.optuna_runner import OptimizationRunner
from backend.optimize.objectives import multi_objective_function, constraint_checker
from backend.optimize.search_space import define_insulin_search_space

st.set_page_config(page_title="AI Optimize System", page_icon="🤖", layout="wide")
st.title("🤖 Multi-Objective System Optimization")

st.markdown("""
Use AI to optimize insulin delivery system parameters across multiple objectives:
efficacy, safety, manufacturability, and cost.
""")

# Optimization settings
st.sidebar.markdown("## Optimization Configuration")

n_trials = st.sidebar.slider("Number of Trials", 10, 500, 100, step=10)
sampler_type = st.sidebar.selectbox("Sampler Algorithm", ["tpe", "random"])

# Objective weights
st.sidebar.markdown("## Objective Weights")
weight_efficacy = st.sidebar.slider("Efficacy Weight", 0.0, 1.0, 0.35, step=0.05)
weight_safety = st.sidebar.slider("Safety Weight", 0.0, 1.0, 0.25, step=0.05)
weight_mfg = st.sidebar.slider("Manufacturability Weight", 0.0, 1.0, 0.20, step=0.05)
weight_cost = st.sidebar.slider("Cost Weight", 0.0, 1.0, 0.20, step=0.05)

# Normalize weights
total_weight = weight_efficacy + weight_safety + weight_mfg + weight_cost
weights = {
    'glucose_control': weight_efficacy / total_weight,
    'safety': weight_safety / total_weight,
    'manufacturability': weight_mfg / total_weight,
    'cost': weight_cost / total_weight,
}

st.sidebar.markdown("---")

# Run optimization
if st.sidebar.button("▶️ Start Optimization", use_container_width=True):
    st.markdown("### Optimization Running...")
    
    # Create a mock objective function
    def objective_func(params):
        # Simple mock scoring
        score = 50
        if 'basal_insulin_rate' in params:
            score += min(20, abs(1.5 - params['basal_insulin_rate']) * 5)
        if 'nano_size_nm' in params:
            if 100 <= params['nano_size_nm'] <= 300:
                score += 15
        if 'production_yield_percent' in params:
            score += params['production_yield_percent'] / 10
        return min(100, score)
    
    # Get search space
    search_space_def = define_insulin_search_space()
    search_space = search_space_def.to_optuna_dict()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Run optimization
    runner = OptimizationRunner(
        objective_func=objective_func,
        search_space=search_space,
        n_trials=n_trials,
        sampler=sampler_type,
        use_optuna=False  # Use local search for demo
    )
    
    # Run with progress tracking
    for i in range(n_trials):
        # Simulate optimization step
        runner._run_local_search() if i == n_trials - 1 else None
        progress = (i + 1) / n_trials
        progress_bar.progress(progress)
        status_text.text(f"Trial {i+1}/{n_trials} - Best: {runner.get_best_score():.1f}")
    
    # Final optimization run
    best_trial, all_trials = runner.run()
    
    st.session_state.optimization_runner = runner
    st.session_state.best_trial = best_trial
    st.session_state.all_trials = all_trials
    st.session_state.weights = weights
    
    st.success(f"✅ Optimization complete! Best score: {best_trial.combined_score:.1f}/100")

# Display optimization results
if 'best_trial' in st.session_state:
    runner = st.session_state.optimization_runner
    best_trial = st.session_state.best_trial
    
    st.markdown("---")
    st.markdown("### Optimization Results")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Best Score", f"{best_trial.combined_score:.1f}/100")
    with col2:
        st.metric("Total Trials", len(st.session_state.all_trials))
    with col3:
        st.metric("Average Score", 
                 f"{sum(t.combined_score for t in st.session_state.all_trials) / len(st.session_state.all_trials):.1f}/100")
    
    st.markdown("---")
    st.markdown("### Best Parameters Found")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**System Parameters:**")
        for key, value in list(best_trial.parameters.items())[:6]:
            if isinstance(value, float):
                st.write(f"• {key}: {value:.2f}")
            else:
                st.write(f"• {key}: {value}")
    
    with col2:
        st.markdown("**Additional Parameters:**")
        for key, value in list(best_trial.parameters.items())[6:]:
            if isinstance(value, float):
                st.write(f"• {key}: {value:.2f}")
            else:
                st.write(f"• {key}: {value}")
    
    # Visualization
    st.markdown("---")
    st.markdown("### Optimization Progress")
    
    try:
        fig = runner.plot_optimization_history()
        if fig:
            st.pyplot(fig)
    except:
        st.info("Progress visualization not available")
    
    # Parameter importance
    st.markdown("---")
    st.markdown("### Top Performing Parameter Ranges")
    
    # Analyze which parameters appear in best trials
    top_n = min(10, len(st.session_state.all_trials))
    top_trials = sorted(st.session_state.all_trials, key=lambda t: t.combined_score, reverse=True)[:top_n]
    
    st.info(f"Analyzing top {top_n} trials to identify key parameter ranges...")
    
    for param_name in list(best_trial.parameters.keys())[:5]:
        values = [t.parameters[param_name] for t in top_trials if isinstance(t.parameters[param_name], (int, float))]
        if values:
            mean_val = sum(values) / len(values)
            min_val = min(values)
            max_val = max(values)
            st.write(f"**{param_name}**: {min_val:.2f} - {max_val:.2f} (avg: {mean_val:.2f})")
    
    # Export options
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Results"):
            runner.export_results("optimization_results.json")
            st.success("Results exported!")
    
    with col2:
        if st.button("📋 Copy Best Parameters"):
            params_json = json.dumps(best_trial.parameters, indent=2, default=str)
            st.code(params_json)
    
    with col3:
        if st.button("💾 Save Configuration"):
            st.success("Configuration saved!")

else:
    st.info("👈 Configure optimization settings and click 'Start Optimization'")
