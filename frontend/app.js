const API_BASE = "";

const incidentId = "INC-007";


/* ========================================
   DOM HELPERS
======================================== */

function getElement(id) {
    return document.getElementById(id);
}


function showElement(id) {
    const element = getElement(id);

    if (element) {
        element.classList.remove("hidden");
    }
}


function hideElement(id) {
    const element = getElement(id);

    if (element) {
        element.classList.add("hidden");
    }
}


/* ========================================
   API HELPER
======================================== */

async function apiRequest(url, options = {}) {

    const response = await fetch(
        `${API_BASE}${url}`,
        {
            ...options,
            headers: {
                "Accept": "application/json",
                ...(options.headers || {})
            }
        }
    );

    let data;

    try {
        data = await response.json();
    } catch (error) {
        throw new Error(
            `Server returned an invalid response (${response.status}).`
        );
    }

    if (!response.ok) {

        const message =
            data.detail ||
            `Request failed with status ${response.status}.`;

        throw new Error(message);
    }

    return data;
}


/* ========================================
   LOAD INCIDENT
======================================== */

async function loadIncident() {

    const symptomsContainer =
        getElement("symptomsContainer");

    symptomsContainer.innerHTML = `
        <div class="loading">
            Loading incident evidence...
        </div>
    `;

    try {

        const response = await apiRequest(
            `/incidents/${incidentId}`
        );

        const incident = response.incident;

        updateIncidentHeader(incident);

        updateMetrics(incident.metrics);

        renderSymptoms(incident.symptoms);

    } catch (error) {

        symptomsContainer.innerHTML = `
            <div class="loading">
                Failed to load incident:
                ${escapeHtml(error.message)}
            </div>
        `;

        console.error(
            "Incident loading failed:",
            error
        );
    }
}


/* ========================================
   UPDATE INCIDENT HEADER
======================================== */

function updateIncidentHeader(incident) {

    const serviceName =
        getElement("serviceName");

    const incidentStatus =
        getElement("incidentStatus");

    if (serviceName) {
        serviceName.textContent =
            incident.service;
    }

    if (incidentStatus) {
        incidentStatus.textContent =
            "Awaiting investigation";
    }
}


/* ========================================
   UPDATE METRICS
======================================== */

function updateMetrics(metrics) {

    if (!metrics) {
        return;
    }

    const latency =
        getElement("latencyMetric");

    const errorRate =
        getElement("errorMetric");

    const dbUtilization =
        getElement("dbMetric");

    if (latency) {
        latency.textContent =
            `${metrics.latency_seconds}s`;
    }

    if (errorRate) {
        errorRate.textContent =
            `${metrics.error_rate_percent}%`;
    }

    if (dbUtilization) {
        dbUtilization.textContent =
            `${metrics.db_connection_utilization_percent}%`;
    }
}


/* ========================================
   RENDER SYMPTOMS
======================================== */

function renderSymptoms(symptoms) {

    const container =
        getElement("symptomsContainer");

    if (!container) {
        return;
    }

    if (!symptoms || symptoms.length === 0) {

        container.innerHTML = `
            <div class="loading">
                No symptoms available.
            </div>
        `;

        return;
    }

    container.innerHTML =
        symptoms
            .map(
                symptom => `
                    <div class="symptom">

                        <span class="symptom-marker"></span>

                        <span>
                            ${escapeHtml(symptom)}
                        </span>

                    </div>
                `
            )
            .join("");
}


/* ========================================
   ANALYZE INCIDENT
======================================== */

async function analyzeIncident() {

    const button =
        getElement("analyzeButton");

    const status =
        getElement("incidentStatus");

    if (button) {

        button.disabled = true;

        button.innerHTML =
            "◌ Analyzing incident...";
    }

    if (status) {
        status.textContent =
            "OpsMind is investigating...";
    }

    try {

        const response = await apiRequest(
            `/incidents/${incidentId}/analyze`,
            {
                method: "POST"
            }
        );

        const data = response.data;

        renderDiagnosis(
            data.diagnosis
        );

        renderMemory(
            data.diagnosis
        );

        renderRunbook(
            data.diagnosis
        );

        showElement(
            "diagnosisSection"
        );

        showElement(
            "memorySection"
        );

        showElement(
            "runbookSection"
        );

        showElement(
            "approvalSection"
        );

        if (status) {
            status.textContent =
                "Diagnosis ready — awaiting human approval";
        }

        if (button) {

            button.disabled = false;

            button.innerHTML =
                "✓ Analysis Complete";
        }

        scrollToSection(
            "diagnosisSection"
        );

    } catch (error) {

        console.error(
            "Incident analysis failed:",
            error
        );

        if (status) {
            status.textContent =
                "Analysis failed";
        }

        if (button) {

            button.disabled = false;

            button.innerHTML =
                "◉ Analyze Incident";
        }

        showError(
            `OpsMind could not analyze the incident: ${error.message}`
        );
    }
}


/* ========================================
   RENDER DIAGNOSIS
======================================== */

