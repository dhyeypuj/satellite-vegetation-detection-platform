"""
Vegetation Detection Platform - Flask Server (v2.1)

Interactive web interface for vegetation detection in satellite images.
Provides real-time threshold adjustment, method comparison, density heatmap,
3-tier vegetation health assessment, landscape fragmentation & patch analysis,
real-world GSD area scaling, temporal change (deforestation) tracking,
Color-Infrared (CIR) false-color simulation, carbon biomass sequestration,
sub-quadrant ROI sector analysis, and one-click ZIP packaging.
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
import os
import sys
import io
import tempfile
import zipfile
import cv2
import numpy as np
import pandas as pd
import json

# Import our vegetation detection module
from vegetation_detector import (
    load_image, preprocess_image,
    detect_hsv, detect_exg, detect_exgr, detect_vari, detect_gli, detect_sobel,
    compute_statistics, compute_density_heatmap,
    create_overlay, create_density_visualization,
    calculate_real_world_area, analyze_patches_and_fragmentation,
    classify_vegetation_health, detect_temporal_change,
    calculate_carbon_sequestration, simulate_color_infrared, analyze_quadrants,
    image_to_base64, run_all_methods
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))

# Store the current loaded image in memory
current_image = None
current_image_path = None

# Store temporal change images in memory
current_before_image = None
current_after_image = None


def get_active_image():
    """Retrieve active loaded image or fallback to default benchmark image."""
    global current_image, current_image_path
    if current_image is not None:
        return current_image
        
    default_path = os.path.join(BASE_DIR, "satellite_image.jpg")
    if os.path.exists(default_path):
        current_image = preprocess_image(load_image(default_path))
        current_image_path = default_path
        return current_image
    return None


@app.route("/")
def index():
    """Serve the main dashboard HTML page."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/static/<path:filename>")
def serve_static(filename):
    """Serve static files (CSS, JS)."""
    return send_from_directory(app.static_folder, filename)


@app.route("/api/upload", methods=["POST"])
def upload_image():
    """
    Upload a satellite image for processing.
    Accepts multipart/form-data with an 'image' field.
    Returns the original image as base64 and basic metadata.
    """
    global current_image, current_image_path
    
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    upload_dir = os.path.join(tempfile.gettempdir(), "satellite_uploads")
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, "uploaded_image.jpg")
    file.save(filepath)
    
    try:
        current_image = load_image(filepath)
        current_image = preprocess_image(current_image, max_dimension=1200)
        current_image_path = filepath
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    return jsonify({
        "success": True,
        "original": image_to_base64(current_image),
        "width": current_image.shape[1],
        "height": current_image.shape[0],
    })


@app.route("/api/load-default", methods=["POST"])
def load_default():
    """Load the default satellite_image.jpg from the project directory."""
    global current_image, current_image_path
    
    default_path = os.path.join(os.path.dirname(__file__), "satellite_image.jpg")
    if not os.path.exists(default_path):
        return jsonify({"error": "Default image not found. Please upload an image."}), 404
    
    try:
        current_image = load_image(default_path)
        current_image = preprocess_image(current_image, max_dimension=1200)
        current_image_path = default_path
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    return jsonify({
        "success": True,
        "original": image_to_base64(current_image),
        "width": current_image.shape[1],
        "height": current_image.shape[0],
    })


