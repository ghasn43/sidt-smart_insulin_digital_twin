"""
Optimization objectives for Smart Insulin Digital Twin.
"""

from typing import Dict, Tuple, Optional
import numpy as np


def glucose_control_objective(
    trial_params: Dict,
    simulation_result,
    weights: Optional[Dict] = None
) -> float:
    """
    Objective for glucose control quality.
    Higher value = better control.
    
    Returns: Score from 0-100
    """
    if weights is None:
        weights = {
            'tir': 0.4,
            'variability': 0.25,
            'hypoglycemia': 0.2,
            'hyperglycemia': 0.15,
        }
    
    score = 0.0
    
    # Time in range (70-180) - goal >= 70%
    tir_score = min(100, simulation_result.time_in_range_70_180)
    score += tir_score * weights['tir']
    
    # Glucose variability - penalize high variability
    variability_penalty = min(100, simulation_result.glucose_variability * 2)
    variability_score = 100 - variability_penalty
    score += variability_score * weights['variability']
    
    # Hypoglycemia - critical, penalize heavily
    hypo_penalty = simulation_result.time_below_70 * 10  # 1% below 70 = -10 points
    hypo_score = max(0, 100 - hypo_penalty)
    score += hypo_score * weights['hypoglycemia']
    
    # Hyperglycemia - less critical than hypo
    hyper_penalty = simulation_result.time_above_180 * 3
    hyper_score = max(0, 100 - hyper_penalty)
    score += hyper_score * weights['hyperglycemia']
    
    return round(score, 1)


def safety_objective(trial_params: Dict, patient_data: Dict) -> float:
    """
    Objective for system safety.
    Higher value = safer system.
    
    Returns: Score from 0-100
    """
    score = 100.0
    
    # Hypoglycemia risk
    hypo_risk = trial_params.get('hypoglycemia_risk_percent', 10)
    if hypo_risk > 5:
        score -= (hypo_risk - 5) * 5
    
    # Hardware failure rate
    failure_rate = trial_params.get('device_failure_rate_percent', 1)
    score -= failure_rate * 10
    
    # Needle/insertion complications
    insertion_complication = trial_params.get('insertion_complication_rate_percent', 2)
    score -= insertion_complication * 5
    
    # Software safety (cryptographic security, redundancy)
    software_safety = trial_params.get('software_safety_score', 50)
    score += (software_safety / 100) * 10
    
    return max(0, round(score, 1))


def manufacturability_objective(trial_params: Dict) -> float:
    """
    Objective for manufacturability.
    Higher value = easier to manufacture.
    
    Returns: Score from 0-100
    """
    score = 100.0
    
    # Nano size complexity (smaller = harder)
    nano_size_nm = trial_params.get('nano_size_nm', 200)
    if nano_size_nm < 50:
        score -= 20
    elif nano_size_nm < 100:
        score -= 10
    elif nano_size_nm > 500:
        score -= 5
    
    # Drug loading percentage
    drug_loading = trial_params.get('drug_loading_percent', 20)
    if drug_loading > 40 or drug_loading < 5:
        score -= 15
    
    # Release mechanism
    release_mechanism = trial_params.get('release_mechanism', 'sustained')
    if release_mechanism == 'pulsatile':
        score -= 20
    elif release_mechanism == 'triggered':
        score -= 10
    
    # Production yield
    yield_percent = trial_params.get('production_yield_percent', 60)
    score += (yield_percent / 100) * 20 - 10
    
    # Cost factor
    estimated_cost_usd = trial_params.get('estimated_cost_per_injection', 50)
    cost_score = max(0, 100 - (estimated_cost_usd / 20))
    score += cost_score * 0.2
    
    return max(0, round(score, 1))


