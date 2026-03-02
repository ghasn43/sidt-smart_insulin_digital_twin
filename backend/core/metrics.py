"""
Metrics calculation for Smart Insulin Digital Twin.
"""

import numpy as np
from typing import Tuple, Dict
from .models import SimulationResult


def calculate_metrics(result: SimulationResult) -> SimulationResult:
    """Calculate all metrics for a simulation result."""
    glucose = result.glucose_mg_dl
    
    # Basic statistics
    result.mean_glucose = np.mean(glucose)
    result.std_glucose = np.std(glucose)
    
    # Time in range metrics
    result.time_in_range_70_180 = np.sum((glucose >= 70) & (glucose <= 180)) / len(glucose) * 100
    result.time_above_180 = np.sum(glucose > 180) / len(glucose) * 100
    result.time_below_70 = np.sum(glucose < 70) / len(glucose) * 100
    
    # Glucose variability
    result.glucose_variability = compute_glucose_variability(glucose)
    
    # Risk indices
    result.hyperglycemic_index = compute_hyperglycemic_index(glucose)
    result.hypoglycemic_index = compute_hypoglycemic_index(glucose)
    
    return result


def compute_glucose_variability(glucose_mg_dl: np.ndarray) -> float:
    """
    Compute glucose variability using coefficient of variation.
    Higher values indicate more variable glucose.
    """
    if np.mean(glucose_mg_dl) == 0:
        return 0.0
    return (np.std(glucose_mg_dl) / np.mean(glucose_mg_dl)) * 100


def compute_hyperglycemic_index(glucose_mg_dl: np.ndarray, threshold: float = 180) -> float:
    """
    Compute hyperglycemic index (average excursion above threshold).
    """
    high_values = glucose_mg_dl[glucose_mg_dl > threshold]
    if len(high_values) == 0:
        return 0.0
    return np.mean(high_values - threshold)


def compute_hypoglycemic_index(glucose_mg_dl: np.ndarray, threshold: float = 70) -> float:
    """
    Compute hypoglycemic index (average excursion below threshold).
    """
    low_values = glucose_mg_dl[glucose_mg_dl < threshold]
    if len(low_values) == 0:
        return 0.0
    return np.mean(threshold - low_values)


def assess_control_quality(result: SimulationResult) -> Dict[str, str]:
    """
    Assess overall glucose control quality.
    Returns categories for different metrics.
    """
    assessment = {}
    
    # Mean glucose assessment
    if result.mean_glucose < 100:
        assessment['mean_glucose'] = 'Excellent (Low Risk of Hyperglycemia)'
    elif result.mean_glucose < 130:
        assessment['mean_glucose'] = 'Good'
    elif result.mean_glucose < 180:
        assessment['mean_glucose'] = 'Fair'
    else:
        assessment['mean_glucose'] = 'Poor (High Risk of Hyperglycemia)'
    
    # TIR assessment
    if result.time_in_range_70_180 >= 70:
        assessment['time_in_range'] = 'Excellent (≥70% TIR)'
    elif result.time_in_range_70_180 >= 50:
        assessment['time_in_range'] = 'Good (50-70% TIR)'
    else:
        assessment['time_in_range'] = 'Poor (<50% TIR)'
    
    # Glucose variability assessment
    if result.glucose_variability < 20:
        assessment['variability'] = 'Excellent (Low Variability)'
    elif result.glucose_variability < 35:
        assessment['variability'] = 'Good (Moderate Variability)'
    else:
        assessment['variability'] = 'High Variability'
    
    # Hypoglycemia risk
    if result.time_below_70 < 5:
        assessment['hypoglycemia'] = 'Low Risk (<5% time below 70)'
    elif result.time_below_70 < 10:
        assessment['hypoglycemia'] = 'Moderate Risk (5-10% time below 70)'
    else:
        assessment['hypoglycemia'] = 'High Risk (>10% time below 70)'
    
    return assessment


def compute_hba1c_equivalent(mean_glucose_mg_dl: float) -> float:
    """
    Estimate HbA1c from mean glucose (ADAG formula).
    Returns HbA1c in percentage.
    """
    return (46.7 + mean_glucose_mg_dl) / 28.7


def compute_glucose_excursion(glucose_mg_dl: np.ndarray) -> float:
    """Compute mean absolute glucose excursion."""
    diffs = np.abs(np.diff(glucose_mg_dl))
    return np.mean(diffs)


def compute_esteemed_hba1c(glucose_mg_dl: np.ndarray) -> float:
    """
    Compute esteemed HbA1c from CGM data.
    """
    mean_glucose = np.mean(glucose_mg_dl)
    return compute_hba1c_equivalent(mean_glucose)
