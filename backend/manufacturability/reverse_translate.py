"""
Reverse translation of protein sequences to DNA.
"""

from typing import Dict, Tuple, Optional
import numpy as np


class ReverseTranslator:
    """Translates protein sequences back to DNA with optimization."""
    
    def __init__(self, codon_usage: Optional[Dict] = None):
        """Initialize with codon usage table."""
        self.codon_usage = codon_usage or self._default_codon_usage()
        self.genetic_code = self._get_genetic_code()
    
    def _default_codon_usage(self) -> Dict[str, dict]:
        """Default human codon usage."""
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
    
    def _get_genetic_code(self) -> Dict[str, str]:
        """Standard genetic code."""
        return {
            'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M',
            'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
            'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K',
            'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R',
            'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L',
            'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
            'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q',
            'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
            'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V',
            'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
            'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E',
            'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
            'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S',
            'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
            'TAC':'Y', 'TAT':'Y', 'TAA':'*', 'TAG':'*',
            'TGC':'C', 'TGT':'C', 'TGA':'*', 'TGG':'W',
        }
    
    def translate(self, dna_sequence: str) -> str:
        """Translate DNA to protein."""
        protein = ""
        for i in range(0, len(dna_sequence) - 2, 3):
            codon = dna_sequence[i:i+3].upper()
            if len(codon) == 3:
                protein += self.genetic_code.get(codon, 'X')
        return protein
    
    def reverse_translate_optimized(self, protein_sequence: str) -> Tuple[str, float]:
        """
        Reverse translate protein to DNA with optimization.
        
        Returns:
        dna_sequence: Optimized DNA sequence
        optimization_score: Average codon frequency score (0-1)
        """
        dna = ""
        scores = []
        
        for aa in protein_sequence:
            if aa == 'X' or aa == '*':
                continue
            
            if aa not in self.codon_usage:
                raise ValueError(f"Unknown amino acid: {aa}")
            
            # Select most frequent codon
            codons = self.codon_usage[aa]
            best_codon = max(codons.keys(), key=lambda x: codons[x])
            score = codons[best_codon]
            
            dna += best_codon
            scores.append(score)
        
        optimized_score = np.mean(scores) if scores else 0.0
        return dna, optimized_score
    
    def reverse_translate_degeneracy(self, protein_sequence: str, method: str = "conserved") -> str:
        """
        Reverse translate with different degeneracy strategies.
        
        method: "conserved" (most frequent), "random" (random codon), "balanced"
        """
        dna = ""
        
        for aa in protein_sequence:
            if aa == 'X' or aa == '*':
                continue
            
            if aa not in self.codon_usage:
                raise ValueError(f"Unknown amino acid: {aa}")
            
            codons = self.codon_usage[aa]
            
            if method == "conserved":
                codon = max(codons.keys(), key=lambda x: codons[x])
            elif method == "balanced":
                # Weighted random selection
                codon_list = list(codons.keys())
                weights = [codons[c] for c in codon_list]
                codon = np.random.choice(codon_list, p=np.array(weights)/sum(weights))
            else:  # random
                codon = np.random.choice(list(codons.keys()))
            
            dna += codon
        
        return dna
    
    def codon_harmonization(self, dna_sequence: str, gc_target: float = 0.5) -> str:
        """
        Harmonize codon usage to reach target GC content.
        """
        gc_content = (dna_sequence.count('G') + dna_sequence.count('C')) / len(dna_sequence)
        
        if abs(gc_content - gc_target) < 0.05:
            return dna_sequence
        
        protein = self.translate(dna_sequence)
        harmonized = ""
        
        for aa in protein:
            if aa not in self.codon_usage:
                continue
            
            codons = self.codon_usage[aa]
            
            # Score codons based on GC content and usage
            best_score = -1
            best_codon = None
            
            for codon, freq in codons.items():
                codon_gc = (codon.count('G') + codon.count('C')) / 3
                gc_diff = abs(codon_gc - gc_target)
                score = freq - (0.5 * gc_diff)
                
                if score > best_score:
                    best_score = score
                    best_codon = codon
            
            if best_codon:
                harmonized += best_codon
        
        return harmonized
    
    def validate_sequence(self, dna_sequence: str) -> Tuple[bool, list]:
        """
        Validate DNA sequence for manufacturability.
        
        Returns:
        is_valid: Boolean indicating if sequence is valid
        issues: List of any issues found
        """
        issues = []
        
        # Check for invalid characters
        valid_chars = set('ATGC')
        if not all(c in valid_chars for c in dna_sequence.upper()):
            issues.append("Invalid DNA characters")
        
        # Check for stop codons in middle
        protein = self.translate(dna_sequence)
        if '*' in protein[:-1]:
            issues.append("Stop codon in middle of sequence")
        
        # Check GC content
        gc_content = (dna_sequence.count('G') + dna_sequence.count('C')) / len(dna_sequence)
        if gc_content < 0.35 or gc_content > 0.65:
            issues.append(f"GC content {gc_content*100:.1f}% outside recommended range")
        
        return len(issues) == 0, issues
