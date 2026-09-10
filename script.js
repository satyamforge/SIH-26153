/* =====================================================
   NETGUARD AI — SIH 26153
   JAVASCRIPT
   PART 1 — Upload, Sample Data & Navigation
   ===================================================== */

document.addEventListener("DOMContentLoaded", () => {

    /* =========================
       ELEMENTS
    ========================= */

    const fileInput = document.getElementById("fileInput");
    const browseButton = document.getElementById("browseButton");
    const dropZone = document.getElementById("dropZone");

    const selectedFile = document.getElementById("selectedFile");
    const fileName = document.getElementById("fileName");
    const fileSize = document.getElementById("fileSize");
    const removeFileButton =
        document.getElementById("removeFileButton");

    const loadSampleButton =
        document.getElementById("loadSampleButton");

    const uploadHeroButton =
        document.getElementById("uploadHeroButton");

    const resetButton =
        document.getElementById("resetButton");

    const navItems =
        document.querySelectorAll(".nav-item");

    const pageSections =
        document.querySelectorAll(".page-section");

    const toast =
        document.getElementById("toast");

    const toastTitle =
        document.getElementById("toastTitle");

    const toastMessage =
        document.getElementById("toastMessage");

    const toastClose =
        document.getElementById("toastClose");


    /* =========================
       APP STATE
    ========================= */

    let currentFile = null;
    let usingSampleData = false;

    const MAX_FILE_SIZE = 50 * 1024 * 1024;

    const allowedExtensions = [
        ".pcap",
        ".pcapng",
        ".csv"
    ];


    /* =========================
       TOAST MESSAGE
    ========================= */

    function showToast(title, message) {

        if (!toast) return;

        toastTitle.textContent = title;
        toastMessage.textContent = message;

        toast.classList.add("show");

        setTimeout(() => {
            toast.classList.remove("show");
        }, 3500);
    }


    if (toastClose) {

        toastClose.addEventListener("click", () => {
            toast.classList.remove("show");
        });

    }


    /* =========================
       FILE VALIDATION
    ========================= */

    function validateFile(file) {

        if (!file) {
            return false;
        }

        const name =
            file.name.toLowerCase();

        const validExtension =
            allowedExtensions.some(extension =>
                name.endsWith(extension)
            );

        if (!validExtension) {

            showToast(
                "Invalid File",
                "Please upload a PCAP, PCAPNG or CSV file."
            );

            return false;
        }


        if (file.size > MAX_FILE_SIZE) {

            showToast(
                "File Too Large",
                "Maximum allowed file size is 50 MB."
            );

            return false;
        }


        return true;
    }


    /* =========================
       FORMAT FILE SIZE
    ========================= */

    function formatFileSize(bytes) {

        if (bytes < 1024) {
            return bytes + " B";
        }

        if (bytes < 1024 * 1024) {
            return (bytes / 1024).toFixed(1) + " KB";
        }

        return (bytes / (1024 * 1024)).toFixed(2) + " MB";
    }


    /* =========================
       SHOW SELECTED FILE
    ========================= */

    function displayFile(file) {

        if (!validateFile(file)) {
            return;
        }

        currentFile = file;
        usingSampleData = false;

        fileName.textContent =
            file.name;

        fileSize.textContent =
            formatFileSize(file.size);

        selectedFile.hidden = false;

        showToast(
            "File Ready",
            `${file.name} is ready for analysis.`
        );
    }


    /* =========================
       BROWSE FILE
    ========================= */

    if (browseButton && fileInput) {

        browseButton.addEventListener("click", () => {

            fileInput.click();

        });


        fileInput.addEventListener("change", event => {

            const file =
                event.target.files[0];

            displayFile(file);

        });

    }


    /* =========================
       HERO UPLOAD BUTTON
    ========================= */

    if (uploadHeroButton && fileInput) {

        uploadHeroButton.addEventListener("click", () => {

            fileInput.click();

        });

    }


    /* =========================
       DRAG & DROP
    ========================= */

    if (dropZone) {

        dropZone.addEventListener(
            "dragover",
            event => {

                event.preventDefault();

                dropZone.classList.add(
                    "drag-over"
                );

            }
        );


        dropZone.addEventListener(
            "dragleave",
            () => {

                dropZone.classList.remove(
                    "drag-over"
                );

            }
        );


        dropZone.addEventListener(
            "drop",
            event => {

                event.preventDefault();

                dropZone.classList.remove(
                    "drag-over"
                );

                const file =
                    event.dataTransfer.files[0];

                displayFile(file);

            }
        );

    }


    /* =========================
       REMOVE FILE
    ========================= */

    if (removeFileButton) {

        removeFileButton.addEventListener(
            "click",
            () => {

                currentFile = null;
                usingSampleData = false;

                selectedFile.hidden = true;

                if (fileInput) {
                    fileInput.value = "";
                }

                showToast(
                    "File Removed",
                    "Upload area is ready for a new analysis."
                );

            }
        );

    }


    /* =========================
       LOAD SAMPLE DATA
    ========================= */

    if (loadSampleButton) {

        loadSampleButton.addEventListener(
            "click",
            () => {
                

                currentFile = {
                    name: "SIH26153_demo_traffic.csv",
                    size: 2.4 * 1024 * 1024,
                    sample: true
                };

                usingSampleData = true;

                fileName.textContent =
                    "SIH26153_demo_traffic.csv";

                fileSize.textContent =
                    "2.40 MB • Bundled Demo Dataset";

                selectedFile.hidden = false;

                showToast(
                    "Sample Data Loaded",
                    "Demo network traffic is ready for analysis."
                );

            }
        );

    }


    /* =========================
       NAVIGATION
    ========================= */

    navItems.forEach(item => {

        item.addEventListener(
            "click",
            () => {

                const target =
                    item.dataset.section;

                if (!target) return;


                navItems.forEach(nav => {
                    nav.classList.remove(
                        "active"
                    );
                });

                item.classList.add("active");


                pageSections.forEach(section => {

                    section.classList.remove(
                        "active-section"
                    );

                });


                const targetSection =
                    document.getElementById(target);

                if (targetSection) {

                    targetSection.classList.add(
                        "active-section"
                    );

                }

                window.scrollTo({
                    top: 0,
                    behavior: "smooth"
                });

            }
        );

    });


    /* =========================
       RESET
    ========================= */

    if (resetButton) {

        resetButton.addEventListener(
            "click",
            () => {

                currentFile = null;
                usingSampleData = false;

                if (fileInput) {
                    fileInput.value = "";
                }

                if (selectedFile) {
                    selectedFile.hidden = true;
                }

                showToast(
                    "Analysis Reset",
                    "The dashboard is ready for a new analysis."
                );

            }
        );

    }


    /* =========================
       INITIAL STATUS
    ========================= */

    console.log(
        "NetGuard AI frontend initialized."
    );

});
/* =====================================================
   PART 2 — Analysis, Results, Chart, Filters & Export
   ===================================================== */

