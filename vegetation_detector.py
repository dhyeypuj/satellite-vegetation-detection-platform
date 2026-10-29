"""
Vegetation Detection in Satellite Images using OpenCV & Remote Sensing Indices

This module implements multiple vegetation detection algorithms
and provides comparison analysis, density mapping, and statistics.

Methods implemented:
    1. HSV Color Space Segmentation
    2. Excess Green Index (ExG)
    3. Excess Green minus Red (ExGR)
    4. Visible Atmospherically Resistant Index (VARI)
    5. Green Leaf Index (GLI)
    6. Sobel Edge Detection (baseline method, retained for comparison)
"""

import cv2
import numpy as np
import pandas as pd
import os
import json
import base64
import sys
from io import BytesIO


# =============================================================================
# IMAGE LOADING & PREPROCESSING
# =============================================================================

def load_image(image_path):
    """
    Load and validate a satellite image from disk.
    
    Args:
        image_path (str): Path to the satellite image file.
        
    Returns:
        numpy.ndarray: The loaded BGR image.
        
    Raises:
        FileNotFoundError: If the image file does not exist.
        ValueError: If the image cannot be decoded by OpenCV.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Unable to decode image: {image_path}")
    
    return image


def preprocess_image(image, max_dimension=1200):
    """
    Preprocess the image: resize if too large and apply light Gaussian blur
    to reduce noise while preserving vegetation features.
    
    Args:
        image (numpy.ndarray): Input BGR image.
        max_dimension (int): Maximum width or height. Image is resized
            proportionally if either dimension exceeds this value.
            
    Returns:
        numpy.ndarray: Preprocessed BGR image.
    """
    h, w = image.shape[:2]
    if max(h, w) > max_dimension:
        scale = max_dimension / max(h, w)
        image = cv2.resize(image, (int(w * scale), int(h * scale)),
                           interpolation=cv2.INTER_AREA)
    
    # Light Gaussian blur to reduce noise
    image = cv2.GaussianBlur(image, (3, 3), 0)
    return image


# =============================================================================
# VEGETATION DETECTION METHODS
# =============================================================================

def detect_hsv(image, lower_hsv=None, upper_hsv=None):
    """
    Detect vegetation using HSV color space thresholding.
    
    Vegetation typically appears in the green hue range (25-85) with
    moderate to high saturation and value. This method converts the
    image to HSV and creates a binary mask of pixels within the
    specified range.
    
    Args:
        image (numpy.ndarray): Input BGR image.
        lower_hsv (tuple): Lower HSV bound as (H, S, V). 
            Defaults to (25, 30, 30).
        upper_hsv (tuple): Upper HSV bound as (H, S, V).
            Defaults to (95, 255, 255).
            
    Returns:
        numpy.ndarray: Binary mask (0 or 255) where 255 = vegetation.
    """
    if lower_hsv is None:
        lower_hsv = (25, 30, 30)
    if upper_hsv is None:
        upper_hsv = (95, 255, 255)
    
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(lower_hsv), np.array(upper_hsv))
    
    # Morphological operations to clean up noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    return mask


def detect_exg(image, threshold=20):
    """
    Detect vegetation using the Excess Green Index (ExG).
    
    Formula: ExG = 2*G - R - B
    
    This index highlights pixels where the green channel significantly
    exceeds the red and blue channels, which is characteristic of
    healthy vegetation.
    
    Args:
        image (numpy.ndarray): Input BGR image.
        threshold (float): Minimum ExG value to classify as vegetation.
            Defaults to 20.
            
    Returns:
        numpy.ndarray: Binary mask (0 or 255) where 255 = vegetation.
    """
    b, g, r = cv2.split(image.astype(np.float64))
    exg = 2.0 * g - r - b
    
    mask = np.zeros_like(exg, dtype=np.uint8)
    mask[exg > threshold] = 255
    
    # Clean up
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    return mask


def detect_exgr(image, threshold=10):
    """
    Detect vegetation using Excess Green minus Excess Red (ExGR).
    
    Formula: ExGR = ExG - ExR = (2*G - R - B) - (1.4*R - G)
                  = 3*G - 2.4*R - B
    
    This index provides better separation of vegetation from soil
    compared to ExG alone, as it penalizes red-heavy pixels.
    
    Args:
        image (numpy.ndarray): Input BGR image.
        threshold (float): Minimum ExGR value to classify as vegetation.
            Defaults to 10.
            
    Returns:
        numpy.ndarray: Binary mask (0 or 255) where 255 = vegetation.
    """
    b, g, r = cv2.split(image.astype(np.float64))
    exgr = 3.0 * g - 2.4 * r - b
    
    mask = np.zeros_like(exgr, dtype=np.uint8)
    mask[exgr > threshold] = 255
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    return mask


def detect_vari(image, threshold=0.05):
    """
    Detect vegetation using the Visible Atmospherically Resistant Index (VARI).
    
    Formula: VARI = (G - R) / (G + R - B)
    
    VARI is designed to be more robust to atmospheric effects and
    lighting variation than simple color thresholding.
    
    Args:
        image (numpy.ndarray): Input BGR image.
        threshold (float): Minimum VARI value to classify as vegetation.
            Defaults to 0.05.
            
    Returns:
        numpy.ndarray: Binary mask (0 or 255) where 255 = vegetation.
    """
    b, g, r = cv2.split(image.astype(np.float64))
    
    denominator = g + r - b
    # Avoid division by zero
    denominator[denominator == 0] = 0.001
    
    vari = (g - r) / denominator
    
    mask = np.zeros_like(vari, dtype=np.uint8)
    mask[vari > threshold] = 255
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    return mask


def detect_gli(image, threshold=0.02):
    """
    Detect vegetation using the Green Leaf Index (GLI).
    
    Formula: GLI = (2*G - R - B) / (2*G + R + B)
    
    GLI normalizes the Excess Green Index, making it less sensitive
    to overall brightness changes and useful for leaf area estimation.
    
    Args:
        image (numpy.ndarray): Input BGR image.
        threshold (float): Minimum GLI value to classify as vegetation.
            Defaults to 0.02.
            
    Returns:
        numpy.ndarray: Binary mask (0 or 255) where 255 = vegetation.
    """
    b, g, r = cv2.split(image.astype(np.float64))
    
    numerator = 2.0 * g - r - b
    denominator = 2.0 * g + r + b
    denominator[denominator == 0] = 0.001
    
    gli = numerator / denominator
    
    mask = np.zeros_like(gli, dtype=np.uint8)
    mask[gli > threshold] = 255
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    return mask


def detect_sobel(image, threshold_value=100):
    """
    Detect edges using Sobel operator (baseline method).
    
    This method detects edges/boundaries rather than vegetation directly.
    Retained for comparison purposes to demonstrate the improvement
    of color-based methods over edge-based detection.
    
    Args:
        image (numpy.ndarray): Input BGR image.
        threshold_value (float): Gradient magnitude threshold.
            Defaults to 100.
            
    Returns:
        numpy.ndarray: Binary mask (0 or 255) where 255 = edge pixel.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = cv2.magnitude(sobel_x, sobel_y)
    
    _, mask = cv2.threshold(gradient_magnitude, threshold_value, 255,
                            cv2.THRESH_BINARY)
    
    return mask.astype(np.uint8)


