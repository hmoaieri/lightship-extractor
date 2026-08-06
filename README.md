# Lightship Weight Extractor

This repository implements a reverse engineering method to extract the longitudinal distribution of lightship weight from standard loading manual data.

## Method Overview

The method uses the fundamental relationship between shear force (S), buoyancy (b), and deadweight (w_DW) to recover the lightship weight (w_LS):
`w_LS(x) = b(x) - dS(x)/dx - w_DW(x)`

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/lightship-extractor.git
cd lightship-extractor
pip install -e .
Usage

See example.py for a complete demonstration.
Data Requirements

    Shear force curve at standard stations

    Submerged cross-sectional areas

    Compartment layout (tanks, cargo holds)

Citation

If you use this code, please cite:
[Your Paper Reference]
text


**4. Sample Data Files**
- `data/sample_shear_force.csv`: Two columns: `Position, Shear_Force`
- `data/sample_section_area.csv`: Two columns: `Position, Section_Area`
- `data/sample_tanks.json`: JSON array of compartment objects

---

### Instructions to Upload to GitHub

1.  **Create a new repository** on GitHub (do not initialize with README, .gitignore, or license).
2.  **On your local machine**, create the project folder with the structure above.
3.  **Run these commands** in the project folder:
    ```bash
    git init
    git add .
    git commit -m "Initial commit: Full implementation of lightship weight extractor"
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/lightship-extractor.git
    git push -u origin main

    Replace YOUR_USERNAME with your actual GitHub username in the commands and README.md.





Contact & Support

    Authors: Dr. Hamid Moaieri

    Affiliation: Department of MARINE ENG,IMAM KHOMEINI MARITIME UNIVERSITY

    Email: H.MOAIERI@GMAIL.COM

    Issues: Please use the GitHub issue tracker for bug reports and feature requests
