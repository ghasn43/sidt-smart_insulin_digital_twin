"""
Optuna-based optimization runner for Smart Insulin Digital Twin.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, Any, List, Optional, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)

try:
    import optuna
except ImportError:
    # Optuna not installed, provide mock
    optuna = None


@dataclass
class OptimizationTrial:
    """Represents a single optimization trial."""
    trial_id: int
    parameters: Dict[str, Any]
    objective_scores: Dict[str, float]
    combined_score: float
    timestamp: str = field(default_factory=lambda: __import__('datetime').datetime.now().isoformat())
    status: str = "completed"


class OptimizationRunner:
    """Runs optimization using Optuna or local search."""
    
    def __init__(
        self,
        objective_func: Callable,
        search_space: Dict[str, Dict],
        n_trials: int = 100,
        sampler: str = "tpe",  # "tpe" or "random"
        use_optuna: bool = True
    ):
        """
        Initialize optimization runner.
        
        Args:
            objective_func: Function to optimize (should return float)
            search_space: Dict defining parameter bounds
            n_trials: Number of trials to run
            sampler: Optuna sampler type
            use_optuna: Whether to use Optuna (if available)
        """
        self.objective_func = objective_func
        self.search_space = search_space
        self.n_trials = n_trials
        self.sampler = sampler
        self.use_optuna = use_optuna and optuna is not None
        
        self.trials: List[OptimizationTrial] = []
        self.best_trial: Optional[OptimizationTrial] = None
        self.study = None
    
    def run(self) -> Tuple[OptimizationTrial, List[OptimizationTrial]]:
        """
        Run optimization.
        
        Returns:
            best_trial: The trial with the best objective value
            all_trials: List of all completed trials
        """
        if self.use_optuna and optuna is not None:
            return self._run_optuna()
        else:
            return self._run_local_search()
    
    def _run_optuna(self) -> Tuple[OptimizationTrial, List[OptimizationTrial]]:
        """Run optimization using Optuna."""
        try:
            # Create sampler
            if self.sampler == "tpe":
                sampler = optuna.samplers.TPESampler(seed=42)
            else:
                sampler = optuna.samplers.RandomSampler(seed=42)
            
            # Create study
            self.study = optuna.create_study(sampler=sampler, direction="maximize")
            
            # Define objective wrapper for Optuna
            def optuna_objective(trial):
                params = self._suggest_from_optuna_trial(trial)
                score = self.objective_func(params)
                return score
            
            # Optimize
            self.study.optimize(optuna_objective, n_trials=self.n_trials, show_progress_bar=True)
            
            # Extract trials
            self.trials = []
            for trial in self.study.trials:
                opt_trial = OptimizationTrial(
                    trial_id=trial.number,
                    parameters=trial.params,
                    objective_scores={'score': trial.value},
                    combined_score=trial.value or 0.0
                )
                self.trials.append(opt_trial)
            
            # Get best trial
            best_optuna_trial = self.study.best_trial
            self.best_trial = OptimizationTrial(
                trial_id=best_optuna_trial.number,
                parameters=best_optuna_trial.params,
                objective_scores={'score': best_optuna_trial.value},
                combined_score=best_optuna_trial.value or 0.0
            )
            
            logger.info(f"Optuna optimization complete. Best score: {self.best_trial.combined_score}")
            return self.best_trial, self.trials
        
        except Exception as e:
            logger.exception(f"Optuna optimization failed: {e}")
            # Fall back to local search
            return self._run_local_search()
    
    def _run_local_search(self) -> Tuple[OptimizationTrial, List[OptimizationTrial]]:
        """Run local random search without Optuna."""
        self.trials = []
        best_score = float('-inf')
        
        for trial_id in range(self.n_trials):
            # Sample random parameters
            params = self._random_sample()
            
            # Evaluate
            try:
                score = self.objective_func(params)
            except Exception as e:
                logger.warning(f"Trial {trial_id} failed: {e}")
                score = float('-inf')
            
            # Create trial record
            trial = OptimizationTrial(
                trial_id=trial_id,
                parameters=params,
                objective_scores={'score': score},
                combined_score=score
            )
            self.trials.append(trial)
            
            # Track best
            if score > best_score:
                best_score = score
                self.best_trial = trial
            
            if (trial_id + 1) % 10 == 0:
                logger.info(f"Trial {trial_id + 1}/{self.n_trials} - Best score: {best_score}")
        
        logger.info(f"Local search complete. Best score: {best_score}")
        return self.best_trial, self.trials
    
    def _suggest_from_optuna_trial(self, trial) -> Dict[str, Any]:
        """Suggest parameters from Optuna trial."""
        params = {}
        for param_name, param_config in self.search_space.items():
            param_type = param_config.get('type', 'float')
            
            if param_type == 'int':
                params[param_name] = trial.suggest_int(
                    param_name,
                    param_config['low'],
                    param_config['high'],
                    step=param_config.get('step', 1)
                )
            elif param_type == 'float':
                params[param_name] = trial.suggest_float(
                    param_name,
                    param_config['low'],
                    param_config['high'],
                    step=param_config.get('step'),
                    log=param_config.get('log', False)
                )
            elif param_type == 'categorical':
                params[param_name] = trial.suggest_categorical(
                    param_name,
                    param_config['choices']
                )
        
        return params
    
    def _random_sample(self) -> Dict[str, Any]:
        """Random sample from search space."""
        params = {}
        
        for param_name, param_config in self.search_space.items():
            param_type = param_config.get('type', 'float')
            
            if param_type == 'int':
                low, high = int(param_config['low']), int(param_config['high'])
                params[param_name] = np.random.randint(low, high + 1)
            elif param_type == 'float':
                low, high = param_config['low'], param_config['high']
                if param_config.get('log', False):
                    params[param_name] = np.exp(np.random.uniform(np.log(low), np.log(high)))
                else:
                    params[param_name] = np.random.uniform(low, high)
            elif param_type == 'categorical':
                params[param_name] = np.random.choice(param_config['choices'])
        
        return params
    
    def get_best_parameters(self) -> Dict[str, Any]:
        """Get the best parameters found."""
        if self.best_trial:
            return self.best_trial.parameters
        return {}
    
    def get_best_score(self) -> float:
        """Get the best score achieved."""
        if self.best_trial:
            return self.best_trial.combined_score
        return float('-inf')
    
    def get_trial_history(self) -> List[Dict]:
        """Get history of all trials."""
        return [
            {
                'trial_id': t.trial_id,
                'parameters': t.parameters,
                'score': t.combined_score,
                'timestamp': t.timestamp
            }
            for t in self.trials
        ]
    
    def plot_optimization_history(self):
        """Plot optimization history (requires matplotlib)."""
        try:
            import matplotlib.pyplot as plt
            
            scores = [t.combined_score for t in self.trials]
            trial_ids = range(len(scores))
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
            
            # Score over trials
            ax1.plot(trial_ids, scores, 'b-', alpha=0.7)
            best_score = max(scores)
            ax1.axhline(best_score, color='r', linestyle='--', label=f'Best: {best_score:.2f}')
            ax1.set_xlabel('Trial Number')
            ax1.set_ylabel('Objective Score')
            ax1.set_title('Optimization Progress')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Score distribution
            ax2.hist(scores, bins=20, edgecolor='black', alpha=0.7)
            ax2.axvline(best_score, color='r', linestyle='--', label='Best')
            ax2.set_xlabel('Objective Score')
            ax2.set_ylabel('Frequency')
            ax2.set_title('Score Distribution')
            ax2.legend()
            ax2.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            return fig
        
        except ImportError:
            logger.warning("Matplotlib not available for plotting")
            return None
    
    def export_results(self, filepath: str) -> None:
        """Export optimization results to JSON."""
        import json
        
        export_data = {
            'best_trial': {
                'parameters': self.best_trial.parameters,
                'score': self.best_trial.combined_score
            } if self.best_trial else None,
            'all_trials': self.get_trial_history(),
            'n_trials': len(self.trials),
            'best_score': self.get_best_score()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"Results exported to {filepath}")
