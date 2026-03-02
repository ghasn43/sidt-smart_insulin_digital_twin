"""
Plotting utilities for Smart Insulin Digital Twin.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Tuple, Optional, List
from datetime import datetime
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)


def plot_glucose_profile(
    timestamps: np.ndarray,
    glucose_mg_dl: np.ndarray,
    title: str = "Glucose Profile",
    figsize: Tuple[int, int] = (14, 6)
) -> plt.Figure:
    """Plot glucose profile with target ranges."""
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot glucose
    ax.plot(timestamps, glucose_mg_dl, 'b-', linewidth=2, label='Glucose')
    
    # Target ranges
    ax.axhspan(70, 180, alpha=0.2, color='green', label='Target Range (70-180)')
    ax.axhline(70, color='orange', linestyle='--', alpha=0.7, label='Low Alert')
    ax.axhline(180, color='red', linestyle='--', alpha=0.7, label='High Alert')
    
    # Formatting
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Glucose (mg/dL)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    if len(timestamps) > 0:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.xticks(rotation=45)
    
    plt.tight_layout()
    return fig


def plot_insulin_delivery(
    timestamps: np.ndarray,
    insulin_units: np.ndarray,
    carb_intake: np.ndarray,
    title: str = "Insulin Delivery and Carb Intake",
    figsize: Tuple[int, int] = (14, 8)
) -> plt.Figure:
    """Plot insulin delivery and carbohydrate intake."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)
    
    # Insulin plot
    ax1.plot(timestamps, insulin_units, 'r-', linewidth=2, label='Insulin On Board')
    ax1.fill_between(timestamps, 0, insulin_units, alpha=0.3, color='red')
    ax1.set_ylabel('Insulin (Units)', fontsize=11)
    ax1.set_title(title, fontsize=13, fontweight='bold')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Carb intake plot
    ax2.bar(timestamps, carb_intake, color='orange', alpha=0.7, label='Carb Intake')
    ax2.set_xlabel('Time', fontsize=11)
    ax2.set_ylabel('Carbs (grams)', fontsize=11)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3, axis='y')
    
    if len(timestamps) > 0:
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.xticks(rotation=45)
    
    plt.tight_layout()
    return fig


def plot_comparison(
    timestamps_list: List[np.ndarray],
    glucose_list: List[np.ndarray],
    labels: List[str],
    title: str = "Comparison of Control Strategies",
    figsize: Tuple[int, int] = (14, 7)
) -> plt.Figure:
    """Compare multiple glucose profiles."""
    fig, ax = plt.subplots(figsize=figsize)
    
    colors = ['blue', 'red', 'green', 'purple', 'orange']
    
    for i, (timestamps, glucose, label) in enumerate(zip(timestamps_list, glucose_list, labels)):
        color = colors[i % len(colors)]
        ax.plot(timestamps, glucose, color=color, linewidth=2, label=label)
    
    # Target ranges
    if len(timestamps_list) > 0:
        ax.axhspan(70, 180, alpha=0.15, color='green')
        ax.axhline(70, color='orange', linestyle='--', alpha=0.5, linewidth=1)
        ax.axhline(180, color='red', linestyle='--', alpha=0.5, linewidth=1)
    
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Glucose (mg/dL)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    if len(timestamps_list) > 0 and len(timestamps_list[0]) > 0:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.xticks(rotation=45)
    
    plt.tight_layout()
    return fig


def plot_daily_patterns(
    glucose_mg_dl: np.ndarray,
    timestamps: np.ndarray,
    title: str = "Daily Glucose Patterns",
    figsize: Tuple[int, int] = (14, 6)
) -> plt.Figure:
    """Plot glucose patterns by hour of day."""
    fig, ax = plt.subplots(figsize=figsize)
    
    # Extract hours from timestamps
    hours = np.array([t.hour for t in timestamps])
    unique_hours = np.arange(0, 24)
    
    # Calculate mean glucose by hour
    hourly_glucose = []
    for hour in unique_hours:
        mask = hours == hour
        if np.any(mask):
            hourly_glucose.append(np.mean(glucose_mg_dl[mask]))
        else:
            hourly_glucose.append(np.nan)
    
    ax.plot(unique_hours, hourly_glucose, 'o-', linewidth=2, markersize=8, color='blue')
    ax.axhspan(70, 180, alpha=0.2, color='green')
    ax.axhline(70, color='orange', linestyle='--', alpha=0.7)
    ax.axhline(180, color='red', linestyle='--', alpha=0.7)
    
    ax.set_xlabel('Hour of Day', fontsize=12)
    ax.set_ylabel('Mean Glucose (mg/dL)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xticks(unique_hours)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_glycemic_variability(
    glucose_mg_dl: np.ndarray,
    timestamps: np.ndarray,
    window_hours: int = 24,
    title: str = "Glycemic Variability (Coefficient of Variation)",
    figsize: Tuple[int, int] = (14, 6)
) -> plt.Figure:
    """Plot glycemic variability over time."""
    fig, ax = plt.subplots(figsize=figsize)
    
    # Calculate rolling variability
    window_size = max(1, int(len(glucose_mg_dl) / (24 / window_hours)))
    if window_size > 1:
        rolling_cv = []
        rolling_times = []
        
        for i in range(0, len(glucose_mg_dl) - window_size, window_size // 2):
            segment = glucose_mg_dl[i:i + window_size]
            cv = (np.std(segment) / np.mean(segment)) * 100 if np.mean(segment) > 0 else 0
            rolling_cv.append(cv)
            rolling_times.append(timestamps[i + window_size // 2])
        
        ax.plot(rolling_times, rolling_cv, 'g-', linewidth=2, marker='o', markersize=5)
    
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Coefficient of Variation (%)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    if len(timestamps) > 0:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.xticks(rotation=45)
    
    plt.tight_layout()
    return fig
