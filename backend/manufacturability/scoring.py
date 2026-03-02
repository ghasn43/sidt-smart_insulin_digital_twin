"""
Scoring system for manufacturability assessment.
"""

from typing import Dict, Tuple
import numpy as np


class ManufacturabilityScorer:
    """Scores manufacturability of insulin variants and manufacturing processes."""
    
    def __init__(self):
        """Initialize scorer with weights."""
        self.weights = {
            'expression': 0.25,
            'purification': 0.20,
            'stability': 0.20,
            'safety': 0.20,
            'regulatory': 0.15,
        }
    
    def score_expression(
        self,
        gc_content: float,
        codon_adaptation_index: float,
        rare_codon_count: int,
        max_homo polymer: int
    ) -> float:
        """Score expression likelihood (0-100)."""
        score = 100.0
        
        # GC content (optimal 40-60%)
        if 0.4 <= gc_content <= 0.6:
            gc_score = 100
        elif 0.3 <= gc_content <= 0.7:
            gc_score = 80
        else:
            gc_score = 50
        
        # CAI score (higher is better)
        cai_score = codon_adaptation_index * 100
        
        # Rare codons penalty
        rare_penalty = min(30, rare_codon_count * 2)
        
        # Homopolymer penalty (long runs interfere with synthesis)
        homo_penalty = min(25, max(0, max_homopolymer - 8) * 2)
        
        score = (gc_score * 0.3 + cai_score * 0.4 - rare_penalty * 0.2 - homo_penalty * 0.1)
        
        return max(0, min(100, score))
    
    def score_purification(
        self,
        target_purity: float,
        yield_percent: float,
        protein_aggregation_risk: float
    ) -> float:
        """Score purification feasibility (0-100)."""
        score = 100.0
        
        # Purity target (higher = harder but better)
        if target_purity >= 98:
            purity_score = 100
        elif target_purity >= 95:
            purity_score = 90
        elif target_purity >= 90:
            purity_score = 80
        else:
            purity_score = 70
        
        # Yield (higher = better)
        yield_score = min(100, yield_percent * 1.2)
        
        # Aggregation risk (lower = better for purification)
        aggregation_penalty = aggregation_risk * 30
        
        score = (purity_score * 0.4 + yield_score * 0.4 - aggregation_penalty * 0.2)
        
        return max(0, min(100, score))
    
    def score_stability(
        self,
        sequence_complexity: float,
        disulfide_bonds: int,
        glycosylation_sites: int,
        predicted_tm_celsius: float
    ) -> float:
        """Score protein stability (0-100)."""
        score = 100.0
        
        # Sequence complexity (higher = more stable)
        complexity_score = sequence_complexity * 100
        
        # Disulfide bonds (some is good, too many might be risky)
        if 0 < disulfide_bonds <= 2:
            disulfide_score = 100
        elif disulfide_bonds == 0:
            disulfide_score = 80
        else:
            disulfide_score = max(50, 100 - (disulfide_bonds - 2) * 10)
        
        # Glycosylation (helps stability)
        if glycosylation_sites > 0:
            glyco_score = min(100, 70 + glycosylation_sites * 15)
        else:
            glyco_score = 70
        
        # Melting temperature (37-42°C optimal for insulin)
        if 37 <= predicted_tm_celsius <= 45:
            tm_score = 100
        elif 30 <= predicted_tm_celsius <= 50:
            tm_score = 80
        else:
            tm_score = 50
        
        score = (complexity_score * 0.2 + disulfide_score * 0.3 + 
                glyco_score * 0.2 + tm_score * 0.3)
        
        return max(0, min(100, score))
    
    def score_safety(
        self,
        endotoxin_level: float,
        protein_homology: float,
        known_immunogenic: bool
    ) -> float:
        """Score manufacturing safety (0-100)."""
        score = 100.0
        
        # Endotoxin (lower = better)
        if endotoxin_level < 1:
            endotoxin_score = 100
        elif endotoxin_level < 5:
            endotoxin_score = 80
        elif endotoxin_level < 10:
            endotoxin_score = 50
        else:
            endotoxin_score = 0
        
        # Homology to reference insulin (higher = safer)
        homology_score = protein_homology * 100 if protein_homology > 0.95 else protein_homology * 80
        
        # Known immunogenicity (penalty if true)
        immunogenic_penalty = 30 if known_immunogenic else 0
        
        score = (endotoxin_score * 0.4 + homology_score * 0.4 - immunogenic_penalty * 0.2)
        
        return max(0, min(100, score))
    
    def score_regulatory(self, changes_from_reference: int, variant_type: str) -> float:
        """Score regulatory pathway complexity (0-100)."""
        score = 100.0
        
        # Number of amino acid changes
        change_penalty = min(50, changes_from_reference * 5)
        
        # Type of variant
        if variant_type.lower() == 'analog':
            regulatory_complexity = 20  # Analogs are well-studied
        elif variant_type.lower() == 'ultra_long':
            regulatory_complexity = 30
        elif variant_type.lower() == 'ultra_rapid':
            regulatory_complexity = 35
        elif variant_type.lower() == 'novel':
            regulatory_complexity = 50
        else:
            regulatory_complexity = 40
        
        score = 100 - change_penalty - regulatory_complexity
        
        return max(0, min(100, score))
    
    def compute_overall_score(self, component_scores: Dict[str, float]) -> float:
        """Compute weighted overall manufacturability score."""
        total_score = 0.0
        
        for component, weight in self.weights.items():
            if component in component_scores:
                total_score += component_scores[component] * weight
        
        return round(total_score, 1)
    
    def get_risk_category(self, overall_score: float) -> str:
        """Categorize manufacturability risk based on score."""
        if overall_score >= 85:
            return "LOW RISK - Highly manufacturable"
        elif overall_score >= 70:
            return "MODERATE RISK - Manufacturable with optimizations"
        elif overall_score >= 55:
            return "HIGH RISK - Significant manufacturing challenges"
        else:
            return "VERY HIGH RISK - Major manufacturability concerns"
    
    def generate_report(
        self,
        variant_name: str,
        component_scores: Dict[str, float],
        recommendations: list = None
    ) -> Dict:
        """Generate comprehensive manufacturability report."""
        overall = self.compute_overall_score(component_scores)
        risk_category = self.get_risk_category(overall)
        
        report = {
            'variant_name': variant_name,
            'overall_score': overall,
            'risk_category': risk_category,
            'component_scores': component_scores,
            'recommendations': recommendations or [],
            'summary': f"{variant_name} has {risk_category}"
        }
        
        return report