document.addEventListener("DOMContentLoaded", () => {

    /* =========================
       ANALYSIS ELEMENTS
    ========================= */

    const runButton =
        document.getElementById("runAnalysisButton");

    const progressPanel =
        document.getElementById("progressPanel");

    const progressFill =
        document.getElementById("progressFill");

    const progressText =
        document.getElementById("progressText");

    const progressStages =
        document.querySelectorAll(".progress-stages span");

    const resultsSection =
        document.getElementById("results");

    const threatTableBody =
        document.getElementById("threatTableBody");

    const searchInput =
        document.getElementById("threatSearch");

    const stageFilter =
        document.getElementById("stageFilter");

    const exportCsvButton =
        document.getElementById("exportCsvButton");

    const exportPdfButton =
        document.getElementById("exportPdfButton");

    const baselineToggle =
        document.getElementById("baselineToggle");

    const explanationPanel =
        document.getElementById("explanationPanel");

    const explanationClose =
        document.getElementById("explanationClose");

    const explanationTitle =
        document.getElementById("explanationTitle");

    const probabilityChart =
        document.getElementById("probabilityChart");

    const riskValue =
        document.getElementById("riskValue");


    /* =========================
       DEMO RESULTS
       ========================= */

    const demoFlows = [

        {
            src: "192.168.1.24",
            dst: "10.0.0.15",
            port: 445,
            protocol: "TCP",
            risk: 94,
            stage: "Lateral Movement"
        },

        {
            src: "172.16.4.21",
            dst: "192.168.1.8",
            port: 22,
            protocol: "TCP",
            risk: 87,
            stage: "Initial Access"
        },

        {
            src: "10.0.0.42",
            dst: "8.8.8.8",
            port: 443,
            protocol: "TCP",
            risk: 79,
            stage: "Command & Control"
        },

        {
            src: "192.168.1.77",
            dst: "172.16.0.20",
            port: 3389,
            protocol: "TCP",
            risk: 72,
            stage: "Reconnaissance"
        },

        {
            src: "10.10.2.14",
            dst: "10.10.4.9",
            port: 21,
            protocol: "TCP",
            risk: 91,
            stage: "Exfiltration"
        },

        {
            src: "172.20.1.12",
            dst: "192.168.1.30",
            port: 8080,
            protocol: "TCP",
            risk: 68,
            stage: "Initial Access"
        },

        {
            src: "192.168.2.44",
            dst: "10.0.0.11",
            port: 53,
            protocol: "UDP",
            risk: 61,
            stage: "Reconnaissance"
        },

        {
            src: "10.0.1.18",
            dst: "10.0.2.50",
            port: 445,
            protocol: "TCP",
            risk: 83,
            stage: "Lateral Movement"
        }
    ];


    let analysisResults = [];


    /* =========================
       PROGRESS HELPER
    ========================= */

    function updateProgress(percent, message, stage) {

        if (progressFill) {
            progressFill.style.width = percent + "%";
        }

        if (progressText) {
            progressText.textContent = message;
        }

        progressStages.forEach((item, index) => {

            item.classList.remove(
                "active",
                "completed"
            );

            if (index < stage) {
                item.classList.add("completed");
            }

            if (index === stage) {
                item.classList.add("active");
            }

        });
    }


    /* =========================
       RUN ANALYSIS
    ========================= */

    if (runButton) {

        runButton.addEventListener(
            "click",
            async () => {

                runButton.disabled = true;

                if (progressPanel) {
                    progressPanel.hidden = false;
                }

                updateProgress(
                    10,
                    "Preparing network telemetry...",
                    0
                );

                await wait(700);


                updateProgress(
                    35,
                    "Extracting network flow features...",
                    0
                );

                await wait(800);


                updateProgress(
                    62,
                    "Running world-model prediction...",
                    1
                );

                await wait(900);


                updateProgress(
                    82,
                    "Computing SHAP explanations...",
                    2
                );

                await wait(800);


                updateProgress(
                    100,
                    "Analysis completed successfully.",
                    2
                );


                analysisResults =
                    [...demoFlows];


                renderResults();

                drawProbabilityChart();

                if (resultsSection) {
                    resultsSection.scrollIntoView({
                        behavior: "smooth"
                    });
                }


                showAnalysisToast();


                setTimeout(() => {
                    runButton.disabled = false;
                }, 500);

            }
        );

    }


    /* =========================
       WAIT
    ========================= */

    function wait(milliseconds) {

        return new Promise(resolve => {

            setTimeout(
                resolve,
                milliseconds
            );

        });

    }


    /* =========================
       SHOW RESULTS
    ========================= */

    function renderResults() {

        if (!threatTableBody) {
            return;
        }


        threatTableBody.innerHTML = "";


        analysisResults.forEach(
            (flow, index) => {

                const row =
                    document.createElement("tr");


                const riskClass =
                    flow.risk >= 80
                        ? "risk-high"
                        : flow.risk >= 60
                            ? "risk-medium"
                            : "risk-low";


                const stageClass =
                    getStageClass(flow.stage);


                row.innerHTML = `

                    <td>${flow.src}</td>

                    <td>${flow.dst}</td>

                    <td>${flow.port}</td>

                    <td>${flow.protocol}</td>

                    <td>
                        <span class="${riskClass}">
                            ${flow.risk}%
                        </span>
                    </td>

                    <td>
                        <span class="stage-pill ${stageClass}">
                            ${flow.stage}
                        </span>
                    </td>

                    <td>
                        <button
                            class="why-button"
                            data-index="${index}">
                            WHY FLAGGED
                        </button>
                    </td>

                `;


                threatTableBody.appendChild(row);

            }
        );


        attachExplanationButtons();

        updateRiskScore();

    }


    /* =========================
       STAGE CLASS
    ========================= */

    function getStageClass(stage) {

        if (stage === "Reconnaissance") {
            return "recon";
        }

        if (stage === "Initial Access") {
            return "initial";
        }

        if (stage === "Lateral Movement") {
            return "lateral";
        }

        if (stage === "Command & Control") {
            return "c2";
        }

        return "exfil";
    }


    /* =========================
       RISK SCORE
    ========================= */

    function updateRiskScore() {

        if (!riskValue) {
            return;
        }

        if (analysisResults.length === 0) {
            riskValue.textContent = "0%";
            return;
        }


        const total =
            analysisResults.reduce(
                (sum, flow) =>
                    sum + flow.risk,
                0
            );


        const average =
            Math.round(
                total / analysisResults.length
            );


        riskValue.textContent =
            average + "%";

    }


    /* =========================
       WHY FLAGGED
       ========================= */

    function attachExplanationButtons() {

        const buttons =
            document.querySelectorAll(
                ".why-button"
            );


        buttons.forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    const index =
                        Number(
                            button.dataset.index
                        );

                    showExplanation(
                        analysisResults[index]
                    );

                }
            );

        });

    }


    function showExplanation(flow) {

        if (!explanationPanel || !flow) {
            return;
        }


        if (explanationTitle) {

            explanationTitle.textContent =
                `${flow.src} → ${flow.dst}`;

        }


        const shapList =
            document.querySelector(".shap-list");


        const attentionList =
            document.querySelector(".attention-list");


        if (shapList) {

            shapList.innerHTML = `

                <div class="explanation-item">

                    <div class="explanation-item-top">
                        <span>Flow Duration</span>
                        <strong class="explanation-value">
                            +0.31
                        </strong>
                    </div>

                    <div class="impact-bar">
                        <div
                            class="impact-fill"
                            style="width:82%">
                        </div>
                    </div>

                </div>


                <div class="explanation-item">

                    <div class="explanation-item-top">
                        <span>Destination Port</span>
                        <strong class="explanation-value">
                            +0.27
                        </strong>
                    </div>

                    <div class="impact-bar">
                        <div
                            class="impact-fill"
                            style="width:71%">
                        </div>
                    </div>

                </div>


                <div class="explanation-item">

                    <div class="explanation-item-top">
                        <span>Packet Rate</span>
                        <strong class="explanation-value">
                            +0.22
                        </strong>
                    </div>

                    <div class="impact-bar">
                        <div
                            class="impact-fill"
                            style="width:63%">
                        </div>
                    </div>

                </div>

            `;

        }


        if (attentionList) {

            attentionList.innerHTML = `

                <div class="explanation-item">

                    <div class="explanation-item-top">
                        <span>Temporal Pattern</span>
                        <strong>0.91</strong>
                    </div>

                    <div class="impact-bar">
                        <div
                            class="impact-fill"
                            style="width:91%">
                        </div>
                    </div>

                </div>


                <div class="explanation-item">

                    <div class="explanation-item-top">
                        <span>Connection Sequence</span>
                        <strong>0.84</strong>
                    </div>

                    <div class="impact-bar">
                        <div
                            class="impact-fill"
                            style="width:84%">
                        </div>
                    </div>

                </div>

            `;

        }


        explanationPanel.hidden = false;


        explanationPanel.scrollIntoView({
            behavior: "smooth"
        });

    }


    /* =========================
       CLOSE EXPLANATION
       ========================= */

    if (explanationClose) {

        explanationClose.addEventListener(
            "click",
            () => {

                explanationPanel.hidden = true;

            }
        );

    }


    /* =========================
       SEARCH
       ========================= */

    if (searchInput) {

        searchInput.addEventListener(
            "input",
            filterTable
        );

    }


    if (stageFilter) {

        stageFilter.addEventListener(
            "change",
            filterTable
        );

    }


    function filterTable() {

        const search =
            searchInput
                ? searchInput.value.toLowerCase()
                : "";


        const selectedStage =
            stageFilter
                ? stageFilter.value
                : "all";


        const rows =
            document.querySelectorAll(
                "#threatTableBody tr"
            );


        rows.forEach(row => {

            const text =
                row.textContent.toLowerCase();


            const matchesSearch =
                text.includes(search);


            const matchesStage =
                selectedStage === "all" ||
                text.includes(
                    selectedStage.toLowerCase()
                );


            row.style.display =
                matchesSearch &&
                matchesStage
                    ? ""
                    : "none";

        });

    }


    /* =========================
       SORT TABLE
       ========================= */

    const tableHeaders =
        document.querySelectorAll(
            "#threatTable th"
        );


    tableHeaders.forEach(
        (header, columnIndex) => {

            header.addEventListener(
                "click",
                () => {

                    if (
                        columnIndex === 4
                    ) {

                        analysisResults.sort(
                            (a, b) =>
                                b.risk - a.risk
                        );

                        renderResults();

                    }

                }
            );

        }
    );


    /* =========================
       PROBABILITY CHART
       ========================= */

    function drawProbabilityChart() {

        if (!probabilityChart) {
            return;
        }


        const canvas =
            probabilityChart;


        const ctx =
            canvas.getContext("2d");


        const rect =
            canvas.getBoundingClientRect();


        const dpr =
            window.devicePixelRatio || 1;


        canvas.width =
            rect.width * dpr;


        canvas.height =
            rect.height * dpr;


        ctx.scale(dpr, dpr);


        const width =
            rect.width;


        const height =
            rect.height;


        ctx.clearRect(
            0,
            0,
            width,
            height
        );


        const values = [
            18, 22, 25, 31,
            29, 38, 43, 51,
            57, 54, 66, 71,
            69, 78, 84, 91
        ];


        const points = [];


        values.forEach(
            (value, index) => {

                const x =
                    25 +
                    (
                        index /
                        (values.length - 1)
                    ) *
                    (width - 50);


                const y =
                    height -
                    25 -
                    (
                        value / 100
                    ) *
                    (height - 50);


                points.push({
                    x,
                    y
                });

            }
        );


        /* GRID */

        ctx.strokeStyle =
            "rgba(130,146,165,.12)";

        ctx.lineWidth = 1;


        for (
            let i = 0;
            i <= 4;
            i++
        ) {

            const y =
                20 +
                i *
                (
                    (height - 40) / 4
                );


            ctx.beginPath();

            ctx.moveTo(
                0,
                y
            );

            ctx.lineTo(
                width,
                y
            );

            ctx.stroke();

        }


        /* AREA */

        ctx.beginPath();

        ctx.moveTo(
            points[0].x,
            height - 25
        );


        points.forEach(point => {

            ctx.lineTo(
                point.x,
                point.y
            );

        });


        ctx.lineTo(
            points[points.length - 1].x,
            height - 25
        );


        ctx.closePath();


        ctx.fillStyle =
            "rgba(0,229,255,.06)";

        ctx.fill();


        /* LINE */

        ctx.beginPath();


        points.forEach(
            (point, index) => {

                if (index === 0) {

                    ctx.moveTo(
                        point.x,
                        point.y
                    );

                } else {

                    ctx.lineTo(
                        point.x,
                        point.y
                    );

                }

            }
        );


        ctx.strokeStyle =
            "#00e5ff";

        ctx.lineWidth = 2.5;

        ctx.stroke();


        /* POINTS */

        points.forEach(point => {

            ctx.beginPath();

            ctx.arc(
                point.x,
                point.y,
                3,
                0,
                Math.PI * 2
            );

            ctx.fillStyle =
                "#00e5ff";

            ctx.fill();

        });

    }


    /* =========================
       TIME BUTTONS
       ========================= */

    const timeButtons =
        document.querySelectorAll(
            ".time-button"
        );


    timeButtons.forEach(button => {

        button.addEventListener(
            "click",
            () => {

                timeButtons.forEach(
                    item =>
                        item.classList.remove(
                            "active"
                        )
                );


                button.classList.add(
                    "active"
                );


                drawProbabilityChart();

            }
        );

    });


    /* =========================
       BASELINE TOGGLE
       ========================= */

    if (baselineToggle) {

        baselineToggle.addEventListener(
            "change",
            () => {

                const baselineCard =
                    document.querySelector(
                        ".baseline-card"
                    );


                if (baselineCard) {

                    baselineCard.style.display =
                        baselineToggle.checked
                            ? ""
                            : "none";

                }

            }
        );

    }

