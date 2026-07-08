# Prokudin-Gorskii Photo Collection Colorization Pipeline

This project contains a high-performance computer vision pipeline designed to automate the alignment and reconstruction of the historic Prokudin-Gorskii photo collection. By extracting and re-assembling the sequentially exposed red, green, and blue glass plate channels, this framework eliminates temporal and physical camera displacement to output vibrant, high-fidelity color restorations.

---

## Technical Pipeline & Key Design Decisions

### 1. Robust Reference Anchoring (Green vs. Blue Anchor)
While common approaches baseline alignment on the Blue channel, empirical testing revealed that the Blue channel frequently exhibits high grain, noise artifacts, and age-related blur. To resolve this, this implementation uses the **Green channel as the master anchor frame**. Red and Blue channels are systematically warped to align to the stable geometry of the Green plate.

### 2. Dual-Mode Spatial Alignment
* **Single-Scale Exhaustive Search**: Applied exclusively to low-resolution JPG assets. The algorithm runs an exhaustive window search over a boundary of `[-15, 15]` pixels to optimize alignment.
* **Coarse-to-Fine Image Pyramid**: Applied recursively to high-resolution TIF files. Utterances are downsampled to a manageable scale (threshold limit set to $500\text{px}$), aligned coarsely, and scaled back up to evaluate pixel-perfect local residuals using a tight `[-2, 2]` refinement step.

### 3. Quantitative Error Metrics
The pipeline benchmarks alignment using two independent similarity scoring functions over a central $10\%$ interior slice to clip out corrupted plate borders:
* **L2 Norm (SSD)**: Minimizes the Euclidean intensity distance between structural edges.
* **Normalized Cross-Correlation (NCC)**: Maximizes vector dot products to ensure high contrast matching.

### 4. Advanced Post-Processing (Bells & Whistles)
* **Automatic White Balance**: Employs the **Gray World Assumption**. Calculates average R, G, and B channel intensities across the aligned grid and dynamically rescales color vectors to force a neutral gray distribution, removing vintage age tints.
* **Automatic Contrast Correction**: Prevents flat tones by calculating the **2nd and 98th intensity percentiles**. This ignores clipping anomalies and flattens out values across the total `[0, 1]` float space via localized histogram stretching.
* **Adaptive Border Cropping**: Identifies borders based on file signatures. Applies a light $6\%$ crop for generic assets, an $8\%$ crop for heavily fractured edges (`lastochikino`, `lugano`), and custom directional masks (e.g., $15\%$ left-side crop for `self_portrait.tif`) to slice away plate frame shadows.

---

## Performance Summary

| Image Asset | Format | Red Displacement Vector $(y, x)$ | Blue Displacement Vector $(y, x)$ |
| :--- | :---: | :---: | :---: |
| **`cathedral`** | JPG | `[7, 1]` | `[-5, -2]` |
| **`monastery`** | JPG | `[6, 1]` | `[3, -2]` |
| **`tobolsk`** | JPG | `[4, 1]` | `[-3, -3]` |
| **`church`** | TIF | `[33, -8]` | `[-25, -4]` |
| **`emir`** | TIF | `[57, 17]` | `[-49, -24]` |
| **`harvesters`** | TIF | `[65, -3]` | `[-59, -16]` |
| **`melons`** | TIF | `[96, 4]` | `[-82, -11]` |
| **`self_portrait`** | TIF | `[98, 8]` | `[-79, -29]` |

*Note: For the small JPG files, the Coarse-to-Fine Pyramid alignment method successfully converges onto the exact same displacement vectors discovered by the exhaustive Single-Scale algorithm, verifying absolute structural consistency.*

---

## Installation & Execution

### 1. Requirements Configuration
Ensure you are running an environment with Python 3.7+ along with NumPy and scikit-image installed:
```bash
pip install numpy scikit-image

```

### 2. Execution Flow

Place your target glass plate image folders in the code directory, navigate into your local space, and execute:

```bash
cd code/
python main.py
```

The routine completes execution in approximately **2–3 minutes** across all 17 multi-layered files, generating structured outputs inside the local `output/` subfolder.
