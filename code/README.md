# COMS 4732 Project 1: Colorizing the Prokudin-Gorskii Collection

**Author:** Maddison Hoveida  
**UNI:** mh4572

## Requirements

- Python 3.7+
- NumPy
- scikit-image

Install dependencies:
```bash
pip install numpy scikit-image
```

## Setup

1. Place all input images in the same directory as `main.py`
2. Required images: 
`cathedral.jpg`, 
`monastery.jpg`, 
`tobolsk.jpg`, 
`church.tif`, 
`emir.tif`, 
`harvesters.tif`, 
`icon.tif`, 
`italil.tif`, 
`lastochikino.tif`, 
`lugano.tif`, 
`melons.tif`, 
`self_portrait.tif`, 
`siren.tif`, 
`three_generations.tif`
3. Additional images: 
`krym.tif`, 
`peonies.tif`, 
`capri.tif`

## Running the Code
1. Navigate to the code directory:
```bash
cd code/
```

2. Run the main script:
```bash
python main.py
```

3. The script will:
   - Process all images in the current directory
   - Create an `output/` folder
   - Save aligned images with multiple processing stages

## Output Files

For each input image, 6 files are generated:

**L2 metric:**
- `{name}_l2.jpg` - Aligned only
- `{name}_l2_wb.jpg` - Aligned + White balance
- `{name}_l2_final.jpg` - Aligned + White balance + Contrast

**NCC metric:**
- `{name}_ncc.jpg` - Aligned only
- `{name}_ncc_wb.jpg` - Aligned + White balance
- `{name}_ncc_final.jpg` - Aligned + White balance + Contrast

## Algorithm

- **Single-Scale:** Exhaustive search over [-15, 15] pixels (JPG images)
- **Pyramid:** Recursive coarse-to-fine alignment (TIF images)
- **Anchor:** Green channel (Blue was too noisy)
- **Metrics:** L2 (minimize) and NCC (maximize)

## Expected Runtime

- JPG images: ~1-2 seconds each
- TIF images: ~5-10 seconds each
- Total: ~2-3 minutes for all 17 images