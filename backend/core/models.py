"""
Core data models for Smart Insulin Digital Twin.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta


@dataclass
class Patient:
    """Represents a patient profile for simulation."""
    patient_id: str
    age: int
    weight_kg: float
    height_cm: float
    bmi: float = field(init=False)
    insulin_sensitivity: float  # mg/dL per unit insulin
    basal_insulin_rate: float  # units/hour
    carb_ratio: float  # grams per unit insulin
    dawn_phenomenon: bool = False
    dawn_magnitude: float = 0.0  # mg/dL increase
    
    def __post_init__(self):
        self.bmi = (self.weight_kg / ((self.height_cm / 100) ** 2))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'patient_id': self.patient_id,
            'age': self.age,
            'weight_kg': self.weight_kg,
            'height_cm': self.height_cm,
            'bmi': self.bmi,
            'insulin_sensitivity': self.insulin_sensitivity,
            'basal_insulin_rate': self.basal_insulin_rate,
            'carb_ratio': self.carb_ratio,
            'dawn_phenomenon': self.dawn_phenomenon,
            'dawn_magnitude': self.dawn_magnitude,
        }


@dataclass
class InsulinDose:
    """Represents an insulin administration event."""
    timestamp: datetime
    magnitude: float  # units
    bolus: bool = True  # True for bolus, False for basal
    carb_amount: float = 0.0  # grams
    source: str = "manual"  # manual, basal, pump, algorithm


@dataclass
class SystemConfig:
    """Configuration for nano insulin delivery system."""
    nano_size_nm: float  # diameter in nanometers
    drug_loading: float  # percentage
    release_rate: float  # units/minute per nano particle
    particle_count: float  # number of particles
    target_absorption: float  # percentage of drug absorbed
    max_release_rate: float  # safety limit


@dataclass
class SimulationResult:
    """Results from a simulation."""
    patient: Patient
    timestamps: np.ndarray  # datetime objects
    glucose_mg_dl: np.ndarray  # continuous glucose monitoring values
    insulin_units: np.ndarray  # insulin on board
    carb_intake: np.ndarray  # carbohydrate intake
    doses: List[InsulinDose] = field(default_factory=list)
    
    # Metrics
    mean_glucose: float = 0.0
    std_glucose: float = 0.0
    time_in_range_70_180: float = 0.0  # percentage
    time_above_180: float = 0.0
    time_below_70: float = 0.0
    hyperglycemic_index: float = 0.0
    hypoglycemic_index: float = 0.0
    glucose_variability: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for saving."""
        return {
            'patient': self.patient.to_dict(),
            'mean_glucose': self.mean_glucose,
            'std_glucose': self.std_glucose,
            'time_in_range': self.time_in_range_70_180,
            'time_above_180': self.time_above_180,
            'time_below_70': self.time_below_70,
            'hyperglycemic_index': self.hyperglycemic_index,
            'hypoglycemic_index': self.hypoglycemic_index,
            'glucose_variability': self.glucose_variability,
        }


@dataclass
class ManufacturingSpec:
    """Specifications for insulin variant manufacturing."""
    protein_sequence: str
    target_expression_level: float  # mg/L
    purification_yield: float  # percentage
    endotoxin_level: float  # EU/mL
    protein_purity: float  # percentage
    vial_concentration: float  # units/mL
    shelf_life_months: int


@dataclass
class NanoReleaseProfile:
    """Release profile for nanoparticles."""
    time_hours: List[float]
    cumulative_release_percent: List[float]
    burst_release: float  # percentage released in first hour
    sustained_duration: float  # hours
    release_mechanism: str  # "diffusion", "degradation", "enzymatic"