function renderDiagnosis(diagnosis) {

    if (!diagnosis) {
        return;
    }

    const rootCause =
        getElement("rootCause");

    const confidence =
        getElement("confidenceValue");

    const reasoning =
        getElement("reasoningText");

    if (rootCause) {

        rootCause.textContent =
            diagnosis.likely_root_cause ||
            "Unknown";
    }

    if (confidence) {

        confidence.textContent =
            diagnosis.confidence ||
            "Unknown";
    }

    if (reasoning) {

        reasoning.textContent =
            diagnosis.reasoning ||
            "No reasoning available.";
    }


    /* =========================
       EVIDENCE
    ========================== */

    const evidenceList =
        getElement("evidenceList");

    if (!evidenceList) {
        return;
    }

    const evidence =
        diagnosis.evidence || [];

    if (evidence.length === 0) {

        evidenceList.innerHTML = `
            <div class="loading">
                No evidence available.
            </div>
        `;

        return;
    }

    evidenceList.innerHTML =
        evidence
            .map(
                item => `
                    <div class="evidence-item">
                        ${escapeHtml(item)}
                    </div>
                `
            )
            .join("");
}


/* ========================================
   RENDER HINDSIGHT MEMORY
======================================== */

function renderMemory(diagnosis) {

    const container =
        getElement("memoryContainer");

    if (!container) {
        return;
    }

    const historicalContext =
        diagnosis.historical_context ||
        "";

    if (
        !historicalContext ||
        historicalContext.includes(
            "No similar historical incidents found"
        )
    ) {

        container.innerHTML = `
            <div class="memory-card">

                <div class="memory-card-header">

                    <span class="memory-incident">
                        NO MATCHING MEMORY
                    </span>

                    <span class="memory-tag">
                        HINDSIGHT
                    </span>

                </div>

                <p>
                    No relevant historical incidents
                    were found for this investigation.
                </p>

            </div>
        `;

        return;
    }


    /*
     * The current backend returns historical context
     * as readable text. We split it into historical
     * incident sections for the dashboard.
     */

    const sections =
        historicalContext
            .split(
                /\n\n|(?=Historical Incident:)/
            )
            .map(
                section => section.trim()
            )
            .filter(
                section => section.length > 0
            );


    const cards = [];

    sections.forEach(
        section => {

            const match =
                section.match(
                    /Historical Incident:\s*(INC-\d+|UNKNOWN)/
                );

            const incident =
                match
                    ? match[1]
                    : "Historical Memory";

            const text =
                section
                    .replace(
                        /Historical Incident:\s*(INC-\d+|UNKNOWN)/,
                        ""
                    )
                    .trim();

            if (
                incident === "UNKNOWN"
            ) {

                cards.push(`
                    <div class="memory-card">

                        <div class="memory-card-header">

                            <span class="memory-incident">
                                GENERAL SRE LESSON
                            </span>

                            <span class="memory-tag">
                                LEARNED
                            </span>

                        </div>

                        <p>
                            ${escapeHtml(text)}
                        </p>

                    </div>
                `);

            } else {

                cards.push(`
                    <div class="memory-card">

                        <div class="memory-card-header">

                            <span class="memory-incident">
                                ${escapeHtml(incident)}
                            </span>

                            <span class="memory-tag">
                                SIMILAR INCIDENT
                            </span>

                        </div>

                        <p>
                            ${escapeHtml(text)}
                        </p>

                    </div>
                `);
            }
        }
    );


    if (cards.length === 0) {

        container.innerHTML = `
            <div class="memory-card">

                <div class="memory-card-header">

                    <span class="memory-incident">
                        HINDSIGHT
                    </span>

                </div>

                <p>
                    Historical context was found,
                    but could not be displayed.
                </p>

            </div>
        `;

    } else {

        container.innerHTML =
            cards.join("");
    }
}


/* ========================================
   RENDER RUNBOOK
======================================== */

function renderRunbook(diagnosis) {

    const runbook =
        diagnosis.runbook;

    if (!runbook) {
        return;
    }

    const title =
        getElement("runbookTitle");

    if (title) {
        title.textContent =
            runbook.title ||
            "Recommended Runbook";
    }


    /* =========================
       PROCEDURE
    ========================== */

    const stepsContainer =
        getElement("runbookSteps");

    if (stepsContainer) {

        const procedure =
            runbook.procedure || [];

        stepsContainer.innerHTML =
            procedure
                .map(
                    step => `
                        <div class="runbook-step">

                            <div class="step-number">
                                ${escapeHtml(
                                    String(step.step)
                                )}
                            </div>

                            <div class="step-action">
                                ${escapeHtml(
                                    step.action
                                )}
                            </div>

                        </div>
                    `
                )
                .join("");
    }


    /* =========================
       VERIFICATION
    ========================== */

    const verificationContainer =
        getElement(
            "verificationContainer"
        );

    if (verificationContainer) {

        const verification =
            runbook.verification || [];

        verificationContainer.innerHTML = `
            <div class="verification-title">
                VERIFICATION CHECKS
            </div>

            ${
                verification
                    .map(
                        item => `
                            <div class="verification-item">
                                ✓
                                ${escapeHtml(item)}
                            </div>
                        `
                    )
                    .join("")
            }
        `;
    }
}


