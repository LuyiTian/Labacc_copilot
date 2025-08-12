# PCR Optimization Experiment - exp_001

**Date**: 2025-08-12  
**Objective**: Optimize PCR conditions for GC-rich template amplification

## Protocol

**Template**: GC-rich genomic DNA (65% GC content)  
**Primers**: Forward: 5'-GCGCGCATCGATCGAT-3', Reverse: 5'-TATCGATCGATGCGCG-3'  
**Product Size**: 1.2 kb

### Reaction Conditions Tested:
1. **Standard Taq**: 94°C-30s, 58°C-30s, 72°C-1min x 30 cycles
2. **High GC Buffer**: Added 5% DMSO, increased annealing to 62°C  
3. **Touchdown PCR**: Starting at 65°C, decreasing 0.5°C per cycle

## Results

- **Standard Taq**: Faint bands, multiple non-specific products
- **High GC Buffer**: Strong specific band, minimal background
- **Touchdown**: Clean specific product, highest yield

## Analysis

**Success Rate**: 67% (2/3 conditions successful)  
**Best Condition**: High GC buffer with DMSO addition  
**Key Factor**: DMSO significantly improved amplification efficiency

## Next Steps

1. Test DMSO concentration range (2.5-10%)
2. Try alternative polymerases (Phusion, Q5)
3. Optimize Mg2+ concentration
4. Test nested PCR approach

## Files

- `gel_image_001.jpg` - Agarose gel results
- `protocol_conditions.xlsx` - Detailed reaction conditions
- `thermal_cycler_log.txt` - Temperature profiles used