@app.route("/api/detect", methods=["POST"])
def detect():
    """
    Run a specific vegetation detection method with custom parameters.
    Returns mask, overlay, statistics, area metrics, and carbon sequestration.
    """
    img = get_active_image()
    if img is None:
        return jsonify({"error": "No image loaded. Upload or load default first."}), 400
    
    data = request.get_json() or {}
    method = data.get("method", "hsv")
    params = data.get("params", {})
    gsd_meters = float(data.get("gsd_meters", 10.0))
    
    try:
        if method == "hsv":
            lower = (
                int(params.get("h_low", 25)),
                int(params.get("s_low", 30)),
                int(params.get("v_low", 30)),
            )
            upper = (
                int(params.get("h_high", 95)),
                int(params.get("s_high", 255)),
                int(params.get("v_high", 255)),
            )
            mask = detect_hsv(img, lower, upper)
        elif method == "exg":
            mask = detect_exg(img, float(params.get("threshold", 20)))
        elif method == "exgr":
            mask = detect_exgr(img, float(params.get("threshold", 10)))
        elif method == "vari":
            mask = detect_vari(img, float(params.get("threshold", 0.05)))
        elif method == "gli":
            mask = detect_gli(img, float(params.get("threshold", 0.02)))
        elif method == "sobel":
            mask = detect_sobel(img, float(params.get("threshold", 100)))
        else:
            return jsonify({"error": f"Unknown method: {method}"}), 400
        
        stats = compute_statistics(mask, img.shape)
        overlay = create_overlay(img, mask)
        area_metrics = calculate_real_world_area(
            stats["vegetation_pixels"], stats["total_pixels"], gsd_meters
        )
        carbon_metrics = calculate_carbon_sequestration(area_metrics["area_hectares"])
        
        return jsonify({
            "success": True,
            "mask": image_to_base64(mask),
            "overlay": image_to_base64(overlay),
            "stats": stats,
            "area_metrics": area_metrics,
            "carbon_metrics": carbon_metrics,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cir", methods=["POST"])
def cir_composite():
    """
    Generate and return a Color-Infrared (CIR False-Color) composite.
    """
    img = get_active_image()
    if img is None:
        return jsonify({"error": "No image loaded."}), 400
        
    try:
        cir = simulate_color_infrared(img)
        return jsonify({
            "success": True,
            "cir": image_to_base64(cir),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/quadrants", methods=["POST"])
def quadrant_analysis():
    """
    Compute localized sector / quadrant metrics.
    """
    img = get_active_image()
    if img is None:
        return jsonify({"error": "No image loaded."}), 400
        
    data = request.get_json() or {}
    method = data.get("method", "hsv")
    gsd_meters = float(data.get("gsd_meters", 10.0))
    
    try:
        results = analyze_quadrants(img, method, gsd_meters)
        return jsonify({
            "success": True,
            "sectors": results,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/carbon", methods=["POST"])
def carbon_sequestration():
    """
    Calculate carbon stock and CO2 sequestration for user-specified canopy hectares.
    """
    data = request.get_json() or {}
    hectares = float(data.get("hectares", 0.0))
    
    try:
        result = calculate_carbon_sequestration(hectares)
        return jsonify({"success": True, "carbon": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/compare", methods=["POST"])
def compare():
    """Run all vegetation detection methods and return a comparison."""
    global current_image
    
    if current_image is None:
        return jsonify({"error": "No image loaded."}), 400
    
    try:
        results = run_all_methods(current_image)
        
        response = {"success": True, "methods": {}}
        for name, data in results.items():
            response["methods"][name] = {
                "mask": image_to_base64(data["mask"]),
                "overlay": image_to_base64(data["overlay"]),
                "stats": data["stats"],
            }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/density", methods=["POST"])
def density():
    """Compute and return a vegetation density heatmap."""
    global current_image
    
    if current_image is None:
        return jsonify({"error": "No image loaded."}), 400
    
    data = request.get_json() or {}
    method = data.get("method", "hsv")
    grid_size = int(data.get("grid_size", 20))
    
    try:
        if method == "hsv":
            mask = detect_hsv(current_image)
        elif method == "exg":
            mask = detect_exg(current_image)
        elif method == "vari":
            mask = detect_vari(current_image)
        elif method == "gli":
            mask = detect_gli(current_image)
        else:
            mask = detect_hsv(current_image)
        
        density_map, cell_data = compute_density_heatmap(mask, grid_size)
        density_viz = create_density_visualization(
            current_image, density_map, grid_size
        )
        
        return jsonify({
            "success": True,
            "heatmap": image_to_base64(density_viz),
            "grid_size": grid_size,
            "avg_density": round(float(density_map.mean()) * 100, 2),
            "max_density": round(float(density_map.max()) * 100, 2),
            "min_density": round(float(density_map.min()) * 100, 2),
            "cell_data": cell_data,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["POST"])
def health_classification():
    """Classify vegetation into 3 physiological vigor tiers."""
    global current_image
    
    if current_image is None:
        return jsonify({"error": "No image loaded."}), 400
    
    try:
        metrics, overlay, masks = classify_vegetation_health(current_image)
        
        return jsonify({
            "success": True,
            "metrics": metrics,
            "overlay": image_to_base64(overlay),
            "tier1_mask": image_to_base64(masks["tier1"]),
            "tier2_mask": image_to_base64(masks["tier2"]),
            "tier3_mask": image_to_base64(masks["tier3"]),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/patches", methods=["POST"])
def patch_analysis():
    """Analyze landscape canopy patch distribution and fragmentation."""
    global current_image
    
    if current_image is None:
        return jsonify({"error": "No image loaded."}), 400
    
    data = request.get_json() or {}
    method = data.get("method", "hsv")
    min_patch_area = int(data.get("min_patch_area", 25))
    
    try:
        if method == "exg":
            mask = detect_exg(current_image)
        elif method == "vari":
            mask = detect_vari(current_image)
        elif method == "gli":
            mask = detect_gli(current_image)
        else:
            mask = detect_hsv(current_image)
            
        metrics, annotated = analyze_patches_and_fragmentation(
            mask, min_patch_area=min_patch_area
        )
        
        return jsonify({
            "success": True,
            "metrics": metrics,
            "annotated": image_to_base64(annotated),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/area_scale", methods=["POST"])
def area_scale():
    """Recalculate real-world geographic area for user-specified GSD."""
    data = request.get_json() or {}
    pixel_count = int(data.get("pixel_count", 0))
    total_pixels = int(data.get("total_pixels", 0))
    gsd_meters = float(data.get("gsd_meters", 10.0))
    
    try:
        result = calculate_real_world_area(pixel_count, total_pixels, gsd_meters)
        carbon = calculate_carbon_sequestration(result["area_hectares"])
        return jsonify({"success": True, "area_metrics": result, "carbon_metrics": carbon})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/temporal_sample", methods=["GET", "POST"])
def load_temporal_sample():
    """Load default Before & After satellite images."""
    global current_before_image, current_after_image
    
    before_path = os.path.join(os.path.dirname(__file__), "satellite_image_before.jpg")
    after_path = os.path.join(os.path.dirname(__file__), "satellite_image_after.jpg")
    
    if not os.path.exists(before_path) or not os.path.exists(after_path):
        return jsonify({"error": "Temporal sample images not found."}), 404
        
    try:
        current_before_image = preprocess_image(load_image(before_path))
        current_after_image = preprocess_image(load_image(after_path))
        
        return jsonify({
            "success": True,
            "before": image_to_base64(current_before_image),
            "after": image_to_base64(current_after_image),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/temporal_change", methods=["POST"])
def temporal_change():
    """Compute deforestation / afforestation change between Before & After images."""
    global current_before_image, current_after_image
    
    method = "hsv"
    gsd_meters = 10.0
    
    if request.is_json:
        data = request.get_json() or {}
        method = data.get("method", "hsv")
        gsd_meters = float(data.get("gsd_meters", 10.0))
        use_sample = data.get("use_sample", False)
        
        if use_sample or (current_before_image is not None and current_after_image is not None):
            if current_before_image is None or current_after_image is None:
                before_path = os.path.join(os.path.dirname(__file__), "satellite_image_before.jpg")
                after_path = os.path.join(os.path.dirname(__file__), "satellite_image_after.jpg")
                current_before_image = preprocess_image(load_image(before_path))
                current_after_image = preprocess_image(load_image(after_path))
    else:
        method = request.form.get("method", "hsv")
        gsd_meters = float(request.form.get("gsd_meters", 10.0))
        
        upload_dir = os.path.join(tempfile.gettempdir(), "satellite_uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        if "image_before" in request.files and request.files["image_before"].filename != "":
            b_file = request.files["image_before"]
            b_path = os.path.join(upload_dir, "before.jpg")
            b_file.save(b_path)
            current_before_image = preprocess_image(load_image(b_path))
            
        if "image_after" in request.files and request.files["image_after"].filename != "":
            a_file = request.files["image_after"]
            a_path = os.path.join(upload_dir, "after.jpg")
            a_file.save(a_path)
            current_after_image = preprocess_image(load_image(a_path))
            
    if current_before_image is None or current_after_image is None:
        return jsonify({"error": "Both 'Before' and 'After' images must be uploaded or loaded."}), 400
        
    try:
        metrics, change_viz, masks = detect_temporal_change(
            current_before_image, current_after_image, method, gsd_meters
        )
        
        return jsonify({
            "success": True,
            "metrics": metrics,
            "visualization": image_to_base64(change_viz),
            "loss_mask": image_to_base64(masks["loss"]),
            "gain_mask": image_to_base64(masks["gain"]),
            "persist_mask": image_to_base64(masks["persist"]),
            "before_image": image_to_base64(current_before_image),
            "after_image": image_to_base64(current_after_image),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/full_report", methods=["GET", "POST"])
def full_report():
    """Compile diagnostic audit payload."""
    global current_image
    
    if current_image is None:
        default_path = os.path.join(os.path.dirname(__file__), "satellite_image.jpg")
        if os.path.exists(default_path):
            current_image = preprocess_image(load_image(default_path))
        else:
            return jsonify({"error": "No image loaded."}), 400
            
    try:
        comp_results = run_all_methods(current_image)
        comp_summary = {}
        for name, d in comp_results.items():
            comp_summary[name] = d["stats"]
            
        health_metrics, _, _ = classify_vegetation_health(current_image)
        hsv_mask = detect_hsv(current_image)
        patch_metrics, _ = analyze_patches_and_fragmentation(hsv_mask)
        
        stats = comp_summary["HSV Segmentation"]
        scales = {
            "sentinel2_10m": calculate_real_world_area(stats["vegetation_pixels"], stats["total_pixels"], 10.0),
            "planetscope_3m": calculate_real_world_area(stats["vegetation_pixels"], stats["total_pixels"], 3.0),
            "drone_05m": calculate_real_world_area(stats["vegetation_pixels"], stats["total_pixels"], 0.5),
        }
        carbon = calculate_carbon_sequestration(scales["sentinel2_10m"]["area_hectares"])
        quadrants = analyze_quadrants(current_image, "hsv", 10.0)
        
        return jsonify({
            "success": True,
            "image_dimensions": {"width": current_image.shape[1], "height": current_image.shape[0]},
            "comparison": comp_summary,
            "health": health_metrics,
            "patches": patch_metrics,
            "scales": scales,
            "carbon": carbon,
            "quadrants": quadrants,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/export_zip", methods=["GET"])
def export_zip_bundle():
    """
    Compile all generated masks, overlays, CIR composite, density map,
    and CSV metrics into a downloadable ZIP archive.
    """
    global current_image
    
    if current_image is None:
        default_path = os.path.join(os.path.dirname(__file__), "satellite_image.jpg")
        if os.path.exists(default_path):
            current_image = preprocess_image(load_image(default_path))
        else:
            return jsonify({"error": "No image loaded."}), 400
            
    try:
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # 1. Original image
            _, img_buf = cv2.imencode(".jpg", current_image)
            zf.writestr("01_original_satellite.jpg", img_buf.tobytes())
            
            # 2. CIR False-Color
            cir = simulate_color_infrared(current_image)
            _, cir_buf = cv2.imencode(".jpg", cir)
            zf.writestr("02_color_infrared_composite.jpg", cir_buf.tobytes())
            
            # 3. All 6 Methods
            results = run_all_methods(current_image)
            csv_rows = []
            
            for name, data in results.items():
                safe_name = name.lower().replace(" ", "_").replace("(", "").replace(")", "")
                _, m_buf = cv2.imencode(".png", data["mask"])
                _, o_buf = cv2.imencode(".jpg", data["overlay"])
                zf.writestr(f"masks/mask_{safe_name}.png", m_buf.tobytes())
                zf.writestr(f"overlays/overlay_{safe_name}.jpg", o_buf.tobytes())
                
                s = data["stats"]
                csv_rows.append({
                    "Method": name,
                    "Vegetation Pixels": s["vegetation_pixels"],
                    "Total Pixels": s["total_pixels"],
                    "Coverage (%)": s["coverage_percentage"],
                })
                
            # CSV comparison
            df_comp = pd.DataFrame(csv_rows)
            zf.writestr("method_comparison.csv", df_comp.to_csv(index=False))
            
            # 4. Density Heatmap
            hsv_mask = results["HSV Segmentation"]["mask"]
            density_map, cell_data = compute_density_heatmap(hsv_mask, 20)
            density_viz = create_density_visualization(current_image, density_map, 20)
            _, dens_buf = cv2.imencode(".jpg", density_viz)
            zf.writestr("03_density_heatmap.jpg", dens_buf.tobytes())
            df_dens = pd.DataFrame(cell_data)
            zf.writestr("density_cell_data.csv", df_dens.to_csv(index=False))
            
            # 5. Health overlay
            _, health_viz, _ = classify_vegetation_health(current_image, hsv_mask)
            _, h_buf = cv2.imencode(".jpg", health_viz)
            zf.writestr("04_canopy_health_classification.jpg", h_buf.tobytes())
            
            # 6. Patch fragmentation annotated
            _, patch_viz = analyze_patches_and_fragmentation(hsv_mask)
            _, p_buf = cv2.imencode(".jpg", patch_viz)
            zf.writestr("05_patch_clusters_annotated.jpg", p_buf.tobytes())
            
            # 7. Summary Readme in ZIP
            readme_txt = f"""Vegetation Remote Sensing Analysis Package
================================================
Scene Size: {current_image.shape[1]}x{current_image.shape[0]} px
Generated by Vegetation Detection Platform (v2.1).
Contains all 6 spectral masks, overlays, CIR composite, density maps, and CSVs.
"""
            zf.writestr("PACKAGE_INFO.txt", readme_txt)
            
        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name="Vegetation_Analysis_Package.zip"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("=" * 60)
    print("  Vegetation Detection Platform (v2.1)")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 60)
    app.run(debug=True, port=5000)
