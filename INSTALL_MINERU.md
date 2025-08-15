# Installing MinerU for Advanced PDF Conversion

MinerU provides superior PDF conversion quality, especially for:
- Complex scientific papers with formulas
- Multi-column layouts
- Tables and figures
- Scanned PDFs (with OCR)

## Installation Options

### Option 1: Basic Installation (CPU only)
```bash
uv pip install magic-pdf[full] --extra-index-url https://myhloli.github.io/wheels/
```

### Option 2: CUDA GPU Support (NVIDIA)
```bash
# Ensure CUDA is installed first
uv pip install magic-pdf[full] --extra-index-url https://myhloli.github.io/wheels/
```

### Option 3: Apple Silicon Support (M1/M2/M3)
```bash
# For MPS (Metal Performance Shaders) support
uv pip install magic-pdf[full-mps] --extra-index-url https://myhloli.github.io/wheels/
```

## Verify Installation

```bash
# Test if MinerU is available
uv run python -c "import magic_pdf; print('MinerU installed successfully!')"
```

## Troubleshooting

### Common Issues:

1. **ImportError**: Make sure to use the custom index URL
2. **CUDA not found**: MinerU will automatically fall back to CPU
3. **Large download**: The package is ~500MB due to ML models

### Fallback Behavior:

If MinerU is not installed or fails, the system automatically falls back to MarkItDown for basic PDF conversion. Your files will still be converted, just with simpler formatting.

## Benefits of MinerU

- **Better formula rendering**: LaTeX formulas preserved
- **Table extraction**: Complex tables converted accurately  
- **Multi-column support**: Research papers layout maintained
- **OCR capability**: Can extract text from scanned PDFs
- **GPU acceleration**: 10x faster on CUDA/MPS devices

## Notes

- MinerU is optional but recommended for scientific documents
- The system works fine without it using MarkItDown
- Installation adds ~500MB to environment size
- First conversion may be slower due to model loading