/* =========================
   CSV EXPORT
   ========================= */

if (exportCsvButton) {

    exportCsvButton.addEventListener(
        "click",
        exportCSV
    );

}


function exportCSV() {

    if (analysisResults.length === 0) {

        showToast(
            "Nothing to Export",
            "Run an analysis first."
        );

        return;
    }

    const header = [
        "Source IP",
        "Destination IP",
        "Port",
        "Protocol",
        "Risk Score",
        "Predicted Stage"
    ];

    const rows = analysisResults.map(flow => [

        flow.src,
        flow.dst,
        flow.port,
        flow.protocol,
        flow.risk + "%",
        flow.stage

    ]);

    const csv =
        [header, ...rows]
        .map(row => row.join(","))
        .join("\n");


    const blob = new Blob(
        [csv],
        {
            type: "text/csv"
        }
    );


    const url =
        URL.createObjectURL(blob);


    const link =
        document.createElement("a");

    link.href = url;

    link.download =
        "NetGuard_AI_Threat_Report.csv";

    link.click();


    URL.revokeObjectURL(url);


    showToast(
        "CSV Exported",
        "Threat analysis report downloaded."
    );

}


/* =========================
   PDF REPORT
   ========================= */

if (exportPdfButton) {

    exportPdfButton.addEventListener(
        "click",
        exportPDF
    );

}


