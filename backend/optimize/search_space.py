"""
Search space definitions for optimization.
"""

from dataclasses import dataclass
from typing import Dict, Any, Tuple, List, Optional


@dataclass
class ParameterSpace:
    """Defines a single parameter space."""
    name: str
    param_type: str  # "int", "float", "categorical"
    low: Optional[float] = None
    high: Optional[float] = None
    step: Optional[float] = None
    choices: Optional[List[Any]] = None
    log_scale: bool = False


class SearchSpace:
    """Defines the complete search space for optimization."""
    
    def __init__(self):
        """Initialize search space."""
        self.parameters: Dict[str, ParameterSpace] = {}
    
    def add_parameter(
        self,
        name: str,
        param_type: str,
        low: Optional[float] = None,
        high: Optional[float] = None,
        step: Optional[float] = None,
        choices: Optional[List[Any]] = None,
        log_scale: bool = False
    ) -> None:
        """Add a parameter to the search space."""
        param = ParameterSpace(
            name=name,
            param_type=param_type,
            low=low,
            high=high,
            step=step,
            choices=choices,
            log_scale=log_scale
        )
        self.parameters[name] = param
    
    def to_optuna_dict(self) -> Dict[str, Dict]:
        """Convert to Optuna trial.suggest_* format."""
        optuna_config = {}
        for name, param in self.parameters.items():
            optuna_config[name] = {
                'type': param.param_type,
                'low': param.low,
                'high': param.high,
                'step': param.step,
                'choices': param.choices,
                'log': param.log_scale,
            }
        return optuna_config
    
    def get_parameter(self, name: str) -> ParameterSpace:
        """Get a parameter by name."""
        return self.parameters[name]
    
    def get_all_parameters(self) -> Dict[str, ParameterSpace]:
        """Get all parameters."""
        return self.parameters


def define_insulin_search_space() -> SearchSpace:
    """
    Define search space for insulin system optimization.
    
    Returns:
    SearchSpace object with all relevant parameters.
    """
    space = SearchSpace()
    
    # Insulin formulation parameters
    space.add_parameter('basal_insulin_rate', 'float', low=0.3, high=3.0, step=0.1,
                       help='Units/hour')
    space.add_parameter('bolus_sensitivity', 'float', low=2, high=30, step=0.5,
                       help='Grams per unit')
    space.add_parameter('carb_ratio', 'float', low=5, high=20, step=0.5,
                       help='Grams per unit')
    
    # Nano delivery parameters
    space.add_parameter('nano_size_nm', 'float', low=50, high=500, step=25,
                       help='Nanoparticle diameter')
    space.add_parameter('drug_loading_percent', 'float', low=5, high=50, step=1,
                       help='Drug loading percentage')
    space.add_parameter('release_rate_percent_per_hour', 'float', low=1, high=20, step=0.5,
                       help='Release rate from nanoparticles')
    
    # Control algorithm parameters
    space.add_parameter('proportional_gain_kp', 'float', low=0.01, high=1.0, log_scale=True,
                       help='PID controller proportional gain')
    space.add_parameter('integral_gain_ki', 'float', low=0.001, high=0.5, log_scale=True,
                       help='PID controller integral gain')
    space.add_parameter('derivative_gain_kd', 'float', low=0.0, high=0.1, log_scale=True,
                       help='PID controller derivative gain')
    space.add_parameter('setpoint_mg_dl', 'float', low=80, high=160, step=5,
                       help='Target glucose setpoint')
    
    # Safety thresholds
    space.add_parameter('low_alarm_threshold', 'float', low=50, high=80, step=5,
                       help='Low glucose alarm threshold')
    space.add_parameter('high_alarm_threshold', 'float', low=180, high=250, step=10,
                       help='High glucose alarm threshold')
    space.add_parameter('min_bolus_interval_minutes', 'int', low=60, high=360, step=30,
                       help='Minimum time between boluses')
    
    # Manufacturing parameters
    space.add_parameter('production_yield_percent', 'float', low=20, high=95, step=5,
                       help='Production yield percentage')
    space.add_parameter('batch_size_units', 'int', low=100, high=10000, step=500,
                       help='Batch size in units')
    space.add_parameter('release_mechanism', 'categorical', 
                       choices=['sustained', 'pulsatile', 'triggered', 'enzymatic'],
                       help='Mechanism of drug release')
    
    # Cost parameters
    space.add_parameter('device_cost_usd', 'float', low=100, high=2000, step=100,
                       help='One-time device cost')
    space.add_parameter('injection_cost_usd', 'float', low=10, high=200, step=10,
                       help='Cost per injection')
    
    return space


def define_system_optimization_space() -> SearchSpace:
    """
    Define search space for overall system optimization.
    
    Includes hardware, control, and manufacturing parameters.
    """
    space = SearchSpace()
    
    # Hardware parameters
    space.add_parameter('pump_accuracy_percent', 'float', low=95, high=99.9, step=0.5,
                       help='Infusion accuracy')
    space.add_parameter('sensor_accuracy_percent', 'float', low=85, high=98, step=1,
                       help='CGM accuracy')
    space.add_parameter('wireless_latency_ms', 'float', low=100, high=5000, step=100,
                       help='Communication latency')
    
    # Software parameters
    space.add_parameter('update_interval_minutes', 'float', low=1, high=30, step=1,
                       help='Control algorithm update frequency')
    space.add_parameter('prediction_horizon_hours', 'float', low=0.5, high=6, step=0.5,
                       help='Glucose prediction horizon')
    
    # Regulatory parameters
    space.add_parameter('quality_of_life_score', 'float', low=1, high=10, step=0.5,
                       help='Patient-reported quality of life')
    space.add_parameter('clinical_efficacy_score', 'float', low=1, high=10, step=0.5,
                       help='Clinical efficacy assessment')
    
    return space


def define_variant_optimization_space() -> SearchSpace:
    """
    Define search space for insulin variant optimization.
    
    Parameters for designing new insulin analogs.
    """
    space = SearchSpace()
    
    # Variant properties
    space.add_parameter('onset_minutes', 'float', low=5, high=30, step=1,
                       help='Time to peak action')
    space.add_parameter('peak_time_hours', 'float', low=0.5, high=3, step=0.1,
                       help='Peak effect time')
    space.add_parameter('duration_hours', 'float', low=2, high=8, step=0.25,
                       help='Duration of action')
    space.add_parameter('potency_percent_of_wild_type', 'float', low=50, high=150, step=5,
                       help='Potency relative to natural insulin')
    
    # Amino acid changes
    space.add_parameter('number_of_aa_changes', 'int', low=0, high=10, step=1,
                       help='Number of amino acid modifications')
    space.add_parameter('change_position', 'categorical',
                       choices=['A_chain', 'B_chain', 'C_peptide', 'multiple'],
                       help='Location of modifications')
    
    return space
