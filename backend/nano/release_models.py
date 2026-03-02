"""
Nano module for nanoparticle-based insulin delivery.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import numpy as np
from datetime import datetime, timedelta


@dataclass
class NanoParticle:
    """Represents a single nanoparticle."""
    particle_id: str
    diameter_nm: float
    drug_loading_percent: float
    coating_type: str  # "PEG", "lipid", "polymer"
    insulin_units: float
    creation_time: datetime = field(default_factory=datetime.now)
    release_profile: Optional[List[Tuple[float, float]]] = None  # (time_hours, percent_released)


@dataclass
class NanoFormulation:
    """Complete nanoparticle formulation."""
    formulation_id: str
    particle_count: float
    mean_diameter_nm: float
    std_diameter_nm: float
    total_insulin_units: float
    drug_loading_percent: float
    coating_material: str
    batch_date: datetime = field(default_factory=datetime.now)
    stability_months: float = 24  # Shelf life
    release_mechanism: str = "sustained"  # sustained, triggered, pulsatile


class NanoReleaseModeler:
    """Models insulin release from nanoparticles."""
    
    def __init__(self):
        """Initialize release modeler."""
        self.mechanisms = {
            'diffusion': self._diffusion_model,
            'degradation': self._degradation_model,
            'enzymatic': self._enzymatic_model,
            'osmotic': self._osmotic_model,
        }
    
    def _diffusion_model(
        self,
        time_hours: np.ndarray,
        dose_units: float,
        lag_time: float = 0.5,
        release_rate_percent_per_hour: float = 5
    ) -> np.ndarray:
        """
        Simple diffusion-based release model.
        Zero-order kinetics for sustained release.
        """
        release = np.zeros_like(time_hours, dtype=float)
        
        # Lag period
        active_time = np.maximum(0, time_hours - lag_time)
        
        # Zero-order release: constant rate
        release = np.minimum(100, release_rate_percent_per_hour * active_time)
        
        return dose_units * release / 100
    
    def _degradation_model(
        self,
        time_hours: np.ndarray,
        dose_units: float,
        degradation_rate: float = 0.01,  # per hour
        burst_release: float = 20  # initial percentage
    ) -> np.ndarray:
        """
        Degradation-based release model.
        Polymer degradation causes drug release.
        """
        release = np.zeros_like(time_hours, dtype=float)
        
        # Burst release at t=0
        release_percent = np.ones_like(time_hours) * burst_release
        
        # Exponential degradation
        degradation_rate_corrected = degradation_rate / 100  # Per hour
        release_percent += (100 - burst_release) * (1 - np.exp(-degradation_rate_corrected * time_hours))
        
        release_percent = np.minimum(100, release_percent)
        
        return dose_units * release_percent / 100
    
    def _enzymatic_model(
        self,
        time_hours: np.ndarray,
        dose_units: float,
        enzyme_concentration: float = 1.0,
        substrate_affinity: float = 0.5
    ) -> np.ndarray:
        """
        Enzyme-triggered release model.
        Release triggered by local enzymatic conditions.
        """
        release = np.zeros_like(time_hours, dtype=float)
        
        # Michaelis-Menten-like kinetics
        vmax = 15  # max release percent/hour
        km = 2.0  # hours for half-max
        
        release_rate = vmax * time_hours / (km + time_hours)
        release_percent = np.cumsum(release_rate) * (time_hours[1] - time_hours[0] if len(time_hours) > 1 else 1)
        release_percent = np.minimum(100, release_percent)
        
        return dose_units * release_percent / 100
    
    def _osmotic_model(
        self,
        time_hours: np.ndarray,
        dose_units: float,
        osmotic_pressure_difference: float = 10,  # atm
        membrane_permeability: float = 0.5  # um/minute
    ) -> np.ndarray:
        """
        Osmosis-driven release model.
        Water influx drives drug release through pores.
        """
        release = np.zeros_like(time_hours, dtype=float)
        
        # Osmotic flow rate proportional to pressure difference
        flow_rate = osmotic_pressure_difference * membrane_permeability / 10
        
        # Pulsatile release
        release_percent = np.minimum(100, flow_rate * time_hours)
        
        return dose_units * release_percent / 100
    
    def simulate_release_profile(
        self,
        dose_units: float,
        days: float = 7,
        mechanism: str = "sustained",
        dt_hours: float = 0.5,
        **mechanism_params
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate full release profile.
        
        Returns:
        time_hours, insulin_release (units)
        """
        time_hours = np.arange(0, days * 24, dt_hours)
        
        if mechanism not in self.mechanisms:
            raise ValueError(f"Unknown mechanism: {mechanism}")
        
        release_func = self.mechanisms[mechanism]
        release = release_func(time_hours, dose_units, **mechanism_params)
        
        return time_hours, release
    
    def compute_metrics(
        self,
        time_hours: np.ndarray,
        insulin_release: np.ndarray,
        target_release: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """Compute release profile metrics."""
        # Cumulative release
        cumulative = np.cumsum(insulin_release)
        total_released = cumulative[-1]
        
        metrics = {
            'total_released_units': total_released,
            'burst_release_percent': (insulin_release[0] / total_released * 100) if total_released > 0 else 0,
            'median_release_time_hours': self._find_median_release_time(time_hours, cumulative, total_released),
            'peak_release_rate_units_per_hour': np.max(insulin_release) if len(insulin_release) > 0 else 0,
        }
        
        # Deviation from target if provided
        if target_release is not None:
            deviation = np.mean(np.abs(cumulative - target_release))
            metrics['target_deviation'] = deviation
        
        return metrics
    
    def _find_median_release_time(self, time_hours: np.ndarray, cumulative: np.ndarray, total_released: float) -> float:
        """Find time to reach 50% release."""
        threshold = total_released / 2
        idx = np.argmin(np.abs(cumulative - threshold))
        return time_hours[idx]


class ParticleDispersal:
    """Models spatial dispersal and targeting of nanoparticles."""
    
    def __init__(self):
        """Initialize dispersal model."""
        pass
    
    def estimate_absorption_rate(
        self,
        particle_diameter_nm: float,
        administration_route: str = "subcutaneous"
    ) -> float:
        """Estimate absorption rate based on particle size and route."""
        # Smaller particles absorb faster
        if administration_route == "subcutaneous":
            # Lymphatic transport limited
            base_rate = 0.1
            size_factor = max(0.1, 1000 / particle_diameter_nm)
        elif administration_route == "intradermal":
            # Faster
            base_rate = 0.3
            size_factor = max(0.2, 500 / particle_diameter_nm)
        elif administration_route == "intravenous":
            # Immediate
            return 1.0
        else:
            base_rate = 0.1
            size_factor = 1.0
        
        absorption_rate = min(1.0, base_rate * size_factor)
        return absorption_rate
    
    def estimate_targeting(
        self,
        particle_diameter_nm: float,
        target_tissue: str = "islet_cells"
    ) -> Dict[str, float]:
        """Estimate particle distribution to different tissues."""
        distribution = {
            'liver': 0.4,
            'spleen': 0.2,
            'kidney': 0.15,
            'pancreas': 0.1,
            'other': 0.15,
        }
        
        # Smaller particles better target pancreas
        if target_tissue == "islet_cells":
            if particle_diameter_nm < 200:
                distribution['pancreas'] = 0.25
                distribution['liver'] = 0.30
                distribution['other'] = 0.20
            elif particle_diameter_nm < 500:
                distribution['pancreas'] = 0.15
                distribution['liver'] = 0.50
        
        return distribution
