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
