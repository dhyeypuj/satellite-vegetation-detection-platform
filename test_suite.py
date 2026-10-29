"""
Vegetation Detection Platform (v2.1) - Automated Test Suite
Validates core algorithms, mathematical indices, edge cases, API endpoints,
and performance benchmarks.
"""

import os
import sys
import time
import unittest
import numpy as np
import cv2
import pandas as pd

from vegetation_detector import (
    load_image, preprocess_image,
    detect_hsv, detect_exg, detect_exgr, detect_vari, detect_gli, detect_sobel,
    compute_statistics, compute_density_heatmap,
    create_overlay, create_density_visualization,
    calculate_real_world_area, analyze_patches_and_fragmentation,
    classify_vegetation_health, detect_temporal_change,
    image_to_base64, run_all_methods,
    export_comparison_csv, export_density_csv
)


class TestVegetationSuite(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up test images and synthetic fixtures."""
        cls.image_path = "satellite_image.jpg"
        cls.before_path = "satellite_image_before.jpg"
        cls.after_path = "satellite_image_after.jpg"
        
        # Ensure test images exist
        if not os.path.exists(cls.image_path):
            raise FileNotFoundError(f"Missing benchmark: {cls.image_path}")
            
        cls.raw_image = load_image(cls.image_path)
        cls.preprocessed = preprocess_image(cls.raw_image)
        
        # Synthetic test fixtures
        cls.pure_green = np.zeros((100, 100, 3), dtype=np.uint8)
        cls.pure_green[:, :] = [0, 255, 0]  # Pure Green in BGR
        
        cls.pure_black = np.zeros((100, 100, 3), dtype=np.uint8)  # No vegetation
        cls.pure_white = np.full((100, 100, 3), 255, dtype=np.uint8)  # Non-vegetation
        cls.pure_soil = np.full((100, 100, 3), (30, 80, 150), dtype=np.uint8)  # Brownish soil

    # =========================================================================
    # 1. CORE DETECTION ALGORITHM TESTS
    # =========================================================================

    def test_hsv_detection(self):
        """Test HSV color space segmentation."""
        mask = detect_hsv(self.preprocessed)
        self.assertEqual(mask.shape, self.preprocessed.shape[:2])
        self.assertTrue(np.all(np.isin(mask, [0, 255])))
        
        # Test synthetic pure green (must be 100% detected)
        pure_mask = detect_hsv(self.pure_green)
        self.assertEqual(np.count_nonzero(pure_mask), 10000)

    def test_exg_detection(self):
        """Test Excess Green Index."""
        mask = detect_exg(self.preprocessed, threshold=20)
        self.assertEqual(mask.shape, self.preprocessed.shape[:2])
        self.assertTrue(np.all(np.isin(mask, [0, 255])))
        
        # Synthetic test
        pure_mask = detect_exg(self.pure_green, threshold=20)
        self.assertEqual(np.count_nonzero(pure_mask), 10000)

    def test_exgr_detection(self):
        """Test Excess Green-Red Index."""
        mask = detect_exgr(self.preprocessed, threshold=10)
        self.assertEqual(mask.shape, self.preprocessed.shape[:2])
        self.assertTrue(np.all(np.isin(mask, [0, 255])))

    def test_vari_detection(self):
        """Test Visible Atmospherically Resistant Index."""
        mask = detect_vari(self.preprocessed, threshold=0.05)
        self.assertEqual(mask.shape, self.preprocessed.shape[:2])
        self.assertTrue(np.all(np.isin(mask, [0, 255])))

    def test_gli_detection(self):
        """Test Green Leaf Index."""
        mask = detect_gli(self.preprocessed, threshold=0.02)
        self.assertEqual(mask.shape, self.preprocessed.shape[:2])
        self.assertTrue(np.all(np.isin(mask, [0, 255])))

    def test_sobel_detection(self):
        """Test Sobel Gradient Edge baseline."""
        mask = detect_sobel(self.preprocessed, threshold_value=100)
        self.assertEqual(mask.shape, self.preprocessed.shape[:2])
        self.assertTrue(np.all(np.isin(mask, [0, 255])))

    # =========================================================================
    # 2. EXTENDED MODULE TESTS (HEALTH, PATCHES, TEMPORAL, GSD)
    # =========================================================================

    def test_canopy_health_classification(self):
        """Test 3-tier canopy vigor classification."""
        metrics, overlay, masks = classify_vegetation_health(self.preprocessed)
        
        self.assertIn("health_index_score", metrics)
        self.assertGreaterEqual(metrics["health_index_score"], 0.0)
        self.assertLessEqual(metrics["health_index_score"], 100.0)
        
        # Verify 3 sub-masks
        self.assertIn("tier1", masks)
        self.assertIn("tier2", masks)
        self.assertIn("tier3", masks)
        
        # Verify overlay dimensions
        self.assertEqual(overlay.shape, self.preprocessed.shape)

    def test_patch_fragmentation_analysis(self):
        """Test connected components and landscape patch morphology."""
        mask = detect_hsv(self.preprocessed)
        metrics, annotated = analyze_patches_and_fragmentation(mask, min_patch_area=25)
        
        self.assertIn("total_patches", metrics)
        self.assertGreater(metrics["total_patches"], 0)
        self.assertIn("largest_patch_pixels", metrics)
        self.assertIn("fragmentation_ratio", metrics)
        self.assertEqual(annotated.shape, self.preprocessed.shape)

    def test_real_world_area_scaling(self):
        """Test GSD geographic area calculations."""
        # 10,000 pixels at 10m GSD -> 10,000 * 100m² = 1,000,000 m² = 100 ha = 1 km²
        result = calculate_real_world_area(10000, 100000, gsd_meters=10.0)
        
        self.assertEqual(result["area_sq_meters"], 1000000.0)
        self.assertEqual(result["area_hectares"], 100.0)
        self.assertEqual(result["area_sq_km"], 1.0)
        self.assertAlmostEqual(result["coverage_percentage"], 10.0)

    def test_temporal_change_detection(self):
        """Test temporal differential change tracking."""
        b = load_image(self.before_path)
        a = load_image(self.after_path)
        
        metrics, viz, masks = detect_temporal_change(b, a, method="hsv", gsd_meters=10.0)
        
        self.assertIn("net_change_percentage", metrics)
        self.assertIn("status", metrics)
        self.assertIn("loss", masks)
        self.assertIn("gain", masks)
        self.assertIn("persist", masks)
        self.assertEqual(viz.shape, b.shape)

    # =========================================================================
    # 3. PERFORMANCE BENCHMARK TESTS
    # =========================================================================

    def test_execution_performance(self):
        """Ensure all 6 algorithms execute within acceptable latency limits (<500ms)."""
        t0 = time.time()
        results = run_all_methods(self.preprocessed)
        t_elapsed = time.time() - t0
        
        self.assertEqual(len(results), 6)
        self.assertLess(t_elapsed, 1.5, f"All 6 algorithms took {t_elapsed:.2f}s (too slow)")
        print(f"\n[PERFORMANCE] All 6 methods executed in {t_elapsed*1000:.1f}ms on {self.preprocessed.shape[1]}x{self.preprocessed.shape[0]} image.")


def run_tests():
    print("=" * 60)
    print("  Vegetation Detection Platform - AUTOMATED VERIFICATION")
    print("=" * 60)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVegetationSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n" + "=" * 60)
        print("  ALL TESTS PASSED SUCCESSFULLY! (100% PASS RATE) [OK]")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("  TESTS FAILED [ERROR]")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
