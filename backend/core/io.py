"""
Input/Output utilities for Smart Insulin Digital Twin.
"""

import json
import pickle
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataManager:
    """Manages data persistence and I/O operations."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.sim_dir = self.data_dir / "simulations"
        self.sim_dir.mkdir(parents=True, exist_ok=True)
    
    def save_json(self, data: Dict[str, Any], filename: str) -> Path:
        """Save data as JSON."""
        filepath = self.data_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Saved JSON to {filepath}")
        return filepath
    
    def load_json(self, filename: str) -> Dict[str, Any]:
        """Load data from JSON."""
        filepath = self.data_dir / filename
        with open(filepath, 'r') as f:
            data = json.load(f)
        logger.info(f"Loaded JSON from {filepath}")
        return data
    
    def save_pickle(self, data: Any, filename: str) -> Path:
        """Save data as pickle."""
        filepath = self.data_dir / filename
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        logger.info(f"Saved pickle to {filepath}")
        return filepath
    
    def load_pickle(self, filename: str) -> Any:
        """Load data from pickle."""
        filepath = self.data_dir / filename
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        logger.info(f"Loaded pickle from {filepath}")
        return data
    
    def save_simulation(self, result, name: str) -> Path:
        """Save simulation results with metadata."""
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'simulation_name': name,
            'patient_id': result.patient.patient_id,
            'metrics': result.to_dict(),
        }
        
        filename = f"sim_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        meta_file = self.sim_dir / f"{filename}_meta.json"
        data_file = self.sim_dir / f"{filename}_data.pkl"
        
        with open(meta_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        with open(data_file, 'wb') as f:
            pickle.dump(result, f)
        
        logger.info(f"Saved simulation to {data_file}")
        return data_file
    
    def list_simulations(self) -> list:
        """List all saved simulations."""
        pkl_files = list(self.sim_dir.glob("*_data.pkl"))
        return [f.stem.replace("_data", "") for f in pkl_files]
    
    def load_simulation(self, name: str):
        """Load a saved simulation."""
        data_file = self.sim_dir / f"{name}_data.pkl"
        meta_file = self.sim_dir / f"{name}_meta.json"
        
        if not data_file.exists():
            raise FileNotFoundError(f"Simulation {name} not found")
        
        with open(data_file, 'rb') as f:
            result = pickle.load(f)
        
        with open(meta_file, 'r') as f:
            metadata = json.load(f)
        
        logger.info(f"Loaded simulation {name}")
        return result, metadata


def save_simulation(result, filepath: str) -> None:
    """Save simulation results to file."""
    manager = DataManager()
    manager.save_pickle(result, Path(filepath).name)


def load_simulation(filepath: str):
    """Load simulation results from file."""
    manager = DataManager()
    return manager.load_pickle(Path(filepath).name)


def export_to_csv(result, filepath: str) -> None:
    """Export simulation results to CSV."""
    import pandas as pd
    
    df = pd.DataFrame({
        'timestamp': result.timestamps,
        'glucose_mg_dl': result.glucose_mg_dl,
        'insulin_units': result.insulin_units,
        'carb_intake': result.carb_intake,
    })
    df.to_csv(filepath, index=False)
    logger.info(f"Exported simulation to {filepath}")


def import_from_csv(filepath: str) -> Dict[str, np.ndarray]:
    """Import data from CSV."""
    import pandas as pd
    
    df = pd.read_csv(filepath)
    return {
        'timestamps': pd.to_datetime(df['timestamp']).values,
        'glucose_mg_dl': df['glucose_mg_dl'].values,
        'insulin_units': df['insulin_units'].values,
        'carb_intake': df['carb_intake'].values,
    }
