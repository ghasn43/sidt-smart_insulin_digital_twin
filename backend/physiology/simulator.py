"""
Physiological models for Smart Insulin Digital Twin.
Simulates glucose and insulin dynamics using minimal model.
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class MinimalModelParams:
    """Parameters for minimal model of glucose-insulin dynamics."""
    # Glucose effectiveness
    Sg: float = 0.03  # min^-1
    
    # Insulin sensitivity
    Si: float = 0.0001  # mL/(mU*min)
    
    # Insulin secretion
    p2: float = 0.025  # min^-1
    
    # Glucose absorption
    Vg: float = 1.4  # dL (glucose distribution volume)
    
    # Insulin distribution parameters
    p3: float = 0.0003  # min^-1 (delay factor)
    Vi: float = 1.2  # L (insulin distribution volume)
    
    # Renal glucose clearance threshold
    Gb: float = 91.0  # mg/dL (basal glucose)
    
    # Initial conditions
    Ib: float = 15.0  # mU/L (basal insulin)


class MinimalModel:
    """Minimal glucose-insulin model (Bergman model)."""
    
    def __init__(self, params: Optional[MinimalModelParams] = None):
        self.params = params or MinimalModelParams()
    
    def derivatives(self, t: float, state: np.ndarray, glucose_input: float, insulin_input: float) -> np.ndarray:
        """
        Compute state derivatives.
        
        State: [G, I, X]
        G: Plasma glucose (mg/dL)
        I: Plasma insulin (mU/L)
        X: Insulin effect on glucose disposal
        
        Inputs:
        glucose_input: Glucose appearance rate (mg/min)
        insulin_input: Insulin secretion or injection (mU/min)
        """
        G, I, X = state
        p = self.params
        
        # Glucose equation
        dG = -p.Sg * G - X * G + glucose_input / p.Vg
        
        # Insulin remote effect equation
        dX = p.p3 * (I - p.Ib) - p.p2 * X
        
        # Insulin equation (with insulin input)
        dI = -p.p2 * I + insulin_input
        
        return np.array([dG, dI, dX])
    
    def simulate(
        self,
        initial_glucose: float,
        initial_insulin: float,
        time_minutes: int,
        dt: float = 1.0,
        glucose_inputs: Optional[np.ndarray] = None,
        insulin_inputs: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Simulate glucose-insulin dynamics.
        
        Returns:
        time, glucose, insulin, remote_effect
        """
        n_steps = int(time_minutes / dt)
        t = np.linspace(0, time_minutes, n_steps)
        
        glucose = np.zeros(n_steps)
        insulin = np.zeros(n_steps)
        remote_effect = np.zeros(n_steps)
        
        state = np.array([initial_glucose, initial_insulin, 0.0])
        glucose[0], insulin[0], remote_effect[0] = state
        
        if glucose_inputs is None:
            glucose_inputs = np.zeros(n_steps)
        if insulin_inputs is None:
            insulin_inputs = np.zeros(n_steps)
        
        # Forward Euler integration
        for i in range(n_steps - 1):
            # Interpolate inputs
            g_input = glucose_inputs[i] if i < len(glucose_inputs) else 0
            i_input = insulin_inputs[i] if i < len(insulin_inputs) else 0
            
            derivatives = self.derivatives(t[i], state, g_input, i_input)
            state = state + derivatives * dt
            
            # Bounds checking
            state[0] = max(20.0, state[0])  # Glucose >= 20 mg/dL
            state[1] = max(0.0, state[1])   # Insulin >= 0
            
            glucose[i + 1], insulin[i + 1], remote_effect[i + 1] = state
        
        return t, glucose, insulin, remote_effect


