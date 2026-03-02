"""
Scenario definitions for physiology simulations.
"""

from dataclasses import dataclass
from typing import Optional, Callable
import numpy as np


@dataclass
class Scenario:
    """Base scenario class."""
    name: str
    description: str
    
    def apply_effect(self, glucose: np.ndarray, insulin: np.ndarray, time_minutes: np.ndarray) -> tuple:
        """Apply scenario effects to glucose and insulin dynamics."""
        raise NotImplementedError


@dataclass
class StressScenario(Scenario):
    """Stress-induced hyperglycemia scenario."""
    name: str = "Acute Stress"
    description: str = "Simulates stress-induced hyperglycemia"
    cortisol_increase: float = 2.0  # 2x normal
    duration_minutes: float = 180
    glucose_rise_mg_dl: float = 50
    
    def apply_effect(self, glucose: np.ndarray, insulin: np.ndarray, time_minutes: np.ndarray) -> tuple:
        """Apply stress effects to glucose."""
        glucose_modified = glucose.copy()
        
        # Find stress window (first duration minutes)
        stress_mask = time_minutes <= self.duration_minutes
        
        # Apply gradual glucose increase then recovery
        for i, is_stressed in enumerate(stress_mask):
            if is_stressed:
                phase = time_minutes[i] / self.duration_minutes
                # Smooth rise and fall
                effect = self.glucose_rise_mg_dl * np.sin(np.pi * phase)
                glucose_modified[i] += effect
        
        return glucose_modified, insulin


@dataclass
class ExerciseScenario(Scenario):
    """Exercise-induced glucose changes."""
    name: str = "Exercise"
    description: str = "Simulates exercise effects on glucose"
    start_time_minutes: float = 120
    duration_minutes: float = 60
    intensity: float = 0.7  # 0-1 scale
    
    def apply_effect(self, glucose: np.ndarray, insulin: np.ndarray, time_minutes: np.ndarray) -> tuple:
        """Apply exercise effects."""
        glucose_modified = glucose.copy()
        insulin_modified = insulin.copy()
        
        ex_start = self.start_time_minutes
        ex_end = ex_start + self.duration_minutes
        
        exercise_mask = (time_minutes >= ex_start) & (time_minutes <= ex_end)
        
        # Exercise increases insulin sensitivity and glucose uptake
        sensitivity_boost = 1.5 * self.intensity
        glucose_modified[exercise_mask] -= glucose[exercise_mask] * (0.2 * self.intensity)
        insulin_modified[exercise_mask] *= sensitivity_boost
        
        # Post-exercise effects for recovery period
        recovery_mask = (time_minutes > ex_end) & (time_minutes <= ex_end + 120)
        recovery_phase = (time_minutes[recovery_mask] - ex_end) / 120
        recovery_effect = 0.1 * self.intensity * np.exp(-recovery_phase)
        glucose_modified[recovery_mask] -= recovery_effect * glucose[recovery_mask]
        
        return glucose_modified, insulin_modified


@dataclass
class ColdScenario(Scenario):
    """Cold exposure scenario."""
    name: str = "Cold Exposure"
    description: str = "Simulates cold-induced metabolic changes"
    start_time_minutes: float = 0
    duration_minutes: float = 120
    temperature_celsius: float = 4
    
    def apply_effect(self, glucose: np.ndarray, insulin: np.ndarray, time_minutes: np.ndarray) -> tuple:
        """Apply cold exposure effects."""
        glucose_modified = glucose.copy()
        insulin_modified = insulin.copy()
        
        cold_start = self.start_time_minutes
        cold_end = cold_start + self.duration_minutes
        
        cold_mask = (time_minutes >= cold_start) & (time_minutes <= cold_end)
        
        # Cold increases metabolic rate and glucose demand
        metabolic_increase = 1.3  # 30% increase
        glucose_modified[cold_mask] -= glucose[cold_mask] * 0.15
        insulin_modified[cold_mask] *= 0.8  # Reduced insulin sensitivity in cold
        
        return glucose_modified, insulin_modified


@dataclass
class HyperglycemicScenario(Scenario):
    """Sustained hyperglycemia scenario."""
    name: str = "Hyperglycemia"
    description: str = "Simulates hyperglycemic conditions"
    magnitude_mg_dl: float = 80
    duration_minutes: float = 240
    
    def apply_effect(self, glucose: np.ndarray, insulin: np.ndarray, time_minutes: np.ndarray) -> tuple:
        """Apply hyperglycemia effect."""
        glucose_modified = glucose.copy()
        glucose_modified[:int(self.duration_minutes / (time_minutes[1] - time_minutes[0]))] += self.magnitude_mg_dl
        return glucose_modified, insulin


@dataclass
class HypoglycemiaRecoveryScenario(Scenario):
    """Hypoglycemia and recovery scenario."""
    name: str = "Hypoglycemia"
    description: str = "Simulates hypoglycemic episode and recovery"
    time_of_event: float = 180
    nadir_mg_dl: float = 40
    recovery_carbs_grams: float = 15
    
    def apply_effect(self, glucose: np.ndarray, insulin: np.ndarray, time_minutes: np.ndarray) -> tuple:
        """Apply hypoglycemia effects."""
        glucose_modified = glucose.copy()
        
        event_idx = np.argmin(np.abs(time_minutes - self.time_of_event))
        
        # Drop to nadir
        if event_idx < len(glucose_modified):
            window = int(20 / (time_minutes[1] - time_minutes[0]))  # 20 minute drop
            for i in range(max(0, event_idx - window), event_idx):
                phase = (i - (event_idx - window)) / window
                glucose_modified[i] -= (glucose[i] - self.nadir_mg_dl) * phase
            
            # Recovery with carbs
            glucose_modified[event_idx] = self.nadir_mg_dl
            recovery_window = int(60 / (time_minutes[1] - time_minutes[0]))
            carb_equivalent = self.recovery_carbs_grams * 4  # 4 mg/dL per gram
            for i in range(event_idx, min(event_idx + recovery_window, len(glucose_modified))):
                phase = (i - event_idx) / recovery_window
                glucose_modified[i] += carb_equivalent * (1 - np.exp(-phase))
        
        return glucose_modified, insulin


def create_scenario(scenario_type: str, **kwargs) -> Scenario:
    """Factory function to create scenarios."""
    scenarios = {
        'stress': StressScenario,
        'exercise': ExerciseScenario,
        'cold': ColdScenario,
        'hyperglycemia': HyperglycemicScenario,
        'hypoglycemia': HypoglycemiaRecoveryScenario,
    }
    
    if scenario_type not in scenarios:
        raise ValueError(f"Unknown scenario type: {scenario_type}")
    
    return scenarios[scenario_type](**kwargs)
