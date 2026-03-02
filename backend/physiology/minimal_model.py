"""
Mathematical functions for glucose-insulin physiology.
"""

import numpy as np
from typing import Tuple


def glucose_rate_of_appearance(
    time_minutes: np.ndarray,
    carb_grams: float,
    meal_type: str = "mixed"
) -> np.ndarray:
    """
    Calculate glucose rate of appearance (Ra) from a meal.
    
    meal_type: "fast" (glucose), "mixed" (balanced), "slow" (lipid-rich)
    """
    if meal_type == "fast":
        peak_time = 20
        duration = 120
        max_ra = carb_grams * 5  # mg/min
    elif meal_type == "slow":
        peak_time = 60
        duration = 300
        max_ra = carb_grams * 3
    else:  # mixed
        peak_time = 40
        duration = 200
        max_ra = carb_grams * 4
    
    # Gaussian absorption
    sigma = peak_time / 2
    ra = max_ra * np.exp(-((time_minutes - peak_time) ** 2) / (2 * sigma ** 2))
    
    return np.clip(ra, 0, None)


def insulin_secretion_rate(
    glucose_mg_dl: float,
    basal_insulin: float = 1.0,
    sensitivity: float = 0.005
) -> float:
    """
    Calculate insulin secretion rate based on glucose.
    Represents beta cell function.
    """
    glucose_threshold = 100  # mg/dL
    
    if glucose_mg_dl < glucose_threshold:
        return basal_insulin * 0.5
    
    # Proportional increase above threshold
    excess_glucose = glucose_mg_dl - glucose_threshold
    secretion = basal_insulin + sensitivity * excess_glucose
    
    return max(basal_insulin * 0.5, secretion)


def hepatic_glucose_production(
    glucose_mg_dl: float,
    insulin_mu_l: float,
    basal_hgp: float = 2.0
) -> float:
    """
    Calculate hepatic glucose production (HGP).
    Suppressed by insulin, stimulated by low glucose.
    """
    # Basal HGP ~2 mg/kg/min
    insulin_suppression_factor = 0.003
    glucose_stimulation = max(0, (100 - glucose_mg_dl) / 100)
    
    hgp = basal_hgp * (1 - insulin_suppression_factor * insulin_mu_l) + glucose_stimulation
    
    return max(0.5, hgp)


def glucose_utilization_rate(
    glucose_mg_dl: float,
    insulin_mu_l: float,
    basal_utilization: float = 2.0
) -> float:
    """
    Calculate glucose utilization rate (Rd).
    Increases with glucose and insulin.
    """
    insulin_effect = 0.001 * insulin_mu_l
    glucose_effect = (glucose_mg_dl - 100) / 100
    
    rd = basal_utilization * (1 + insulin_effect + glucose_effect)
    
    return max(0.1, rd)


def insulin_clearance_rate(
    insulin_mu_l: float,
    clearance_factor: float = 0.1
) -> float:
    """
    Calculate insulin clearance (hepatic and renal).
    Proportional to insulin concentration.
    """
    return insulin_mu_l * clearance_factor


def renal_glucose_excretion(
    glucose_mg_dl: float,
    threshold_mg_dl: float = 180,
    max_excretion: float = 10.0
) -> float:
    """
    Calculate glucose excretion in urine.
    Occurs when glucose exceeds renal threshold.
    """
    if glucose_mg_dl < threshold_mg_dl:
        return 0.0
    
    excess = glucose_mg_dl - threshold_mg_dl
    excretion = min(max_excretion, excess * 0.05)
    
    return excretion


def glucagon_secretion(
    glucose_mg_dl: float,
    basal_glucagon: float = 30.0
) -> float:
    """
    Calculate glucagon secretion based on glucose.
    Counter-regulated hormone.
    """
    if glucose_mg_dl > 100:
        return basal_glucagon
    
    # Increases as glucose drops below 100
    return basal_glucagon + (100 - glucose_mg_dl) * 2


def compute_tir_metrics(glucose_mg_dl: np.ndarray) -> dict:
    """
    Compute time-in-range and related metrics.
    """
    total_points = len(glucose_mg_dl)
    
    metrics = {
        'tir_70_180': np.sum((glucose_mg_dl >= 70) & (glucose_mg_dl <= 180)) / total_points * 100,
        'tir_80_140': np.sum((glucose_mg_dl >= 80) & (glucose_mg_dl <= 140)) / total_points * 100,
        'time_below_70': np.sum(glucose_mg_dl < 70) / total_points * 100,
        'time_below_54': np.sum(glucose_mg_dl < 54) / total_points * 100,
        'time_above_180': np.sum(glucose_mg_dl > 180) / total_points * 100,
        'time_above_250': np.sum(glucose_mg_dl > 250) / total_points * 100,
    }
    
    return metrics
