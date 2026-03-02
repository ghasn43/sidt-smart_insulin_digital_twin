"""
Core module for Smart Insulin Digital Twin.
Provides fundamental data structures and utilities.
"""

from .models import Patient, InsulinDose, SimulationResult, SystemConfig
from .io import DataManager, save_simulation, load_simulation
from .metrics import calculate_metrics, compute_glucose_variability, assess_control_quality
from .plotting import plot_glucose_profile, plot_insulin_delivery, plot_comparison

__all__ = [
    'Patient',
    'InsulinDose',
    'SimulationResult',
    'SystemConfig',
    'DataManager',
    'save_simulation',
    'load_simulation',
    'calculate_metrics',
    'compute_glucose_variability',
    'assess_control_quality',
    'plot_glucose_profile',
    'plot_insulin_delivery',
    'plot_comparison',
]