/* ========================================
   RESOLVE / SIMULATE
======================================== */

async function resolveIncident() {

    const button =
        getElement("resolveButton");

    const status =
        getElement("incidentStatus");

    if (button) {

        button.disabled = true;

        button.innerHTML =
            "⚡ Simulating remediation...";
    }

    if (status) {
        status.textContent =
            "Running simulated remediation...";
    }

    try {

        /*
         * The analyze response is already stored
         * in the page. We reconstruct the diagnosis
         * from the visible dashboard data.
         *
         * For the current hackathon prototype,
         * the backend accepts the diagnosis object.
         */

        const diagnosis =
            collectDiagnosisForResolution();


        const response = await apiRequest(
            `/incidents/${incidentId}/resolve`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    diagnosis: diagnosis
                })
            }
        );


        const result =
            response.data;


        renderResolution(
            result
        );


        showElement(
            "resolutionSection"
        );


        if (status) {
            status.textContent =
                "Resolved — learning retained";
        }


        if (button) {

            button.innerHTML =
                "✓ Resolution Simulated";

            button.disabled = true;
        }


        scrollToSection(
            "resolutionSection"
        );

    } catch (error) {

        console.error(
            "Resolution failed:",
            error
        );

        if (status) {
            status.textContent =
                "Resolution simulation failed";
        }

        if (button) {

            button.disabled = false;

            button.innerHTML =
                "⚡ Approve & Simulate Resolution";
        }

        showError(
            `OpsMind could not resolve the incident: ${error.message}`
        );
    }
}


/* ========================================
   COLLECT DIAGNOSIS
======================================== */

function collectDiagnosisForResolution() {

    const rootCause =
        getElement("rootCause")?.textContent ||
        "";

    const confidence =
        getElement("confidenceValue")?.textContent ||
        "";

    const reasoning =
        getElement("reasoningText")?.textContent ||
        "";

    const evidenceElements =
        document.querySelectorAll(
            ".evidence-item"
        );

    const evidence =
        Array.from(
            evidenceElements
        ).map(
            element =>
                element.textContent.trim()
        );


    const stepElements =
        document.querySelectorAll(
            ".runbook-step"
        );

    const procedure =
        Array.from(
            stepElements
        ).map(
            (element, index) => {

                const number =
                    element.querySelector(
                        ".step-number"
                    )?.textContent.trim();

                const action =
                    element.querySelector(
                        ".step-action"
                    )?.textContent.trim();

                return {
                    step:
                        Number(number) ||
                        index + 1,

                    action:
                        action || ""
                };
            }
        );


    const runbookTitle =
        getElement(
            "runbookTitle"
        )?.textContent ||
        "Database Connection Pool Exhaustion Runbook";


    return {

        likely_root_cause:
            rootCause,

        reasoning:
            reasoning,

        evidence:
            evidence,

        historical_context:
            "Historical context retrieved from Hindsight memory.",

        recommended_actions:
            procedure.map(
                item => item.action
            ),

        confidence:
            confidence,

        runbook: {

            title:
                runbookTitle,

            procedure:
                procedure,

            verification: [],

            simulation_only:
                true
        }
    };
}


/* ========================================
   RENDER RESOLUTION
======================================== */

function renderResolution(result) {

    const outcome =
        getElement("resolutionOutcome");

    if (outcome) {

        outcome.textContent =
            result.outcome ||
            "Simulated remediation completed.";
    }
}


/* ========================================
   ERROR DISPLAY
======================================== */

function showError(message) {

    const existing =
        document.querySelector(
            ".frontend-error"
        );

    if (existing) {
        existing.remove();
    }

    const errorBox =
        document.createElement("div");

    errorBox.className =
        "frontend-error";

    errorBox.style.position =
        "fixed";

    errorBox.style.bottom =
        "20px";

    errorBox.style.left =
        "20px";

    errorBox.style.right =
        "20px";

    errorBox.style.zIndex =
        "9999";

    errorBox.style.padding =
        "14px 18px";

    errorBox.style.border =
        "1px solid rgba(255,92,108,0.3)";

    errorBox.style.borderRadius =
        "8px";

    errorBox.style.background =
        "#211015";

    errorBox.style.color =
        "#ff9da7";

    errorBox.style.fontSize =
        "12px";

    errorBox.textContent =
        message;

    document.body.appendChild(
        errorBox
    );


    setTimeout(
        () => {

            errorBox.remove();

        },
        7000
    );
}


/* ========================================
   HTML ESCAPING
======================================== */

function escapeHtml(value) {

    if (value === null ||
        value === undefined) {

        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/* ========================================
   SCROLL
======================================== */

function scrollToSection(id) {

    const element =
        getElement(id);

    if (!element) {
        return;
    }

    setTimeout(
        () => {

            element.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        },
        150
    );
}


/* ========================================
   INITIALIZE
======================================== */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadIncident();

    }
);