# =============================================================================
# ANALYSIS & STATISTICS
# =============================================================================

def compute_statistics(mask, image_shape):
    """
    Compute vegetation coverage statistics from a binary mask.
    
    Args:
        mask (numpy.ndarray): Binary mask (0 or 255).
        image_shape (tuple): Shape of the original image (H, W, C).
        
    Returns:
        dict: Statistics including pixel counts, coverage percentage,
              and estimated area.
    """
    total_pixels = mask.shape[0] * mask.shape[1]
    vegetation_pixels = int(np.count_nonzero(mask))
    non_vegetation_pixels = total_pixels - vegetation_pixels
    coverage_pct = round((vegetation_pixels / total_pixels) * 100, 2)
    
    return {
        "total_pixels": total_pixels,
        "vegetation_pixels": vegetation_pixels,
        "non_vegetation_pixels": non_vegetation_pixels,
        "coverage_percentage": coverage_pct,
        "image_width": image_shape[1],
        "image_height": image_shape[0],
    }


def compute_density_heatmap(mask, grid_size=20):
    """
    Divide the image into a grid and compute vegetation density per cell.
    
    Args:
        mask (numpy.ndarray): Binary vegetation mask.
        grid_size (int): Number of grid divisions along each axis.
            Defaults to 20.
            
    Returns:
        numpy.ndarray: 2D array of density values (0.0 to 1.0) for each cell.
        list: List of dicts with per-cell statistics for CSV export.
    """
    h, w = mask.shape
    cell_h = h // grid_size
    cell_w = w // grid_size
    
    density_map = np.zeros((grid_size, grid_size), dtype=np.float64)
    cell_data = []
    
    for row in range(grid_size):
        for col in range(grid_size):
            y_start = row * cell_h
            y_end = (row + 1) * cell_h if row < grid_size - 1 else h
            x_start = col * cell_w
            x_end = (col + 1) * cell_w if col < grid_size - 1 else w
            
            cell = mask[y_start:y_end, x_start:x_end]
            cell_total = cell.shape[0] * cell.shape[1]
            cell_veg = int(np.count_nonzero(cell))
            density = cell_veg / cell_total if cell_total > 0 else 0
            
            density_map[row, col] = density
            cell_data.append({
                "grid_row": row,
                "grid_col": col,
                "y_start": y_start,
                "y_end": y_end,
                "x_start": x_start,
                "x_end": x_end,
                "vegetation_pixels": cell_veg,
                "total_pixels": cell_total,
                "density": round(density, 4),
            })
    
    return density_map, cell_data


