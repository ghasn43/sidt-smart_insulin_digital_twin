"""
Page 3: Manufacturability & DNA Optimization
"""

import streamlit as st
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

from backend.manufacturability.codon_opt import CodonOptimizer
from backend.manufacturability.reverse_translate import ReverseTranslator
from backend.manufacturability.qc_checks import QCChecker
from backend.manufacturability.scoring import ManufacturabilityScorer

st.set_page_config(page_title="Manufacturability DNA", page_icon="🧪", layout="wide")
st.title("🧪 Insulin Variant Manufacturing")

st.markdown("Optimize DNA sequences and assess manufacturability of insulin variants.")

# Select organism
st.sidebar.markdown("## Expression Host")
organism = st.sidebar.radio("Target Organism", ["hek", "cho"], horizontal=True)

# Input protein sequence
st.markdown("### 1. Protein Sequence")
protein_input = st.text_area(
    "Enter insulin variant protein sequence (one-letter amino acid code)",
    "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKT",
    height=100
)

# Normalize input
protein_sequence = protein_input.upper().replace(" ", "").replace("\n", "")

if st.button("▶️ Optimize Sequence"):
    with st.spinner("Optimizing sequence..."):
        # Reverse translate
        translator = ReverseTranslator()
        dna_optimized, opt_score = translator.reverse_translate_optimized(protein_sequence)
        
        # Optimize codon usage
        optimizer = CodonOptimizer(organism)
        dna_final, cai = optimizer.optimize(protein_sequence)
        
        # Compute metrics
        gc_content = optimizer.compute_gc_content(dna_final)
        rare_codons = optimizer.identify_rare_codons(dna_final)
        
        # QC checks
        qc_checker = QCChecker()
        dna_qc = qc_checker.check_dna_sequence(dna_final)
        protein_qc = qc_checker.check_protein_variant(protein_sequence)
        
        st.session_state.dna_sequence = dna_final
        st.session_state.protein_sequence = protein_sequence
        st.session_state.optimizer = optimizer
        st.session_state.opt_score = opt_score
        st.session_state.cai = cai
        st.session_state.gc = gc_content
        st.session_state.rare = rare_codons
        st.session_state.dna_qc = dna_qc
        st.session_state.protein_qc = protein_qc
        st.session_state.organism = organism
        
        st.success("Sequence optimization complete!")

# Display results
if 'dna_sequence' in st.session_state:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Optimization Score", f"{st.session_state.opt_score:.1%}")
    with col2:
        st.metric("Codon Adaptation Index", f"{st.session_state.cai:.3f}")
    with col3:
        st.metric("GC Content", f"{st.session_state.gc:.1f}%")
    with col4:
        st.metric("Rare Codons", len(st.session_state.rare))
    
    st.markdown("---")
    
    # DNA Sequence display
    st.markdown("### Optimized DNA Sequence")
    dna_seq = st.session_state.dna_sequence
    # Display in chunks of 60
    formatted_dna = "\n".join([dna_seq[i:i+60] for i in range(0, len(dna_seq), 60)])
    st.code(formatted_dna, language="text")
    
    st.download_button(
        label="📥 Download DNA Sequence",
        data=f">{st.session_state.protein_sequence[:20]}...\n{formatted_dna}",
        file_name="insulin_variant.fasta",
        mime="text/plain"
    )
    
    # QC Results
    st.markdown("---")
    st.markdown("### Quality Control Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### DNA Sequence QC")
        dna_qc = st.session_state.dna_qc
        
        if dna_qc['passes_qc']:
            st.success("✅ DNA sequence passes QC")
        else:
            st.error("❌ DNA sequence has issues")
        
        if dna_qc['errors']:
            st.error("**Errors:**")
            for error in dna_qc['errors']:
                st.write(f"• {error}")
        
        if dna_qc['warnings']:
            st.warning("**Warnings:**")
            for warning in dna_qc['warnings']:
                st.write(f"• {warning}")
        
        st.markdown("**Metrics:**")
        for metric, value in dna_qc['metrics'].items():
            st.write(f"• {metric}: {value}")
    
    with col2:
        st.markdown("#### Protein Variant QC")
        protein_qc = st.session_state.protein_qc
        
        if protein_qc['passes_qc']:
            st.success("✅ Protein passes QC")
        else:
            st.warning("⚠️ Review warnings below")
        
        if protein_qc['warnings']:
            for warning in protein_qc['warnings']:
                st.info(f"• {warning}")
        
        st.markdown("**Analysis:**")
        for metric, value in protein_qc['metrics'].items():
            st.write(f"• {metric}: {value}")
    
    # Manufacturability scoring
    st.markdown("---")
    st.markdown("### Manufacturability Assessment")
    
    scorer = ManufacturabilityScorer()
    
    scores = {
        'expression': scorer.score_expression(
            st.session_state.gc / 100,
            st.session_state.cai,
            len(st.session_state.rare),
            st.session_state.dna_qc['metrics'].get('max_homopolymer_length', 0)
        ),
        'purification': scorer.score_purification(98, 75, 0.3),
        'stability': scorer.score_stability(0.7, 2, 1, 40),
        'safety': scorer.score_safety(2, 0.98, False),
        'regulatory': scorer.score_regulatory(3, 'analog'),
    }
    
    overall = scorer.compute_overall_score(scores)
    risk = scorer.get_risk_category(overall)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.metric("Overall Manufacturability Score", f"{overall:.1f}/100")
        st.markdown(f"**Risk Category:** {risk}")
    with col2:
        st.markdown("**Component Scores:**")
        for component, score in scores.items():
            st.write(f"{component.capitalize()}: {score:.0f}")
    
    # Recommendations
    st.markdown("---")
    st.markdown("### Recommendations")
    
    recommendations = []
    if st.session_state.gc < 40 or st.session_state.gc > 60:
        recommendations.append(f"• Adjust GC content (currently {st.session_state.gc:.1f}%)")
    if len(st.session_state.rare) > 5:
        recommendations.append("• Address rare codons for better expression")
    if scores['expression'] < 70:
        recommendations.append("• Consider codon optimization for target organism")
    
    if recommendations:
        for rec in recommendations:
            st.info(rec)
    else:
        st.success("✅ Sequence is well-optimized!")

else:
    st.info("👈 Enter a protein sequence and click 'Optimize Sequence'")