def efficacy_objective(
    simulation_result,
    target_mean_glucose: float = 120,
    target_tir: float = 70
) -> float:
    """
    Objective for clinical efficacy.
    
    Returns: Score from 0-100
    """
    score = 0.0
    
    # Mean glucose closeness to target
    glucose_diff = abs(simulation_result.mean_glucose - target_mean_glucose)
    if glucose_diff < 10:
        glucose_score = 100
    elif glucose_diff < 30:
        glucose_score = 80 - (glucose_diff - 10) / 2
    else:
        glucose_score = max(0, 50 - (glucose_diff - 30) / 5)
    
    score += glucose_score * 0.4
    
    # TIR achievement
    if simulation_result.time_in_range_70_180 >= target_tir:
        tir_score = 100
    else:
        tir_score = (simulation_result.time_in_range_70_180 / target_tir) * 100
    
    score += tir_score * 0.35
    
    # Stability (low variability)
    if simulation_result.glucose_variability < 20:
        variability_score = 100
    elif simulation_result.glucose_variability < 35:
        variability_score = 80 - (simulation_result.glucose_variability - 20) / 2
    else:
        variability_score = max(0, 60 - (simulation_result.glucose_variability - 35) / 2)
    
    score += variability_score * 0.25
    
    return round(score, 1)


def cost_objective(trial_params: Dict) -> float:
    """
    Objective for cost minimization.
    Lower cost = higher score.
    
    Returns: Score from 0-100
    """
    device_cost = trial_params.get('device_cost_usd', 500)
    injection_cost = trial_params.get('injection_cost_usd', 50)
    monthly_disposables = trial_params.get('monthly_disposables_cost_usd', 100)
    
    # Typical insulin costs $50-300 per month
    # Target: < $300 total monthly cost
    monthly_total = injection_cost + monthly_disposables
    
    cost_score = max(0, 100 - (monthly_total / 3))
    
    return round(cost_score, 1)


def multi_objective_function(
    simulation_result,
    trial_params: Dict,
    patient_data: Dict,
    objectives_weights: Optional[Dict] = None
) -> Tuple[float, Dict]:
    """
    Combined multi-objective optimization function.
    
    Returns:
    combined_score: Weighted sum of all objectives
    objective_breakdown: Dict of individual objective scores
    """
    if objectives_weights is None:
        objectives_weights = {
            'glucose_control': 0.35,
            'safety': 0.25,
            'manufacturability': 0.20,
            'efficacy': 0.15,
            'cost': 0.05,
        }
    
    breakdown = {
        'glucose_control': glucose_control_objective(trial_params, simulation_result),
        'safety': safety_objective(trial_params, patient_data),
        'manufacturability': manufacturability_objective(trial_params),
        'efficacy': efficacy_objective(simulation_result),
        'cost': cost_objective(trial_params),
    }
    
    combined = sum(breakdown[key] * objectives_weights[key] 
                   for key in breakdown if key in objectives_weights)
    
    return round(combined, 1), breakdown


def constraint_checker(trial_params: Dict) -> Tuple[bool, list]:
    """
    Check hard constraints (must be satisfied).
    
    Returns:
    is_feasible: Boolean indicating if all constraints are met
    violated_constraints: List of constraint names that are violated
    """
    violations = []
    
    # Safety constraints
    if trial_params.get('hypoglycemia_risk_percent', 100) > 15:
        violations.append('hypoglycemia_risk_too_high')
    
    # Hardware constraints
    if trial_params.get('device_failure_rate_percent', 100) > 5:
        violations.append('device_failure_rate_too_high')
    
    # Manufacturing constraints
    if trial_params.get('production_yield_percent', 0) < 20:
        violations.append('production_yield_too_low')
    
    # Regulatory constraints
    if trial_params.get('time_below_70_percent', 100) > 10:
        violations.append('hypoglycemia_percentage_too_high')
    
    # Cost constraints (optional)
    monthly_cost = trial_params.get('injection_cost_usd', 0) + trial_params.get('monthly_disposables_cost_usd', 0)
    if monthly_cost > 500:  # Arbitrary limit
        violations.append('monthly_cost_too_high')
    
    is_feasible = len(violations) == 0
    return is_feasible, violations
