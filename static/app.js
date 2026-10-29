/**
 * Vegetation Detection Platform (v2.1)
 * Asynchronous client-side application logic for multi-spectral analysis,
 * temporal change tracking, canopy health classification, and GIS area scaling.
 */

document.addEventListener('DOMContentLoaded', () => {

    // =========================================================================
    // STATE
    // =========================================================================
    let currentOriginalImage = null;
    let currentMaskImage = null;
    let currentOverlayImage = null;
    let currentHealthData = null;
    let imageLoaded = false;

    // =========================================================================
    // DOM ELEMENTS
    // =========================================================================
    const navTabs = document.querySelectorAll('.nav-tab[data-tab]');
    const tabContents = document.querySelectorAll('.tab-content');

    // Upload Elements
    const fileInput = document.getElementById('file-input');
    const btnBrowse = document.getElementById('btn-browse');
    const btnDefault = document.getElementById('btn-default');
    const btnChange = document.getElementById('btn-change');
    const uploadArea = document.getElementById('upload-area');
    const uploadPreview = document.getElementById('upload-preview');
    const previewImage = document.getElementById('preview-image');
    const previewDims = document.getElementById('preview-dims');

    // Detect Tab Elements
    const methodSelect = document.getElementById('method-select');
    const hsvControls = document.getElementById('hsv-controls');
    const thresholdControls = document.getElementById('threshold-controls');
    const thresholdLabel = document.getElementById('threshold-label');
    const thresholdInput = document.getElementById('threshold-input');
    const thresholdVal = document.getElementById('threshold-val');
    const hLow = document.getElementById('h-low');
    const hHigh = document.getElementById('h-high');
    const sLow = document.getElementById('s-low');
    const vLow = document.getElementById('v-low');
    const hLowVal = document.getElementById('h-low-val');
    const hHighVal = document.getElementById('h-high-val');
    const sLowVal = document.getElementById('s-low-val');
    const vLowVal = document.getElementById('v-low-val');
    const gsdPreset = document.getElementById('gsd-preset');
    const customGsdBox = document.getElementById('custom-gsd-box');
    const customGsdVal = document.getElementById('custom-gsd-val');
    const btnApplyDetect = document.getElementById('btn-apply-detect');

    // Detect Results
    const containerOriginal = document.getElementById('container-original');
    const containerMask = document.getElementById('container-mask');
    const containerOverlay = document.getElementById('container-overlay');
    const gisHectares = document.getElementById('gis-hectares');
    const gisSqkm = document.getElementById('gis-sqkm');
    const gisAcres = document.getElementById('gis-acres');
    const gisCurrentGsd = document.getElementById('gis-current-gsd');
    const statCoverage = document.getElementById('stat-coverage');
    const statVegPixels = document.getElementById('stat-veg-pixels');
    const statNonvegPixels = document.getElementById('stat-nonveg-pixels');
    const statTotalPixels = document.getElementById('stat-total-pixels');

    // Compare Tab Elements
    const btnRunCompare = document.getElementById('btn-run-compare');
    const comparisonGrid = document.getElementById('comparison-grid');

    // Density Tab Elements
    const densityMethodSelect = document.getElementById('density-method-select');
    const densityGridSelect = document.getElementById('density-grid-select');
    const btnGenerateDensity = document.getElementById('btn-generate-density');
    const containerDensity = document.getElementById('container-density');
    const densityAvg = document.getElementById('density-avg');
    const densityMax = document.getElementById('density-max');
    const densityMin = document.getElementById('density-min');

    // Health Tab Elements
    const btnRunHealth = document.getElementById('btn-run-health');
    const healthScoreVal = document.getElementById('health-score-val');
    const healthScoreDesc = document.getElementById('health-score-desc');
    const tier1PctVeg = document.getElementById('tier1-pct-veg');
    const tier1Pixels = document.getElementById('tier1-pixels');
    const tier2PctVeg = document.getElementById('tier2-pct-veg');
    const tier2Pixels = document.getElementById('tier2-pixels');
    const tier3PctVeg = document.getElementById('tier3-pct-veg');
    const tier3Pixels = document.getElementById('tier3-pixels');
    const containerHealth = document.getElementById('container-health');

    // Patch Tab Elements
    const patchMethodSelect = document.getElementById('patch-method-select');
    const minPatchSize = document.getElementById('min-patch-size');
    const minPatchVal = document.getElementById('min-patch-val');
    const btnRunPatches = document.getElementById('btn-run-patches');
    const patchTotalCount = document.getElementById('patch-total-count');
    const patchLargestArea = document.getElementById('patch-largest-area');
    const patchMeanArea = document.getElementById('patch-mean-area');
    const patchFragmentationRatio = document.getElementById('patch-fragmentation-ratio');
    const containerPatches = document.getElementById('container-patches');

    // Temporal Change Elements
    const btnLoadTemporalSample = document.getElementById('btn-load-temporal-sample');
    const beforeFileInput = document.getElementById('before-file-input');
    const afterFileInput = document.getElementById('after-file-input');
    const temporalMethodSelect = document.getElementById('temporal-method-select');
    const temporalGsdSelect = document.getElementById('temporal-gsd-select');
    const btnRunTemporal = document.getElementById('btn-run-temporal');
    const statusIndicatorDot = document.getElementById('status-indicator-dot');
    const temporalStatusTitle = document.getElementById('temporal-status-title');
    const temporalStatusDesc = document.getElementById('temporal-status-desc');
    const statNetDelta = document.getElementById('stat-net-delta');
    const statLossArea = document.getElementById('stat-loss-area');
    const statGainArea = document.getElementById('stat-gain-area');
    const statPersistArea = document.getElementById('stat-persist-area');
    const containerTemporalViz = document.getElementById('container-temporal-viz');

    // Audit Report Modal Elements
    const btnOpenReport = document.getElementById('btn-open-report');
    const btnCloseReport = document.getElementById('btn-close-report');
    const btnPrintReport = document.getElementById('btn-print-report');
    const reportModal = document.getElementById('report-modal');
    const reportBody = document.getElementById('report-body');


    // =========================================================================
    // NAVIGATION TABS
    // =========================================================================
    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.getAttribute('data-tab');
            navTabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            const targetContent = document.getElementById(`content-${target}`);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });


    // =========================================================================
    // IMAGE UPLOADER & BENCHMARK LOADER
    // =========================================================================
    btnBrowse.addEventListener('click', () => fileInput.click());
    btnChange.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            uploadFile(e.target.files[0]);
        }
    });

    btnDefault.addEventListener('click', async () => {
        btnDefault.innerText = 'Loading...';
        try {
            const res = await fetch('/api/load-default', { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                onImageLoaded(data.original, data.width, data.height);
                runDetection();
            } else {
                alert(data.error || 'Failed to load benchmark image.');
            }
        } catch (err) {
            console.error(err);
            alert('Error connecting to backend server.');
        } finally {
            btnDefault.innerText = 'Use Benchmark Image';
        }
    });

    async function uploadFile(file) {
        const formData = new FormData();
        formData.append('image', file);
        try {
            const res = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if (data.success) {
                onImageLoaded(data.original, data.width, data.height);
                runDetection();
            } else {
                alert(data.error || 'Upload failed.');
            }
        } catch (err) {
            console.error(err);
            alert('Error uploading image.');
        }
    }

    function onImageLoaded(base64Image, w, h) {
        currentOriginalImage = base64Image;
        imageLoaded = true;

        uploadArea.classList.add('hidden');
        uploadPreview.classList.remove('hidden');
        previewImage.src = base64Image;
        previewDims.innerText = `${w} × ${h} px`;

        containerOriginal.innerHTML = `<img src="${base64Image}" alt="Original Satellite View">`;
    }


    // =========================================================================
    // 1. DETECT & AREA SCALE TAB
    // =========================================================================
    // Method select change
    methodSelect.addEventListener('change', () => {
        const method = methodSelect.value;
        if (method === 'hsv') {
            hsvControls.classList.remove('hidden');
            thresholdControls.classList.add('hidden');
        } else {
            hsvControls.classList.add('hidden');
            thresholdControls.classList.remove('hidden');

            if (method === 'exg') {
                thresholdLabel.innerText = 'ExG Threshold (Default: 20)';
                thresholdInput.min = -50; thresholdInput.max = 100; thresholdInput.step = 1; thresholdInput.value = 20;
            } else if (method === 'exgr') {
                thresholdLabel.innerText = 'ExGR Threshold (Default: 10)';
                thresholdInput.min = -50; thresholdInput.max = 100; thresholdInput.step = 1; thresholdInput.value = 10;
            } else if (method === 'vari') {
                thresholdLabel.innerText = 'VARI Threshold (Default: 0.05)';
                thresholdInput.min = -1.0; thresholdInput.max = 1.0; thresholdInput.step = 0.01; thresholdInput.value = 0.05;
            } else if (method === 'gli') {
                thresholdLabel.innerText = 'GLI Threshold (Default: 0.02)';
                thresholdInput.min = -1.0; thresholdInput.max = 1.0; thresholdInput.step = 0.01; thresholdInput.value = 0.02;
            } else if (method === 'sobel') {
                thresholdLabel.innerText = 'Sobel Gradient Threshold (Default: 100)';
                thresholdInput.min = 10; thresholdInput.max = 250; thresholdInput.step = 5; thresholdInput.value = 100;
            }
            thresholdVal.innerText = thresholdInput.value;
        }
    });

    // Sliders
    hLow.addEventListener('input', () => { hLowVal.innerText = hLow.value; });
    hHigh.addEventListener('input', () => { hHighVal.innerText = hHigh.value; });
    sLow.addEventListener('input', () => { sLowVal.innerText = sLow.value; });
    vLow.addEventListener('input', () => { vLowVal.innerText = vLow.value; });
    thresholdInput.addEventListener('input', () => { thresholdVal.innerText = thresholdInput.value; });

    // GSD Resolution Presets
    gsdPreset.addEventListener('change', () => {
        if (gsdPreset.value === 'custom') {
            customGsdBox.classList.remove('hidden');
        } else {
            customGsdBox.classList.add('hidden');
        }
        if (imageLoaded) runDetection();
    });

    function getSelectedGSD() {
        if (gsdPreset.value === 'custom') {
            return parseFloat(customGsdVal.value) || 10.0;
        }
        return parseFloat(gsdPreset.value) || 10.0;
    }

    btnApplyDetect.addEventListener('click', () => {
        if (!imageLoaded) {
            btnDefault.click();
            return;
        }
        runDetection();
    });

    async function runDetection() {
        if (!imageLoaded) return;
        btnApplyDetect.innerText = 'Processing...';

        const method = methodSelect.value;
        const gsd = getSelectedGSD();
        let params = {};

        if (method === 'hsv') {
            params = {
                h_low: parseInt(hLow.value),
                h_high: parseInt(hHigh.value),
                s_low: parseInt(sLow.value),
                v_low: parseInt(vLow.value),
            };
        } else {
            params = { threshold: parseFloat(thresholdInput.value) };
        }

        try {
            const res = await fetch('/api/detect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ method, params, gsd_meters: gsd })
            });
            const data = await res.json();
            if (data.success) {
                currentMaskImage = data.mask;
                currentOverlayImage = data.overlay;

                containerMask.innerHTML = `<img src="${data.mask}" alt="Binary Mask">`;
                containerOverlay.innerHTML = `<img src="${data.overlay}" alt="Canopy Overlay">`;

                // Statistics
                statCoverage.innerText = `${data.stats.coverage_percentage}%`;
                statVegPixels.innerText = data.stats.vegetation_pixels.toLocaleString();
                statNonvegPixels.innerText = data.stats.non_vegetation_pixels.toLocaleString();
                statTotalPixels.innerText = data.stats.total_pixels.toLocaleString();

                // GIS Banner
                if (data.area_metrics) {
                    gisHectares.innerText = `${data.area_metrics.area_hectares.toLocaleString()} ha`;
                    gisSqkm.innerText = `${data.area_metrics.area_sq_km.toLocaleString()} km²`;
                    gisAcres.innerText = `${data.area_metrics.area_acres.toLocaleString()} acres`;
                    gisCurrentGsd.innerText = `${gsd} m/px`;
                }

                // Carbon Banner
                if (data.carbon_metrics) {
                    const c = data.carbon_metrics;
                    document.getElementById('carbon-biomass').innerText = `${c.aboveground_biomass_tons.toLocaleString()} tons`;
                    document.getElementById('carbon-co2e').innerText = `${c.co2e_sequestered_tons.toLocaleString()} tCO₂e`;
                    document.getElementById('carbon-vehicles').innerText = `${c.passenger_vehicles_annual_offset.toLocaleString()} cars/yr`;
                }
            }
        } catch (err) {
            console.error(err);
        } finally {
            btnApplyDetect.innerText = 'Apply & Run Detection';
        }
    }

    // CIR False-Color Toggle
    let currentCirImage = null;
    const btnToggleCir = document.getElementById('btn-toggle-cir');
    if (btnToggleCir) {
        btnToggleCir.addEventListener('click', async () => {
            if (!imageLoaded) return;
            if (!currentCirImage) {
                btnToggleCir.innerText = 'Loading CIR...';
                try {
                    const res = await fetch('/api/cir', { method: 'POST' });
                    const d = await res.json();
                    if (d.success) {
                        currentCirImage = d.cir;
                    }
                } catch(e) { console.error(e); }
                btnToggleCir.innerText = '🛰️ Simulate CIR';
            }
            if (currentCirImage) {
                containerOriginal.innerHTML = `<img src="${currentCirImage}" alt="Simulated CIR False Color">`;
            }
        });
    }

    // Quadrant ROI Slicer
    const quadrantSelect = document.getElementById('quadrant-select');
    if (quadrantSelect) {
        quadrantSelect.addEventListener('change', async () => {
            if (!imageLoaded) return;
            const q = quadrantSelect.value;
            if (q === 'all') {
                runDetection();
                return;
            }
            try {
                const res = await fetch('/api/quadrants', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ method: methodSelect.value, gsd_meters: getSelectedGSD() })
                });
                const d = await res.json();
                if (d.success && d.sectors[q]) {
                    const s = d.sectors[q];
                    statCoverage.innerText = `${s.coverage_percentage}%`;
                    statVegPixels.innerText = s.vegetation_pixels.toLocaleString();
                    statTotalPixels.innerText = s.total_pixels.toLocaleString();
                    statNonvegPixels.innerText = (s.total_pixels - s.vegetation_pixels).toLocaleString();
                    gisHectares.innerText = `${s.area_hectares.toLocaleString()} ha`;
                }
            } catch(e) { console.error(e); }
        });
    }

    // View Toggles on Detect Overlay Card
    document.querySelectorAll('[data-view]').forEach(btn => {
        btn.addEventListener('click', async () => {
            document.querySelectorAll('[data-view]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const view = btn.getAttribute('data-view');
            if (view === 'mask' && currentMaskImage) {
                containerOverlay.innerHTML = `<img src="${currentMaskImage}" alt="Mask View">`;
            } else if (view === 'overlay' && currentOverlayImage) {
                containerOverlay.innerHTML = `<img src="${currentOverlayImage}" alt="Overlay View">`;
            } else if (view === 'cir') {
                if (!currentCirImage) {
                    try {
                        const res = await fetch('/api/cir', { method: 'POST' });
                        const d = await res.json();
                        if (d.success) currentCirImage = d.cir;
                    } catch(e) {}
                }
                if (currentCirImage) {
                    containerOverlay.innerHTML = `<img src="${currentCirImage}" alt="CIR False-Color">`;
                }
            }
        });
    });


    // =========================================================================
    // 2. COMPARE (6 METHODS) TAB
    // =========================================================================
    btnRunCompare.addEventListener('click', async () => {
        if (!imageLoaded) {
            alert('Please load an image first.');
            return;
        }
        btnRunCompare.innerHTML = '<span>⚡ Processing 6 Indices...</span>';

        try {
            const res = await fetch('/api/compare', { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                renderComparisonGrid(data.methods);
            }
        } catch (err) {
            console.error(err);
        } finally {
            btnRunCompare.innerHTML = '<span>⚡ Run All 6 Algorithms</span>';
        }
    });

    function renderComparisonGrid(methods) {
        comparisonGrid.innerHTML = '';
        for (const [name, result] of Object.entries(methods)) {
            const card = document.createElement('div');
            card.className = 'method-card';
            card.innerHTML = `
                <div class="method-card-header">
                    <h4>${name}</h4>
                    <span class="method-badge">${result.stats.coverage_percentage}%</span>
                </div>
                <div class="method-images">
                    <div class="method-img-box">
                        <img src="${result.mask}" alt="${name} Mask" title="Binary Mask">
                    </div>
                    <div class="method-img-box">
                        <img src="${result.overlay}" alt="${name} Overlay" title="Overlay">
                    </div>
                </div>
            `;
            comparisonGrid.appendChild(card);
        }
    }


    // =========================================================================
    // 3. DENSITY HEATMAP TAB
    // =========================================================================
    btnGenerateDensity.addEventListener('click', async () => {
        if (!imageLoaded) {
            alert('Please load an image first.');
            return;
        }
        btnGenerateDensity.innerText = 'Computing Heatmap...';

        const method = densityMethodSelect.value;
        const grid_size = parseInt(densityGridSelect.value);

        try {
            const res = await fetch('/api/density', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ method, grid_size })
            });
            const data = await res.json();
            if (data.success) {
                containerDensity.innerHTML = `<img src="${data.heatmap}" alt="Density Heatmap">`;
                densityAvg.innerText = `${data.avg_density}%`;
                densityMax.innerText = `${data.max_density}%`;
                densityMin.innerText = `${data.min_density}%`;
            }
        } catch (err) {
            console.error(err);
        } finally {
            btnGenerateDensity.innerText = 'Compute Density Heatmap';
        }
    });


    // =========================================================================
    // 4. CANOPY HEALTH & STRESS TAB
    // =========================================================================
    btnRunHealth.addEventListener('click', async () => {
        if (!imageLoaded) {
            alert('Please load an image first.');
            return;
        }
        btnRunHealth.innerText = 'Classifying Vigor...';

        try {
            const res = await fetch('/api/health', { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                currentHealthData = data;
                renderHealthResults(data);
            }
        } catch (err) {
            console.error(err);
        } finally {
            btnRunHealth.innerText = '⚡ Classify Canopy Health';
        }
    });

    function renderHealthResults(data) {
        const m = data.metrics;
        healthScoreVal.innerText = m.health_index_score;
        healthScoreDesc.innerText = `Evaluated across ${m.total_vegetation_pixels.toLocaleString()} vegetation pixels using normalized Green Leaf Index (GLI).`;

        tier1PctVeg.innerText = `${m.tier1_high_vigour.pct_of_veg}%`;
        tier1Pixels.innerText = `${m.tier1_high_vigour.pixels.toLocaleString()} px`;

        tier2PctVeg.innerText = `${m.tier2_moderate.pct_of_veg}%`;
        tier2Pixels.innerText = `${m.tier2_moderate.pixels.toLocaleString()} px`;

        tier3PctVeg.innerText = `${m.tier3_stressed.pct_of_veg}%`;
        tier3Pixels.innerText = `${m.tier3_stressed.pixels.toLocaleString()} px`;

        containerHealth.innerHTML = `<img src="${data.overlay}" alt="Health Overlay">`;
    }

    // Health sub-mask view toggles
    document.querySelectorAll('[data-healthview]').forEach(btn => {
        btn.addEventListener('click', () => {
            if (!currentHealthData) return;
            document.querySelectorAll('[data-healthview]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const view = btn.getAttribute('data-healthview');
            if (view === 'overlay') {
                containerHealth.innerHTML = `<img src="${currentHealthData.overlay}" alt="Full Health Overlay">`;
            } else if (view === 'tier1') {
                containerHealth.innerHTML = `<img src="${currentHealthData.tier1_mask}" alt="Tier 1 High Vigor Mask">`;
            } else if (view === 'tier2') {
                containerHealth.innerHTML = `<img src="${currentHealthData.tier2_mask}" alt="Tier 2 Moderate Vigor Mask">`;
            } else if (view === 'tier3') {
                containerHealth.innerHTML = `<img src="${currentHealthData.tier3_mask}" alt="Tier 3 Stressed Mask">`;
            }
        });
    });


    // =========================================================================
    // 5. PATCH & FRAGMENTATION TAB
    // =========================================================================
    minPatchSize.addEventListener('input', () => {
        minPatchVal.innerText = minPatchSize.value;
    });

    btnRunPatches.addEventListener('click', async () => {
        if (!imageLoaded) {
            alert('Please load an image first.');
            return;
        }
        btnRunPatches.innerText = 'Analyzing Patches...';

        const method = patchMethodSelect.value;
        const min_patch_area = parseInt(minPatchSize.value);

        try {
            const res = await fetch('/api/patches', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ method, min_patch_area })
            });
            const data = await res.json();
            if (data.success) {
                const m = data.metrics;
                patchTotalCount.innerText = m.total_patches.toLocaleString();
                patchLargestArea.innerText = `${m.largest_patch_pixels.toLocaleString()} px (${m.largest_patch_percentage}%)`;
                patchMeanArea.innerText = `${m.mean_patch_pixels.toLocaleString()} px`;
                patchFragmentationRatio.innerText = m.fragmentation_ratio;

                containerPatches.innerHTML = `<img src="${data.annotated}" alt="Patch Cluster Visualization">`;
            }
        } catch (err) {
            console.error(err);
        } finally {
            btnRunPatches.innerText = '⚡ Analyze Patch Clusters';
        }
    });


    // =========================================================================
    // 6. TEMPORAL CHANGE DETECTION TAB
    // =========================================================================
    btnLoadTemporalSample.addEventListener('click', async () => {
        btnLoadTemporalSample.innerText = 'Loading Benchmark Pair...';
        try {
            const res = await fetch('/api/temporal_sample');
            const data = await res.json();
            if (data.success) {
                btnRunTemporal.click();
            }
        } catch (err) {
            console.error(err);
        } finally {
            btnLoadTemporalSample.innerText = '🛰️ Load Benchmark Before/After Pair';
        }
    });

    btnRunTemporal.addEventListener('click', async () => {
        btnRunTemporal.innerText = 'Computing Change...';
        const method = temporalMethodSelect.value;
        const gsd = parseFloat(temporalGsdSelect.value) || 10.0;

        let reqPromise;

        if (beforeFileInput.files[0] && afterFileInput.files[0]) {
            const formData = new FormData();
            formData.append('image_before', beforeFileInput.files[0]);
            formData.append('image_after', afterFileInput.files[0]);
            formData.append('method', method);
            formData.append('gsd_meters', gsd);
            reqPromise = fetch('/api/temporal_change', { method: 'POST', body: formData });
        } else {
            reqPromise = fetch('/api/temporal_change', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ use_sample: true, method, gsd_meters: gsd })
            });
        }

        try {
            const res = await reqPromise;
            const data = await res.json();
            if (data.success) {
                const m = data.metrics;
                temporalStatusTitle.innerText = m.status;
                temporalStatusDesc.innerText = `Before: ${m.before.coverage_percentage}% (${m.before.area_hectares} ha) | After: ${m.after.coverage_percentage}% (${m.after.area_hectares} ha)`;
                statusIndicatorDot.style.background = m.status_color;

                const deltaSign = m.net_change_percentage >= 0 ? '+' : '';
                statNetDelta.innerText = `${deltaSign}${m.net_change_percentage}%`;
                statNetDelta.className = `stat-value ${m.net_change_percentage >= 0 ? 'text-green' : 'text-red'}`;

                statLossArea.innerText = `${m.breakdown.loss_deforestation.area_hectares} ha`;
                statGainArea.innerText = `${m.breakdown.gain_reforestation.area_hectares} ha`;
                statPersistArea.innerText = `${m.breakdown.persistent_canopy.area_hectares} ha`;

                containerTemporalViz.innerHTML = `<img src="${data.visualization}" alt="Temporal Change Map">`;
            } else {
                alert(data.error || 'Failed to compute temporal change.');
            }
        } catch (err) {
            console.error(err);
        } finally {
            btnRunTemporal.innerText = '⚡ Compute Temporal Change';
        }
    });


    // =========================================================================
    // 7. COMPREHENSIVE AUDIT REPORT MODAL
    // =========================================================================
    btnOpenReport.addEventListener('click', async () => {
        reportModal.classList.remove('hidden');
        reportBody.innerHTML = '<div class="report-loading">Compiling diagnostic audit data...</div>';

        try {
            const res = await fetch('/api/full_report');
            const data = await res.json();
            if (data.success) {
                renderAuditReport(data);
            }
        } catch (err) {
            reportBody.innerHTML = '<div class="report-error">Error generating report.</div>';
        }
    });

    btnCloseReport.addEventListener('click', () => {
        reportModal.classList.add('hidden');
    });

    btnPrintReport.addEventListener('click', () => {
        window.print();
    });

    function renderAuditReport(data) {
        let compRows = '';
        for (const [name, stats] of Object.entries(data.comparison)) {
            compRows += `
                <tr>
                    <td><strong>${name}</strong></td>
                    <td>${stats.vegetation_pixels.toLocaleString()}</td>
                    <td>${stats.total_pixels.toLocaleString()}</td>
                    <td><strong class="text-green">${stats.coverage_percentage}%</strong></td>
                </tr>
            `;
        }

        const h = data.health;
        const p = data.patches;
        const s = data.scales;

        reportBody.innerHTML = `
            <div class="report-section">
                <h3>1. Executive Scene Summary</h3>
                <table class="report-table">
                    <tr><th>Parameter</th><th>Value</th></tr>
                    <tr><td>Scene Dimensions</td><td>${data.image_dimensions.width} × ${data.image_dimensions.height} pixels</td></tr>
                    <tr><td>Primary Detection Coverage</td><td><strong>${data.comparison['HSV Segmentation']?.coverage_percentage}%</strong></td></tr>
                    <tr><td>Composite Canopy Health Index</td><td><strong>${h.health_index_score} / 100</strong></td></tr>
                    <tr><td>Discrete Patch Clusters</td><td>${p.total_patches} patches (Largest: ${p.largest_patch_pixels.toLocaleString()} px)</td></tr>
                </table>
            </div>

            <div class="report-section">
                <h3>2. Multi-Spectral Index Benchmark</h3>
                <table class="report-table">
                    <thead>
                        <tr>
                            <th>Algorithm Method</th>
                            <th>Vegetation Pixels</th>
                            <th>Total Pixels</th>
                            <th>Coverage (%)</th>
                        </tr>
                    </thead>
                    <tbody>${compRows}</tbody>
                </table>
            </div>

            <div class="report-section">
                <h3>3. Canopy Physiological Health Breakdown</h3>
                <table class="report-table">
                    <thead>
                        <tr>
                            <th>Health Grade</th>
                            <th>Canopy Share (%)</th>
                            <th>Total Scene (%)</th>
                            <th>Pixel Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><span style="color:#22c55e">●</span> Tier 1: High Vigor / Dense</td>
                            <td><strong>${h.tier1_high_vigour.pct_of_veg}%</strong></td>
                            <td>${h.tier1_high_vigour.pct_of_scene}%</td>
                            <td>${h.tier1_high_vigour.pixels.toLocaleString()}</td>
                        </tr>
                        <tr>
                            <td><span style="color:#32cd32">●</span> Tier 2: Moderate / Grasslands</td>
                            <td><strong>${h.tier2_moderate.pct_of_veg}%</strong></td>
                            <td>${h.tier2_moderate.pct_of_scene}%</td>
                            <td>${h.tier2_moderate.pixels.toLocaleString()}</td>
                        </tr>
                        <tr>
                            <td><span style="color:#ffa500">●</span> Tier 3: Stressed / Dry</td>
                            <td><strong>${h.tier3_stressed.pct_of_veg}%</strong></td>
                            <td>${h.tier3_stressed.pct_of_scene}%</td>
                            <td>${h.tier3_stressed.pixels.toLocaleString()}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="report-section">
                <h3>4. Multi-Sensor GIS Area Scaling</h3>
                <table class="report-table">
                    <thead>
                        <tr>
                            <th>Sensor Resolution</th>
                            <th>GSD</th>
                            <th>Canopy (Hectares)</th>
                            <th>Canopy (Sq Km)</th>
                            <th>Canopy (Acres)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Sentinel-2 (ESA)</td>
                            <td>10.0 m/px</td>
                            <td><strong>${s.sentinel2_10m.area_hectares} ha</strong></td>
                            <td>${s.sentinel2_10m.area_sq_km} km²</td>
                            <td>${s.sentinel2_10m.area_acres} ac</td>
                        </tr>
                        <tr>
                            <td>PlanetScope (Planet Labs)</td>
                            <td>3.0 m/px</td>
                            <td><strong>${s.planetscope_3m.area_hectares} ha</strong></td>
                            <td>${s.planetscope_3m.area_sq_km} km²</td>
                            <td>${s.planetscope_3m.area_acres} ac</td>
                        </tr>
                        <tr>
                            <td>UAV / Aerial Drone</td>
                            <td>0.5 m/px</td>
                            <td><strong>${s.drone_05m.area_hectares} ha</strong></td>
                            <td>${s.drone_05m.area_sq_km} km²</td>
                            <td>${s.drone_05m.area_acres} ac</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        `;
    }

    // Auto-load benchmark on initial dashboard startup for instant demo readiness
    setTimeout(() => {
        btnDefault.click();
    }, 400);

});
