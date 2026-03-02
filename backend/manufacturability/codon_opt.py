"""
Codon optimization for heterologous expression.
"""

import json
from pathlib import Path
from typing import Dict, Tuple
import numpy as np


class CodonOptimizer:
    """Optimizes codon usage for expression in target organisms."""
    
    def __init__(self, organism: str = "hek"):
        """
        Initialize codon optimizer.
        organism: "hek" (Human), "cho" (Chinese Hamster Ovary)
        """
        self.organism = organism
        self.codon_table = self._load_codon_table(organism)
        self.amino_acids = self._get_amino_acids()
    
    def _load_codon_table(self, organism: str) -> Dict[str, Dict[str, float]]:
        """Load codon usage table for organism."""
        codon_tables_dir = Path(__file__).parent / "codon_tables"
        table_file = codon_tables_dir / f"{organism}.json"
        
        if not table_file.exists():
            # Default codon table if file doesn't exist
            return self._default_codon_table()
        
        with open(table_file, 'r') as f:
            return json.load(f)
    
    def _default_codon_table(self) -> Dict[str, Dict[str, float]]:
        """Default human codon usage frequencies."""
        return {
            'A': {'GCA': 0.26, 'GCC': 0.40, 'GCG': 0.11, 'GCT': 0.23},
            'C': {'TGC': 0.55, 'TGT': 0.45},
            'D': {'GAC': 0.64, 'GAT': 0.36},
            'E': {'GAA': 0.42, 'GAG': 0.58},
            'F': {'TTC': 0.63, 'TTT': 0.37},
            'G': {'GGA': 0.25, 'GGC': 0.40, 'GGG': 0.23, 'GGT': 0.12},
            'H': {'CAC': 0.57, 'CAT': 0.43},
            'I': {'ATA': 0.07, 'ATC': 0.61, 'ATT': 0.32},
            'K': {'AAA': 0.42, 'AAG': 0.58},
            'L': {'CTA': 0.07, 'CTC': 0.38, 'CTG': 0.41, 'CTT': 0.13, 'TTA': 0.06, 'TTG': 0.13},
            'M': {'ATG': 1.00},
            'N': {'AAC': 0.67, 'AAT': 0.33},
            'P': {'CCA': 0.28, 'CCC': 0.33, 'CCG': 0.11, 'CCT': 0.27},
            'Q': {'CAA': 0.26, 'CAG': 0.74},
            'R': {'AGA': 0.21, 'AGG': 0.20, 'CGA': 0.07, 'CGC': 0.41, 'CGG': 0.20, 'CGT': 0.12},
            'S': {'AGC': 0.24, 'AGT': 0.15, 'TCA': 0.15, 'TCC': 0.22, 'TCG': 0.04, 'TCT': 0.17},
            'T': {'ACA': 0.25, 'ACC': 0.47, 'ACG': 0.11, 'ACT': 0.24},
            'V': {'GTA': 0.11, 'GTC': 0.26, 'GTG': 0.37, 'GTT': 0.26},
            'W': {'TGG': 1.00},
            'Y': {'TAC': 0.64, 'TAT': 0.36},
            '*': {'TAA': 0.28, 'TAG': 0.23, 'TGA': 0.49},
        }
    
    def _get_amino_acids(self) -> Dict[str, list]:
        """Map amino acids to their codons."""
        return {aa: list(codons.keys()) for aa, codons in self.codon_table.items()}
    
    def optimize(self, protein_sequence: str) -> Tuple[str, float]:
        """
        Optimize protein sequence for expression.
        
        Returns:
        optimized_dna: Optimized DNA sequence
        optimization_score: Score from 0-1 (1 = perfect optimization)
        """
        dna_sequence = ""
        codon_scores = []
        
        for aa in protein_sequence:
            if aa == 'X' or aa == '*':
                continue
            
            if aa not in self.codon_table:
                raise ValueError(f"Unknown amino acid: {aa}")
            
            # Select codon with highest frequency
            codons = self.codon_table[aa]
            best_codon = max(codons.keys(), key=lambda x: codons[x])
            score = codons[best_codon]
            codon_scores.append(score)
            dna_sequence += best_codon
        
        optimization_score = np.mean(codon_scores) if codon_scores else 0.0
        
        return dna_sequence, optimization_score
    
    def compute_cai(self, dna_sequence: str) -> float:
        """
        Compute Codon Adaptation Index (CAI).
        Measures translational efficiency. Range 0-1.
        """
        codons = [dna_sequence[i:i+3] for i in range(0, len(dna_sequence)-2, 3)]
        scores = []
        
        for codon in codons:
            # Find amino acid for codon
            for aa, codon_dict in self.codon_table.items():
                if codon in codon_dict:
                    scores.append(codon_dict[codon])
                    break
        
        return np.geometric_mean(scores) if scores else 0.0
    
    def compute_gc_content(self, dna_sequence: str) -> float:
        """Compute GC content (%), affects expression."""
        gc_count = dna_sequence.count('G') + dna_sequence.count('C')
        return (gc_count / len(dna_sequence)) * 100 if dna_sequence else 0.0
    
    def identify_rare_codons(self, dna_sequence: str, threshold: float = 0.15) -> list:
        """Identify codons below frequency threshold."""
        codons = [dna_sequence[i:i+3] for i in range(0, len(dna_sequence)-2, 3)]
        rare = []
        
        for i, codon in enumerate(codons):
            for aa, codon_dict in self.codon_table.items():
                if codon in codon_dict:
                    if codon_dict[codon] < threshold:
                        rare.append({'position': i, 'codon': codon, 'frequency': codon_dict[codon]})
                    break
        
        return rare