def create_overlay(image, mask, color=(0, 255, 0), alpha=0.4):
    """
    Create a semi-transparent colored overlay on the original image
    highlighting detected vegetation.
    
    Args:
        image (numpy.ndarray): Original BGR image.
        mask (numpy.ndarray): Binary vegetation mask.
        color (tuple): BGR color for the overlay. Defaults to green.
        alpha (float): Overlay transparency (0=invisible, 1=opaque).
            Defaults to 0.4.
            
    Returns:
        numpy.ndarray: Image with colored overlay on vegetation areas.
    """
    overlay = image.copy()
    overlay[mask == 255] = color
    result = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
    return result


def create_density_visualization(image, density_map, grid_size=20):
    """
    Create a color-coded density heatmap overlay on the original image.
    
    Uses a color gradient from red (no vegetation) through yellow 
    (sparse) to green (dense vegetation).
    
    Args:
        image (numpy.ndarray): Original BGR image.
        density_map (numpy.ndarray): 2D density values (0-1).
        grid_size (int): Number of grid divisions.
        
    Returns:
        numpy.ndarray: Image with density heatmap overlay.
    """
    h, w = image.shape[:2]
    heatmap = np.zeros((h, w), dtype=np.float64)
    
    cell_h = h // grid_size
    cell_w = w // grid_size
    
    for row in range(grid_size):
        for col in range(grid_size):
            y_start = row * cell_h
            y_end = (row + 1) * cell_h if row < grid_size - 1 else h
            x_start = col * cell_w
            x_end = (col + 1) * cell_w if col < grid_size - 1 else w
            heatmap[y_start:y_end, x_start:x_end] = density_map[row, col]
    
    # Scale to 0-255 and apply colormap
    heatmap_uint8 = (heatmap * 255).astype(np.uint8)
    colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
    
    # Blend with original
    result = cv2.addWeighted(colored, 0.5, image, 0.5, 0)
    return result


# =============================================================================
# COMPARISON ANALYSIS
# =============================================================================

def run_all_methods(image):
    """
    Run all vegetation detection methods on the given image and return
    their masks and statistics.
    
    Args:
        image (numpy.ndarray): Input BGR image.
        
    Returns:
        dict: Mapping of method name to a dict containing 'mask',
              'stats', and 'overlay'.
    """
    methods = {
        "HSV Segmentation": detect_hsv,
        "Excess Green (ExG)": detect_exg,
        "Excess Green-Red (ExGR)": detect_exgr,
        "VARI": detect_vari,
        "Green Leaf Index (GLI)": detect_gli,
        "Sobel Edge (Original)": detect_sobel,
    }
    
    results = {}
    for name, func in methods.items():
        mask = func(image)
        stats = compute_statistics(mask, image.shape)
        overlay = create_overlay(image, mask)
        results[name] = {
            "mask": mask,
            "stats": stats,
            "overlay": overlay,
        }
    
    return results


# =============================================================================
# EXTENDED ANALYSIS MODULES (PHASE 1)
# =============================================================================

def calculate_real_world_area(pixel_count, total_pixels=None, gsd_meters=1.0):
    """
    Convert raw pixel counts into real-world geographic area units based on
    the Ground Sampling Distance (GSD) in meters per pixel.
    
    Args:
        pixel_count (int): Number of detected pixels.
        total_pixels (int, optional): Total pixels in the scene for relative calculations.
        gsd_meters (float): Ground Sampling Distance in meters/pixel.
            Examples:
                - Sentinel-2 Satellite: 10.0 m/px
                - PlanetScope Satellite: 3.0 m/px
                - Aerial / Drone: 0.1 - 0.5 m/px
                - Landsat-8: 30.0 m/px
                
    Returns:
        dict: Real-world area measurements in m², hectares (ha), km², and acres.
    """
    pixel_area_m2 = float(gsd_meters ** 2)
    area_m2 = float(pixel_count) * pixel_area_m2
    area_ha = area_m2 / 10000.0
    area_sqkm = area_m2 / 1000000.0
    area_acres = area_m2 * 0.000247105
    
    result = {
        "gsd_meters": float(gsd_meters),
        "pixel_area_m2": round(pixel_area_m2, 4),
        "vegetation_pixels": int(pixel_count),
        "area_sq_meters": round(area_m2, 2),
        "area_hectares": round(area_ha, 4),
        "area_sq_km": round(area_sqkm, 6),
        "area_acres": round(area_acres, 4),
    }
    
    if total_pixels is not None and total_pixels > 0:
        total_m2 = float(total_pixels) * pixel_area_m2
        result["total_scene_sq_meters"] = round(total_m2, 2)
        result["total_scene_hectares"] = round(total_m2 / 10000.0, 4)
        result["total_scene_sq_km"] = round(total_m2 / 1000000.0, 6)
        result["total_scene_acres"] = round(total_m2 * 0.000247105, 4)
        result["coverage_percentage"] = round((pixel_count / total_pixels) * 100.0, 2)
        
    return result