function exportPDF() {

    if (analysisResults.length === 0) {

        showToast(
            "Nothing to Export",
            "Run an analysis first."
        );

        return;
    }


    const reportWindow =
        window.open("", "_blank");


    if (!reportWindow) {

        showToast(
            "Popup Blocked",
            "Please allow popups for the PDF report."
        );

        return;
    }


    const rows =
        analysisResults.map(flow => `

            <tr>
                <td>${flow.src}</td>
                <td>${flow.dst}</td>
                <td>${flow.port}</td>
                <td>${flow.protocol}</td>
                <td>${flow.risk}%</td>
                <td>${flow.stage}</td>
            </tr>

        `).join("");


    reportWindow.document.write(`

        <html>

        <head>

            <title>
                NetGuard AI Threat Report
            </title>

            <style>

                body {
                    font-family: Arial, sans-serif;
                    padding: 35px;
                    color: #111;
                }

                h1 {
                    margin-bottom: 5px;
                }

                p {
                    color: #555;
                }

                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 25px;
                }

                th,
                td {
                    padding: 10px;
                    border: 1px solid #ccc;
                    text-align: left;
                }

                th {
                    background: #eee;
                }

            </style>

        </head>

        <body>

            <h1>NetGuard AI</h1>

            <h2>
                Network Threat Analysis Report
            </h2>

            <p>
                SIH 26153 — AI based Network
                Attack Forecasting
            </p>

            <p>
                Generated locally by NetGuard AI.
            </p>

            <table>

                <thead>

                    <tr>
                        <th>Source</th>
                        <th>Destination</th>
                        <th>Port</th>
                        <th>Protocol</th>
                        <th>Risk</th>
                        <th>Stage</th>
                    </tr>

                </thead>

                <tbody>
                    ${rows}
                </tbody>

            </table>

        </body>

        </html>

    `);


    reportWindow.document.close();


    setTimeout(() => {

        reportWindow.print();

    }, 500);


    showToast(
        "PDF Report Ready",
        "Choose 'Save as PDF' in the print window."
    );

}


/* =========================
   WINDOW RESIZE
   ========================= */

window.addEventListener(
    "resize",
    () => {

        if (analysisResults.length > 0) {

            drawProbabilityChart();

        }

    }
);


/* =========================
   FINAL STATUS
   ========================= */

console.log(
    "NetGuard AI analysis engine loaded successfully."
);

});