def simulate_carb_absorption(
    carb_grams: float,
    meal_time: float,
    peak_time: float = 30.0,
    duration: float = 180.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simulate carbohydrate absorption (appearance in bloodstream).
    Uses a Gaussian-like absorption profile.
    
    Returns:
    time (minutes), glucose appearance rate (mg/min)
    """
    t = np.arange(0, duration, 1.0)
    
    # Glucose equivalence: 1 gram carbs ≈ 4 mg/dL in 70 kg person with 2 dL distribution
    # Appearance rate: ~0.5 mg/kg/min per gram carbs
    max_appearance = carb_grams * 4.0  # peak mg/dL/min
    
    # Gaussian absorption
    sigma = peak_time / 2
    appearance_rate = max_appearance * np.exp(-((t - peak_time) ** 2) / (2 * sigma ** 2))
    
    return t, appearance_rate


def simulate_insulin_injection(
    insulin_units: float,
    injection_time: float,
    insulin_type: str = "rapid"
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simulate insulin absorption from subcutaneous injection.
    
    insulin_type: "rapid", "regular", or "long"
    
    Returns:
    time (minutes), insulin appearance rate (mU/min)
    """
    # Peak and duration times for different insulin types
    if insulin_type == "rapid":
        peak_time = 45  # minutes
        duration = 240  # minutes
    elif insulin_type == "regular":
        peak_time = 120
        duration = 480
    else:  # long-acting
        peak_time = 180
        duration = 1440
    
    t = np.arange(0, duration, 1.0)
    
    # Peak rate
    max_rate = insulin_units * 10  # mU/min (rough estimate)
    
    # Bell-shaped absorption curve
    sigma = peak_time / 2
    appearance_rate = max_rate * np.exp(-((t - peak_time) ** 2) / (2 * sigma ** 2))
    
    return t, appearance_rate


class PatientSimulator:
    """Simulates a patient's glucose dynamics over time."""
    
    def __init__(self, patient):
        """Initialize simulator with patient profile."""
        self.patient = patient
        self.model = MinimalModel()
        
        # Individualize parameters based on patient
        self.model.params.Sg = 0.02 + (0.01 * (25 - patient.bmi) / 5)  # Higher BMI = lower effectiveness
        self.model.params.Si = 0.0001 * (1.0 / patient.insulin_sensitivity) * 40  # Normalize to 40 mg/dL per unit
    
    def simulate_day(
        self,
        start_datetime: datetime,
        initial_glucose: float = 120,
        carb_schedule: Optional[List[Tuple[float, float]]] = None,  # (time in hours, grams)
        insulin_schedule: Optional[List[Tuple[float, float]]] = None,  # (time in hours, units)
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Simulate a full day of glucose dynamics.
        
        Returns:
        timestamps, glucose_mg_dl, insulin_units, carb_grams
        """
        simulation_minutes = 24 * 60
        dt = 5  # 5-minute intervals (CGM standard)
        n_steps = int(simulation_minutes / dt)
        
        time_array = np.arange(n_steps) * dt
        glucose_inputs = np.zeros(n_steps)
        insulin_inputs = np.zeros(n_steps)
        carb_inputs = np.zeros(n_steps)
        
        # Add meals
        if carb_schedule:
            for meal_time_hours, carb_grams in carb_schedule:
                meal_time_min = meal_time_hours * 60
                t_carb, absorption = simulate_carb_absorption(carb_grams, 0, peak_time=30)
                
                # Add to glucose inputs
                for i, rate in enumerate(absorption):
                    idx = int((meal_time_min + t_carb[i]) / dt)
                    if idx < n_steps:
                        glucose_inputs[idx] += rate
                        carb_inputs[idx] = carb_grams if i == 0 else 0
        
        # Add insulin injections
        if insulin_schedule:
            for insulin_time_hours, insulin_units in insulin_schedule:
                inj_time_min = insulin_time_hours * 60
                t_insulin, absorption = simulate_insulin_injection(insulin_units, 0, "rapid")
                
                for i, rate in enumerate(absorption):
                    idx = int((inj_time_min + t_insulin[i]) / dt)
                    if idx < n_steps:
                        insulin_inputs[idx] += rate
        
        # Add basal insulin
        basal_rate = self.patient.basal_insulin_rate / 60  # Convert to per-minute
        insulin_inputs += basal_rate * dt
        
        # Add dawn phenomenon if enabled
        if self.patient.dawn_phenomenon:
            dawn_start = 5 * 60  # 5 AM
            dawn_peak = 7 * 60   # 7 AM
            dawn_end = 9 * 60    # 9 AM
            for i, t in enumerate(time_array):
                if dawn_start <= t <= dawn_end:
                    phase = (t - dawn_start) / (dawn_peak - dawn_start)
                    factor = np.sin(np.pi * phase) if phase < 1 else (2 - phase)
                    glucose_inputs[i] += self.patient.dawn_magnitude * factor / 60
        
        # Run simulation
        t, glucose, insulin, _ = self.model.simulate(
            initial_glucose,
            self.patient.basal_insulin_rate,
            simulation_minutes,
            dt=dt,
            glucose_inputs=glucose_inputs,
            insulin_inputs=insulin_inputs
        )
        
        # Convert time to datetime
        timestamps = np.array([start_datetime + timedelta(minutes=float(t_val)) for t_val in t])
        
        return timestamps, glucose, insulin, carb_inputs