def analyze_patches_and_fragmentation(mask, min_patch_area=25, top_k=10):
    """
    Perform connected component analysis to evaluate canopy continuity,
    fragmentation, and discrete forest patch distributions.
    
    Args:
        mask (numpy.ndarray): Binary vegetation mask (0 or 255).
        min_patch_area (int): Minimum pixel area to consider as a valid patch.
        top_k (int): Number of top largest patches to highlight with bounding boxes.
        
    Returns:
        dict: Landscape ecology & fragmentation metrics.
        numpy.ndarray: Annotated visualization showing labeled bounding boxes on top patches.
    """
    binary = (mask > 0).astype(np.uint8)
    total_veg_pixels = int(np.count_nonzero(binary))
    total_scene_pixels = mask.shape[0] * mask.shape[1]
    
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        binary, connectivity=8
    )
    
    valid_patches = []
    for i in range(1, num_labels):  # Skip background (label 0)
        area = int(stats[i, cv2.CC_STAT_AREA])
        if area >= min_patch_area:
            valid_patches.append({
                "label": i,
                "area": area,
                "x": int(stats[i, cv2.CC_STAT_LEFT]),
                "y": int(stats[i, cv2.CC_STAT_TOP]),
                "width": int(stats[i, cv2.CC_STAT_WIDTH]),
                "height": int(stats[i, cv2.CC_STAT_HEIGHT]),
                "centroid_x": round(float(centroids[i][0]), 1),
                "centroid_y": round(float(centroids[i][1]), 1),
            })
            
    # Sort descending by patch area
    valid_patches.sort(key=lambda p: p["area"], reverse=True)
    patch_areas = [p["area"] for p in valid_patches]
    
    total_patches = len(valid_patches)
    largest_patch_area = patch_areas[0] if total_patches > 0 else 0
    largest_patch_pct = round((largest_patch_area / total_veg_pixels * 100.0), 2) if total_veg_pixels > 0 else 0.0
    mean_patch_area = round(float(np.mean(patch_areas)), 2) if total_patches > 0 else 0.0
    median_patch_area = round(float(np.median(patch_areas)), 2) if total_patches > 0 else 0.0
    std_patch_area = round(float(np.std(patch_areas)), 2) if total_patches > 0 else 0.0
    
    # Calculate perimeter to area ratio for fragmentation estimation
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    gradient = cv2.morphologyEx(binary, cv2.MORPH_GRADIENT, kernel)
    perimeter_pixels = int(np.count_nonzero(gradient))
    
    # Fragmentation Index: Perimeter / (2 * sqrt(pi * Area)) or normalized ratio
    fragmentation_ratio = round(perimeter_pixels / total_veg_pixels, 4) if total_veg_pixels > 0 else 0.0
    
    # Size class distribution
    small_patches = sum(1 for a in patch_areas if a < 100)
    medium_patches = sum(1 for a in patch_areas if 100 <= a <= 1000)
    large_patches = sum(1 for a in patch_areas if a > 1000)
    
    # Create annotated visualization
    annotated = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    # Give vegetation a nice emerald tint
    annotated[mask > 0] = [34, 139, 34]
    
    for rank, p in enumerate(valid_patches[:top_k], start=1):
        x, y, w, h = p["x"], p["y"], p["width"], p["height"]
        color = (0, 215, 255) if rank == 1 else (255, 191, 0)  # Gold for #1, Cyan for rest
        cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
        label_text = f"#{rank}: {p['area']}px"
        cv2.putText(
            annotated, label_text, (x, max(y - 6, 15)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA
        )
        
    metrics = {
        "total_patches": total_patches,
        "total_vegetation_pixels": total_veg_pixels,
        "largest_patch_pixels": largest_patch_area,
        "largest_patch_percentage": largest_patch_pct,
        "mean_patch_pixels": mean_patch_area,
        "median_patch_pixels": median_patch_area,
        "std_patch_pixels": std_patch_area,
        "perimeter_pixels": perimeter_pixels,
        "fragmentation_ratio": fragmentation_ratio,
        "distribution": {
            "small_under_100px": small_patches,
            "medium_100_to_1000px": medium_patches,
            "large_over_1000px": large_patches,
        },
        "top_patches": valid_patches[:top_k],
    }
    
    return metrics, annotated


def classify_vegetation_health(image, vegetation_mask=None):
    """
    Classify detected canopy into 3 physiological vigor tiers using
    spectral indices (Green Leaf Index & Excess Green):
      - Tier 1: High Vigor / Dense Canopy (High chlorophyll content)
      - Tier 2: Moderate Vigor / Grasslands & Shrubs
      - Tier 3: Stressed / Dry / Senescent (Drought or disease impacted)
      
    Args:
        image (numpy.ndarray): Input BGR image.
        vegetation_mask (numpy.ndarray, optional): Pre-computed binary mask.
            If None, computed automatically via HSV.
            
    Returns:
        dict: Health tier metrics, percentages, and health index score.
        numpy.ndarray: 3-Color annotated health visualization overlay.
        dict: Binary masks for tier1, tier2, and tier3.
    """
    if vegetation_mask is None:
        vegetation_mask = detect_hsv(image)
        
    veg_bool = vegetation_mask > 0
    total_scene_pixels = image.shape[0] * image.shape[1]
    total_veg_pixels = int(np.count_nonzero(veg_bool))
    
    if total_veg_pixels == 0:
        empty_mask = np.zeros_like(vegetation_mask)
        return {
            "total_vegetation_pixels": 0,
            "health_index_score": 0.0,
            "tier1_high_vigour": {"pixels": 0, "pct_of_veg": 0.0, "pct_of_scene": 0.0},
            "tier2_moderate": {"pixels": 0, "pct_of_veg": 0.0, "pct_of_scene": 0.0},
            "tier3_stressed": {"pixels": 0, "pct_of_veg": 0.0, "pct_of_scene": 0.0},
        }, image.copy(), {"tier1": empty_mask, "tier2": empty_mask, "tier3": empty_mask}
        
    b, g, r = cv2.split(image.astype(np.float64))
    
    # Calculate GLI
    num = 2.0 * g - r - b
    den = 2.0 * g + r + b
    den[den == 0] = 0.001
    gli = num / den
    
    # Tier thresholds
    tier1_bool = veg_bool & (gli >= 0.12)
    tier2_bool = veg_bool & (gli >= 0.02) & (gli < 0.12)
    tier3_bool = veg_bool & (gli < 0.02)
    
    t1_pixels = int(np.count_nonzero(tier1_bool))
    t2_pixels = int(np.count_nonzero(tier2_bool))
    t3_pixels = int(np.count_nonzero(tier3_bool))
    
    # Create binary sub-masks
    t1_mask = (tier1_bool * 255).astype(np.uint8)
    t2_mask = (tier2_bool * 255).astype(np.uint8)
    t3_mask = (tier3_bool * 255).astype(np.uint8)
    
    # Build 3-color visualization overlay
    # Tier 1 = Deep Emerald Green (34, 139, 34)
    # Tier 2 = Vibrant Lime Green (50, 205, 50)
    # Tier 3 = Amber/Gold (0, 165, 255)
    overlay = image.copy()
    overlay[tier1_bool] = [34, 139, 34]
    overlay[tier2_bool] = [50, 205, 50]
    overlay[tier3_bool] = [0, 165, 255]
    
    health_overlay = cv2.addWeighted(overlay, 0.65, image, 0.35, 0)
    
    # Calculate overall health score (0-100)
    health_score = round(
        ((t1_pixels * 100.0) + (t2_pixels * 60.0) + (t3_pixels * 20.0)) / total_veg_pixels,
        2
    )
    
    metrics = {
        "total_vegetation_pixels": total_veg_pixels,
        "health_index_score": health_score,
        "tier1_high_vigour": {
            "name": "High Vigour / Dense Canopy",
            "color_hex": "#228B22",
            "pixels": t1_pixels,
            "pct_of_veg": round((t1_pixels / total_veg_pixels) * 100.0, 2),
            "pct_of_scene": round((t1_pixels / total_scene_pixels) * 100.0, 2),
        },
        "tier2_moderate": {
            "name": "Moderate / Grassland & Shrubs",
            "color_hex": "#32CD32",
            "pixels": t2_pixels,
            "pct_of_veg": round((t2_pixels / total_veg_pixels) * 100.0, 2),
            "pct_of_scene": round((t2_pixels / total_scene_pixels) * 100.0, 2),
        },
        "tier3_stressed": {
            "name": "Stressed / Dry / Senescent",
            "color_hex": "#FFA500",
            "pixels": t3_pixels,
            "pct_of_veg": round((t3_pixels / total_veg_pixels) * 100.0, 2),
            "pct_of_scene": round((t3_pixels / total_scene_pixels) * 100.0, 2),
        },
    }
    
    return metrics, health_overlay, {"tier1": t1_mask, "tier2": t2_mask, "tier3": t3_mask}


def detect_temporal_change(image_before, image_after, method="hsv", gsd_meters=1.0):
    """
    Perform temporal change detection between two co-registered satellite images
    to track deforestation, vegetation loss, afforestation, and canopy dynamics.
    
    Args:
        image_before (numpy.ndarray): Baseline ("Before") satellite image.
        image_after (numpy.ndarray): Follow-up ("After") satellite image.
        method (str): Detection method to extract vegetation ('hsv', 'exg', 'vari', 'gli').
        gsd_meters (float): Ground Sampling Distance for area estimation.
        
    Returns:
        dict: Summary metrics including loss, gain, persistent canopy, and net delta.
        numpy.ndarray: Color-coded differential change map overlay.
        dict: Binary masks for loss, gain, and persistent vegetation.
    """
    # Align dimensions if images differ slightly
    h, w = image_before.shape[:2]
    if image_after.shape[:2] != (h, w):
        image_after = cv2.resize(image_after, (w, h), interpolation=cv2.INTER_AREA)
        
    method_dispatch = {
        "hsv": detect_hsv,
        "exg": detect_exg,
        "exgr": detect_exgr,
        "vari": detect_vari,
        "gli": detect_gli,
    }
    detector_func = method_dispatch.get(method.lower(), detect_hsv)
    
    mask_before = detector_func(image_before)
    mask_after = detector_func(image_after)
    
    b_bool = mask_before > 0
    a_bool = mask_after > 0
    
    # Differential classification
    loss_bool = b_bool & (~a_bool)         # Deforestation / Loss
    gain_bool = (~b_bool) & a_bool         # Afforestation / New Growth
    persist_bool = b_bool & a_bool        # Persistent Canopy
    nonveg_bool = (~b_bool) & (~a_bool)   # Persistent Non-Vegetation
    
    total_pixels = h * w
    before_veg = int(np.count_nonzero(b_bool))
    after_veg = int(np.count_nonzero(a_bool))
    loss_pixels = int(np.count_nonzero(loss_bool))
    gain_pixels = int(np.count_nonzero(gain_bool))
    persist_pixels = int(np.count_nonzero(persist_bool))
    
    before_pct = round((before_veg / total_pixels) * 100.0, 2)
    after_pct = round((after_veg / total_pixels) * 100.0, 2)
    net_change_pct = round(after_pct - before_pct, 2)
    
    # Calculate real-world areas
    area_scaler = float(gsd_meters ** 2)
    loss_ha = round((loss_pixels * area_scaler) / 10000.0, 4)
    gain_ha = round((gain_pixels * area_scaler) / 10000.0, 4)
    net_ha = round(((after_veg - before_veg) * area_scaler) / 10000.0, 4)
    
    # Status classification
    if net_change_pct < -5.0:
        status = "Significant Deforestation / Vegetation Loss"
        status_color = "#EF4444"
    elif net_change_pct < -1.0:
        status = "Moderate Vegetation Loss"
        status_color = "#F59E0B"
    elif net_change_pct > 5.0:
        status = "Significant Reforestation / Biomass Gain"
        status_color = "#10B981"
    elif net_change_pct > 1.0:
        status = "Moderate Vegetation Gain"
        status_color = "#34D399"
    else:
        status = "Canopy Equilibrium / Minimal Change"
        status_color = "#60A5FA"
        
    # Build visual differential change overlay
    # Background: Grayscale representation of 'after' image for spatial reference
    gray_after = cv2.cvtColor(image_after, cv2.COLOR_BGR2GRAY)
    diff_overlay = cv2.cvtColor(gray_after, cv2.COLOR_GRAY2BGR)
    diff_overlay = (diff_overlay * 0.7).astype(np.uint8)  # Dim slightly
    
    # Loss in Vibrant Red (BGR: 0, 0, 255)
    diff_overlay[loss_bool] = [0, 0, 235]
    # Gain in Vibrant Green (BGR: 0, 255, 0)
    diff_overlay[gain_bool] = [0, 235, 0]
    # Persistent in Forest Green (BGR: 34, 139, 34)
    diff_overlay[persist_bool] = [34, 139, 34]
    
    change_visualization = cv2.addWeighted(diff_overlay, 0.8, image_after, 0.2, 0)
    
    loss_mask = (loss_bool * 255).astype(np.uint8)
    gain_mask = (gain_bool * 255).astype(np.uint8)
    persist_mask = (persist_bool * 255).astype(np.uint8)
    
    metrics = {
        "status": status,
        "status_color": status_color,
        "net_change_percentage": net_change_pct,
        "net_change_hectares": net_ha,
        "before": {
            "vegetation_pixels": before_veg,
            "coverage_percentage": before_pct,
            "area_hectares": round((before_veg * area_scaler) / 10000.0, 4),
        },
        "after": {
            "vegetation_pixels": after_veg,
            "coverage_percentage": after_pct,
            "area_hectares": round((after_veg * area_scaler) / 10000.0, 4),
        },
        "breakdown": {
            "loss_deforestation": {
                "pixels": loss_pixels,
                "pct_of_scene": round((loss_pixels / total_pixels) * 100.0, 2),
                "area_hectares": loss_ha,
            },
            "gain_reforestation": {
                "pixels": gain_pixels,
                "pct_of_scene": round((gain_pixels / total_pixels) * 100.0, 2),
                "area_hectares": gain_ha,
            },
            "persistent_canopy": {
                "pixels": persist_pixels,
                "pct_of_scene": round((persist_pixels / total_pixels) * 100.0, 2),
                "area_hectares": round((persist_pixels * area_scaler) / 10000.0, 4),
            },
        }
    }
    
    return metrics, change_visualization, {
        "loss": loss_mask,
        "gain": gain_mask,
        "persist": persist_mask,
    }


def calculate_carbon_sequestration(area_hectares, biomass_factor=140.0, carbon_fraction=0.47):
    """
    Calculate estimated ecological biomass stock and CO2 sequestration based on
    standard IPCC Tier-1 forestry coefficients.
    
    Args:
        area_hectares (float): Total healthy vegetation canopy in hectares.
        biomass_factor (float): Aboveground biomass density in tons/hectare.
            Default: 140.0 t/ha (temperate/subtropical mixed forest).
        carbon_fraction (float): Carbon content fraction in dry biomass.
            Default: 0.47 (IPCC standard).
            
    Returns:
        dict: Biomass, carbon stock, CO2e sequestered, and offset equivalencies.
    """
    biomass_tons = float(area_hectares) * float(biomass_factor)
    carbon_stock_tons = biomass_tons * float(carbon_fraction)
    co2e_tons = carbon_stock_tons * (44.0 / 12.0)
    vehicles_offset = co2e_tons / 4.6  # EPA: 4.6 metric tons CO2/vehicle/year
    homes_powered = co2e_tons / 8.3    # EPA: 8.3 metric tons CO2/home electricity/year
    
    return {
        "canopy_hectares": round(float(area_hectares), 4),
        "aboveground_biomass_tons": round(biomass_tons, 2),
        "carbon_stock_tons": round(carbon_stock_tons, 2),
        "co2e_sequestered_tons": round(co2e_tons, 2),
        "passenger_vehicles_annual_offset": int(vehicles_offset),
        "homes_electricity_annual_offset": int(homes_powered),
    }


def simulate_color_infrared(image):
    """
    Generate a Color-Infrared (CIR False-Color) composite from standard RGB imagery
    using remote-sensing chromaticity transformations.
    
    In CIR imagery:
      - Vegetation exhibits intense chlorophyll reflectance and displays in Vivid Crimson / Red.
      - Bare soils and structures display in Gray / Cyan / Tan.
      - Water bodies absorb NIR and display in Deep Navy / Black.
      
    Args:
        image (numpy.ndarray): Input BGR image.
        
    Returns:
        numpy.ndarray: Synthesized Color-Infrared (CIR) BGR composite.
    """
    b, g, r = cv2.split(image.astype(np.float64))
    
    # Synthesize estimated NIR band from excess green and suppressed red
    nir_est = np.clip(2.2 * g - 0.6 * r, 0, 255)
    
    # CIR Composite mapping:
    # Red channel <- Estimated NIR (Vegetation lights up in Red)
    # Green channel <- Red band
    # Blue channel <- Green band
    cir_b = np.clip(g, 0, 255).astype(np.uint8)
    cir_g = np.clip(r, 0, 255).astype(np.uint8)
    cir_r = np.clip(nir_est, 0, 255).astype(np.uint8)
    
    cir_composite = cv2.merge([cir_b, cir_g, cir_r])
    return cir_composite


def analyze_quadrants(image, method="hsv", gsd_meters=10.0):
    """
    Divide the satellite scene into 5 spatial sub-sectors (Top-Left, Top-Right,
    Bottom-Left, Bottom-Right, and Center Core) and compute localized metrics.
    
    Args:
        image (numpy.ndarray): Input BGR image.
        method (str): Detection algorithm ('hsv', 'exg', 'vari', 'gli').
        gsd_meters (float): Ground Sampling Distance.
        
    Returns:
        dict: Sector metrics containing pixel counts, coverage %, and hectares per sector.
    """
    h, w = image.shape[:2]
    mid_y, mid_x = h // 2, w // 2
    q_y1, q_y2 = h // 4, 3 * h // 4
    q_x1, q_x2 = w // 4, 3 * w // 4
    
    method_dispatch = {
        "hsv": detect_hsv,
        "exg": detect_exg,
        "exgr": detect_exgr,
        "vari": detect_vari,
        "gli": detect_gli,
        "sobel": detect_sobel,
    }
    detector = method_dispatch.get(method.lower(), detect_hsv)
    
    sectors = {
        "top_left": {"name": "North-West (Top-Left)", "slice": (0, mid_y, 0, mid_x)},
        "top_right": {"name": "North-East (Top-Right)", "slice": (0, mid_y, mid_x, w)},
        "bottom_left": {"name": "South-West (Bottom-Left)", "slice": (mid_y, h, 0, mid_x)},
        "bottom_right": {"name": "South-East (Bottom-Right)", "slice": (mid_y, h, mid_x, w)},
        "center_core": {"name": "Central Core Zone", "slice": (q_y1, q_y2, q_x1, q_x2)},
    }
    
    results = {}
    area_scaler = float(gsd_meters ** 2)
    
    for key, info in sectors.items():
        y1, y2, x1, x2 = info["slice"]
        sub_img = image[y1:y2, x1:x2]
        sub_mask = detector(sub_img)
        
        tot_px = sub_mask.shape[0] * sub_mask.shape[1]
        veg_px = int(np.count_nonzero(sub_mask))
        cov_pct = round((veg_px / tot_px * 100.0), 2) if tot_px > 0 else 0.0
        ha = round((veg_px * area_scaler) / 10000.0, 4)
        
        results[key] = {
            "name": info["name"],
            "total_pixels": tot_px,
            "vegetation_pixels": veg_px,
            "coverage_percentage": cov_pct,
            "area_hectares": ha,
        }
        
    return results



# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

def image_to_base64(image, ext=".jpg"):
    """
    Encode an OpenCV image (BGR numpy array) to a base64 string
    suitable for embedding in HTML or JSON.
    
    Args:
        image (numpy.ndarray): BGR image.
        ext (str): Image format extension. Defaults to '.jpg'.
        
    Returns:
        str: Base64-encoded image string with data URI prefix.
    """
    _, buffer = cv2.imencode(ext, image)
    b64 = base64.b64encode(buffer).decode("utf-8")
    mime = "image/jpeg" if ext == ".jpg" else "image/png"
    return f"data:{mime};base64,{b64}"


def export_comparison_csv(results, output_path):
    """
    Export a comparison table of all detection methods to CSV.
    
    Args:
        results (dict): Output from run_all_methods().
        output_path (str): Path to save the CSV file.
    """
    rows = []
    for method_name, data in results.items():
        s = data["stats"]
        rows.append({
            "Method": method_name,
            "Vegetation Pixels": s["vegetation_pixels"],
            "Total Pixels": s["total_pixels"],
            "Coverage (%)": s["coverage_percentage"],
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    return df


def export_density_csv(cell_data, output_path):
    """
    Export per-grid-cell vegetation density data to CSV.
    
    Args:
        cell_data (list): List of dicts from compute_density_heatmap().
        output_path (str): Path to save the CSV file.
    """
    df = pd.DataFrame(cell_data)
    df.to_csv(output_path, index=False)
    return df


# =============================================================================
# MAIN EXECUTION (CLI MODE)
# =============================================================================

def main():
    """
    Command-line interface for vegetation detection.
    Processes the satellite image, runs all methods, generates outputs.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Vegetation Detection in Satellite Images using OpenCV"
    )
    parser.add_argument(
        "--image", "-i",
        default="satellite_image.jpg",
        help="Path to the satellite image (default: satellite_image.jpg)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="output",
        help="Directory for output files (default: output)"
    )
    parser.add_argument(
        "--grid-size", "-g",
        type=int, default=20,
        help="Grid size for density heatmap (default: 20)"
    )
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print("=" * 60)
    print("Vegetation Detection in Satellite Images (OpenCV Engine)")
    print("=" * 60)
    
    # Load and preprocess
    print(f"\n[1/5] Loading image: {args.image}")
    image = load_image(args.image)
    image = preprocess_image(image)
    print(f"      Image size: {image.shape[1]}x{image.shape[0]} pixels")
    
    # Run all detection methods
    print("\n[2/5] Running vegetation detection methods...")
    results = run_all_methods(image)
    
    for name, data in results.items():
        s = data["stats"]
        print(f"      {name:30s} -> {s['coverage_percentage']:6.2f}% coverage")
    
    # Generate density heatmap (using best method: HSV)
    print(f"\n[3/5] Computing density heatmap (grid: {args.grid_size}x{args.grid_size})...")
    hsv_mask = results["HSV Segmentation"]["mask"]
    density_map, cell_data = compute_density_heatmap(hsv_mask, args.grid_size)
    density_viz = create_density_visualization(image, density_map, args.grid_size)
    
    # Save output images
    print(f"\n[4/5] Saving results to {args.output_dir}/...")
    cv2.imwrite(os.path.join(args.output_dir, "original.jpg"), image)
    for name, data in results.items():
        safe_name = name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        cv2.imwrite(
            os.path.join(args.output_dir, f"mask_{safe_name}.jpg"), data["mask"]
        )
        cv2.imwrite(
            os.path.join(args.output_dir, f"overlay_{safe_name}.jpg"),
            data["overlay"]
        )
    cv2.imwrite(os.path.join(args.output_dir, "density_heatmap.jpg"), density_viz)
    
    # Export CSV data
    print("\n[5/5] Exporting data to CSV...")
    comparison_df = export_comparison_csv(
        results, os.path.join(args.output_dir, "method_comparison.csv")
    )
    density_df = export_density_csv(
        cell_data, os.path.join(args.output_dir, "density_data.csv")
    )
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(comparison_df.to_string(index=False))
    print(f"\nAverage vegetation density: {density_map.mean():.2%}")
    print(f"Max cell density:          {density_map.max():.2%}")
    print(f"Min cell density:          {density_map.min():.2%}")
    print(f"\nAll outputs saved to: {os.path.abspath(args.output_dir)}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
