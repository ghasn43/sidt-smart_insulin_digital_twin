"""
Quality control checks for manufacturing.
"""

from typing import Dict, List, Tuple
import numpy as np
import re


class QCChecker:
    """Performs quality control checks on sequences and manufacturing parameters."""
    
    def __init__(self):
        """Initialize QC checker."""
        self.min_sequence_length = 60  # codons
        self.max_sequence_length = 1500  # codons
        self.target_gc_min = 0.40
        self.target_gc_max = 0.60
        self.max_homopolymer = 8  # consecutive identical bases
        self.min_expression_level = 0.5  # Units/mL
    
    def check_dna_sequence(self, dna_sequence: str) -> Dict[str, any]:
        """Comprehensive DNA sequence QC check."""
        results = {
            'passes_qc': True,
            'warnings': [],
            'errors': [],
            'metrics': {}
        }
        
        # Length check
        if len(dna_sequence) < self.min_sequence_length * 3:
            results['errors'].append(f"Sequence too short: {len(dna_sequence)} bp")
            results['passes_qc'] = False
        
        if len(dna_sequence) > self.max_sequence_length * 3:
            results['warnings'].append(f"Sequence very long: {len(dna_sequence)} bp")
        
        # GC content
        gc_content = self._calculate_gc_content(dna_sequence)
        results['metrics']['gc_content'] = gc_content
        
        if gc_content < self.target_gc_min or gc_content > self.target_gc_max:
            results['warnings'].append(f"GC content {gc_content:.1%} outside optimal range")
        
        # Homopolymer runs
        homopolymers = self._find_homopolymers(dna_sequence)
        results['metrics']['max_homopolymer_length'] = max(homopolymers) if homopolymers else 0
        
        if any(h > self.max_homopolymer for h in homopolymers):
            results['errors'].append(f"Homopolymer run exceeds {self.max_homopolymer} bp")
            results['passes_qc'] = False
        
        # Restriction sites (markers for recombination dangers)
        restriction_warnings = self._check_restriction_sites(dna_sequence)
        results['metrics']['restriction_sites'] = len(restriction_warnings)
        if restriction_warnings:
            results['warnings'].append(f"Found {len(restriction_warnings)} common restriction sites")
        
        # Secondary structure
        complexity = self._estimate_sequence_complexity(dna_sequence)
        results['metrics']['sequence_complexity'] = complexity
        
        if complexity < 0.5:
            results['warnings'].append("Low sequence complexity may cause issues")
        
        return results
    
    def check_protein_variant(self, protein_sequence: str) -> Dict[str, any]:
        """QC check for protein variant."""
        results = {
            'passes_qc': True,
            'warnings': [],
            'errors': [],
            'metrics': {}
        }
        
        # Basic amino acid check
        invalid_aas = [aa for aa in protein_sequence if aa not in 'ACDEFGHIKLMNPQRSTVWY*X']
        if invalid_aas:
            results['errors'].append(f"Invalid amino acids: {set(invalid_aas)}")
            results['passes_qc'] = False
        
        # Hydrophobic clusters
        hydro_regions = self._find_hydrophobic_clusters(protein_sequence)
        if hydro_regions:
            results['metrics']['hydrophobic_clusters'] = len(hydro_regions)
            results['warnings'].append(f"Found {len(hydro_regions)} hydrophobic regions")
        
        # Disulfide bonds
        cysteines = protein_sequence.count('C')
        results['metrics']['cysteine_count'] = cysteines
        if cysteines % 2 != 0:
            results['warnings'].append("Odd number of cysteines may affect disulfide bonding")
        
        # Glycosylation sites
        n_glyco = self._count_n_glycosylation_sites(protein_sequence)
        o_glyco = self._count_o_glycosylation_sites(protein_sequence)
        results['metrics']['n_glycosylation_sites'] = n_glyco
        results['metrics']['o_glycosylation_sites'] = o_glyco
        
        return results
    
    def check_manufacturing_parameters(self, parameters: Dict) -> Dict[str, any]:
        """QC check for manufacturing specifications."""
        results = {
            'passes_qc': True,
            'warnings': [],
            'errors': []
        }
        
        required_fields = [
            'target_expression_level',
            'purification_yield',
            'endotoxin_level',
            'protein_purity'
        ]
        
        # Check required fields
        missing = [f for f in required_fields if f not in parameters]
        if missing:
            results['errors'].append(f"Missing parameters: {missing}")
            results['passes_qc'] = False
        
        # Check realistic values
        if 'target_expression_level' in parameters:
            expr = parameters['target_expression_level']
            if expr < 0.1 or expr > 10:
                results['warnings'].append(f"Unusual expression level: {expr} g/L")
        
        if 'purification_yield' in parameters:
            yield_pct = parameters['purification_yield']
            if yield_pct < 20 or yield_pct > 95:
                results['warnings'].append(f"Unusual purification yield: {yield_pct}%")
        
        if 'endotoxin_level' in parameters:
            endotoxin = parameters['endotoxin_level']
            if endotoxin > 10:
                results['errors'].append(f"Endotoxin level {endotoxin} EU/mL exceeds safety limit")
                results['passes_qc'] = False
        
        if 'protein_purity' in parameters:
            purity = parameters['protein_purity']
            if purity < 95:
                results['warnings'].append(f"Protein purity {purity}% below therapeutic standard")
        
        return results
    
    def _calculate_gc_content(self, dna_sequence: str) -> float:
        """Calculate GC content."""
        gc_count = dna_sequence.count('G') + dna_sequence.count('C')
        return gc_count / len(dna_sequence) if dna_sequence else 0
    
    def _find_homopolymers(self, dna_sequence: str) -> List[int]:
        """Find homopolymer runs."""
        pattern = r'(A{4,}|T{4,}|G{4,}|C{4,})'
        matches = re.findall(pattern, dna_sequence.upper())
        return [len(m) for m in matches]
    
    def _check_restriction_sites(self, dna_sequence: str) -> List[Tuple[str, int]]:
        """Check for common restriction sites."""
        sites = {
            'EcoRI': 'GAATTC',
            'BamHI': 'GGATCC',
            'HindIII': 'AAGCTT',
            'NotI': 'GCGGCCGC',
            'SmaI': 'CCCGGG'
        }
        
        found_sites = []
        seq_upper = dna_sequence.upper()
        
        for name, seq in sites.items():
            if seq in seq_upper:
                found_sites.append((name, seq_upper.count(seq)))
        
        return found_sites
    
    def _estimate_sequence_complexity(self, dna_sequence: str) -> float:
        """Estimate Shannon entropy as complexity measure."""
        seq_upper = dna_sequence.upper()
        counts = {'A': 0, 'T': 0, 'G': 0, 'C': 0}
        
        for base in seq_upper:
            if base in counts:
                counts[base] += 1
        
        total = sum(counts.values())
        if total == 0:
            return 0.0
        
        entropy = 0.0
        for count in counts.values():
            if count > 0:
                p = count / total
                entropy -= p * np.log2(p)
        
        return entropy / 2.0  # Normalized to 0-1
    
    def _find_hydrophobic_clusters(self, protein_sequence: str) -> List[Tuple[int, int]]:
        """Find clusters of hydrophobic amino acids."""
        hydrophobic = set('AILMFVPW')
        clusters = []
        in_cluster = False
        cluster_start = 0
        
        for i, aa in enumerate(protein_sequence):
            if aa in hydrophobic and not in_cluster:
                cluster_start = i
                in_cluster = True
            elif aa not in hydrophobic and in_cluster:
                if i - cluster_start >= 6:  # Clusters of 6+ residues
                    clusters.append((cluster_start, i - 1))
                in_cluster = False
        
        return clusters
    
    def _count_n_glycosylation_sites(self, protein_sequence: str) -> int:
        """Count N-glycosylation sites (N-X-[S/T])."""
        pattern = r'N[^P][S|T]'
        return len(re.findall(pattern, protein_sequence))
    
    def _count_o_glycosylation_sites(self, protein_sequence: str) -> int:
        """Count O-glycosylation sites (S/T-X-P)."""
        pattern = r'[S|T].P'
        return len(re.findall(pattern, protein_sequence))
