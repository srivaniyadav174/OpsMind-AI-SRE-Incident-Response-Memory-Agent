const API_BASE = "";

let currentIncidentId = "INC-007";
let currentDiagnosis = null;


/* =========================================================
   DOM HELPERS
========================================================= */

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


function setText(id, value) {
    const element = getElement(id);

    if (element) {
        element.textContent =
            value === null || value === undefined
                ? ""
                : String(value);
    }
}


/* =========================================================
   API
========================================================= */

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
    } catch {
        throw new Error(
            `Server returned an invalid response (${response.status}).`
        );
    }

    if (!response.ok) {

        throw new Error(
            data.detail ||
            `Request failed with status ${response.status}.`
        );
    }

    return data;
}


/* =========================================================
   LOAD INCIDENT
========================================================= */

async function loadIncident(incidentId = currentIncidentId) {

    currentIncidentId = incidentId;

    resetInvestigationState();

    const symptomsContainer =
        getElement("symptomsContainer");

    if (symptomsContainer) {

        symptomsContainer.innerHTML = `
            <div class="signal-loading">
                Loading incident evidence...
            </div>
        `;
    }

    try {

        const response =
            await apiRequest(
                `/incidents/${encodeURIComponent(incidentId)}`
            );

        const incident =
            response.incident;

        updateIncidentHeader(incident);

        updateMetrics(
            incident.metrics
        );

        renderSymptoms(
            incident.symptoms
        );

    } catch (error) {

        console.error(
            "Incident loading failed:",
            error
        );

        if (symptomsContainer) {

            symptomsContainer.innerHTML = `
                <div class="signal-loading">
                    Failed to load incident:
                    ${escapeHtml(error.message)}
                </div>
            `;
        }

        showError(
            `Could not load incident: ${error.message}`
        );
    }
}


/* =========================================================
   INCIDENT HEADER
========================================================= */

function updateIncidentHeader(incident) {

    setText(
        "serviceName",
        incident.service || "Unknown service"
    );

    setText(
        "incidentId",
        incident.incident_id || currentIncidentId
    );

    setText(
        "severityBadge",
        incident.severity
            ? incident.severity.toUpperCase()
            : "UNKNOWN"
    );

    setText(
        "incidentStatus",
        "Awaiting investigation"
    );

    setText(
        "currentMemoryIncident",
        incident.incident_id || currentIncidentId
    );

    setText(
        "currentMemoryService",
        incident.service || "Unknown service"
    );

    setText(
        "resolutionIncident",
        incident.incident_id || currentIncidentId
    );

    setText(
        "learningIncident",
        incident.incident_id || currentIncidentId
    );

    setText(
        "learningService",
        incident.service || "Unknown service"
    );
}


/* =========================================================
   METRICS
========================================================= */

function updateMetrics(metrics) {

    if (!metrics) {
        return;
    }

    setText(
        "latencyMetric",
        `${metrics.latency_seconds}s`
    );

    setText(
        "errorMetric",
        `${metrics.error_rate_percent}%`
    );

    setText(
        "dbMetric",
        `${metrics.db_connection_utilization_percent}%`
    );


    setText(
        "latencyTrend",
        metrics.latency_seconds >= 3
            ? "▲ Critical"
            : "Elevated"
    );

    setText(
        "errorTrend",
        metrics.error_rate_percent >= 10
            ? "▲ Critical"
            : "Elevated"
    );

    setText(
        "dbTrend",
        metrics.db_connection_utilization_percent >= 90
            ? "▲ Saturated"
            : "Elevated"
    );


    const latencyBar =
        getElement("latencyBar");

    if (latencyBar) {

        latencyBar.style.width =
            `${Math.min(
                100,
                Number(metrics.latency_seconds) / 6 * 100
            )}%`;
    }


    const errorBar =
        getElement("errorBar");

    if (errorBar) {

        errorBar.style.width =
            `${Math.min(
                100,
                Number(metrics.error_rate_percent)
            )}%`;
    }


    const dbBar =
        getElement("dbBar");

    if (dbBar) {

        dbBar.style.width =
            `${Math.min(
                100,
                Number(metrics.db_connection_utilization_percent)
            )}%`;
    }


    /*
     * Presentation-only incident health score.
     */

    const latencyPenalty =
        Math.min(
            100,
            Number(metrics.latency_seconds) * 10
        );

    const errorPenalty =
        Math.min(
            100,
            Number(metrics.error_rate_percent) * 2
        );

    const dbPenalty =
        Number(metrics.db_connection_utilization_percent);

    const health =
        Math.max(
            0,
            Math.round(
                100 -
                (
                    latencyPenalty * 0.25 +
                    errorPenalty * 0.30 +
                    dbPenalty * 0.45
                )
            )
        );

    setText(
        "healthScore",
        health
    );

    setText(
        "healthStatus",
        health < 30
            ? "Critical degradation"
            : health < 60
                ? "Degraded"
                : "Stable"
    );

    const healthBar =
        getElement("healthBar");

    if (healthBar) {

        healthBar.style.width =
            `${health}%`;
    }
}


/* =========================================================
   SYMPTOMS
========================================================= */

function renderSymptoms(symptoms) {

    const container =
        getElement("symptomsContainer");

    if (!container) {
        return;
    }

    if (!Array.isArray(symptoms) || symptoms.length === 0) {

        container.innerHTML = `
            <div class="signal-loading">
                No symptoms available.
            </div>
        `;

        return;
    }


    /*
     * Render only into the primary symptoms container.
     *
     * The newer signalTimeline element is intentionally
     * not populated to prevent duplicate signals.
     */

    container.innerHTML = `
        <div class="signal-timeline">

            <div class="timeline-line"></div>

            ${symptoms.map((symptom, index) => {

                let dotClass = "";

                if (index === symptoms.length - 1) {
                    dotClass = "critical-dot";
                } else if (index >= symptoms.length - 2) {
                    dotClass = "danger-dot";
                }

                return `
                    <div class="timeline-item">

                        <div class="timeline-dot ${dotClass}">
                        </div>

                        <div>
                            <strong>
                                Signal ${String(index + 1).padStart(2, "0")}
                            </strong>

                            <span>
                                ${escapeHtml(symptom)}
                            </span>
                        </div>

                    </div>
                `;

            }).join("")}

        </div>
    `;
}


/* =========================================================
   ANALYZE
========================================================= */

async function analyzeIncident() {

    const button =
        getElement("analyzeButton");

    if (button) {

        button.disabled = true;

        button.innerHTML = `
            <span class="action-button-icon">⟳</span>
            Analyzing incident...
        `;
    }


    setText(
        "incidentStatus",
        "OpsMind is investigating..."
    );


    try {

        const response =
            await apiRequest(
                `/incidents/${encodeURIComponent(
                    currentIncidentId
                )}/analyze`,
                {
                    method: "POST"
                }
            );


        const data =
            response.data;


        currentDiagnosis =
            data.diagnosis || null;


        if (!currentDiagnosis) {

            throw new Error(
                "The backend returned no diagnosis."
            );
        }


        renderDiagnosis(
            currentDiagnosis
        );

        renderMemory(
            currentDiagnosis
        );

        renderRunbook(
            currentDiagnosis
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


        setText(
            "incidentStatus",
            "Diagnosis ready — awaiting human approval"
        );


        if (button) {

            button.disabled = false;

            button.innerHTML = `
                <span class="action-button-icon">✓</span>
                Analysis Complete
            `;
        }


        scrollToSection(
            "diagnosisSection"
        );

    } catch (error) {

        console.error(
            "Incident analysis failed:",
            error
        );


        setText(
            "incidentStatus",
            "Analysis failed"
        );


        if (button) {

            button.disabled = false;

            button.innerHTML = `
                <span class="action-button-icon">↻</span>
                Analyze Incident
            `;
        }


        showError(
            `OpsMind could not analyze the incident: ${error.message}`
        );
    }
}


/* =========================================================
   DIAGNOSIS
========================================================= */

function renderDiagnosis(diagnosis) {

    if (!diagnosis) {
        return;
    }


    setText(
        "rootCause",
        diagnosis.likely_root_cause || "Unknown"
    );


    setText(
        "confidenceValue",
        diagnosis.confidence || "Unknown"
    );


    setText(
        "reasoningText",
        diagnosis.reasoning ||
        "No reasoning available."
    );


    /*
     * Confidence bar.
     */

    const confidenceBar =
        getElement("confidenceBar");

    if (confidenceBar) {

        const confidence =
            String(
                diagnosis.confidence || ""
            ).toLowerCase();

        let width = 60;

        if (confidence.includes("high")) {
            width = 90;
        } else if (confidence.includes("medium")) {
            width = 70;
        } else if (confidence.includes("low")) {
            width = 40;
        }

        confidenceBar.style.width =
            `${width}%`;
    }


    /*
     * Evidence.
     */

    const evidenceList =
        getElement("evidenceList");

    const evidence =
        Array.isArray(diagnosis.evidence)
            ? diagnosis.evidence
            : [];


    if (evidenceList) {

        if (evidence.length === 0) {

            evidenceList.innerHTML = `
                <div class="loading">
                    No evidence available.
                </div>
            `;

        } else {

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
    }


    setText(
        "evidenceCount",
        evidence.length || "—"
    );
}


/* =========================================================
   HISTORICAL MEMORY PARSER
========================================================= */

function parseHistoricalMemory(text) {

    if (!text) {
        return [];
    }


    if (
        text.includes(
            "No similar historical incidents found"
        )
    ) {
        return [];
    }


    const memories = [];


    /*
     * Case 1:
     *
     * Historical Incident: INC-007
     *
     * This is the preferred backend format.
     */

    const explicitPattern =
        /Historical Incident:\s*(INC-\d+|UNKNOWN)\s*([\s\S]*?)(?=Historical Incident:\s*INC-\d+|Historical Incident:\s*UNKNOWN|$)/gi;


    let match;

    while (
        (match = explicitPattern.exec(text)) !== null
    ) {

        memories.push({
            incident:
                match[1].toUpperCase(),

            text:
                match[2].trim()
        });
    }


    /*
     * Case 2:
     *
     * Current backend can return a combined paragraph:
     *
     * "Historical incidents INC-001 and INC-007..."
     */

    const incidentIds =
        [
            ...new Set(
                (
                    text.match(
                        /INC-\d+/gi
                    ) || []
                )
                    .map(
                        id => id.toUpperCase()
                    )
            )
        ];


    if (incidentIds.length > 0) {

        incidentIds.forEach(
            incidentId => {

                /*
                 * Never classify the current incident
                 * as historical.
                 */

                if (
                    incidentId ===
                    currentIncidentId
                ) {
                    return;
                }


                /*
                 * Avoid duplicates.
                 */

                const alreadyExists =
                    memories.some(
                        memory =>
                            memory.incident ===
                            incidentId
                    );


                if (!alreadyExists) {

                    memories.push({
                        incident:
                            incidentId,

                        text:
                            text
                                .replace(
                                    /\bUNKNOWN:\s*/i,
                                    ""
                                )
                                .trim()
                    });
                }
            }
        );
    }


    /*
     * Remove UNKNOWN when real incident IDs exist.
     */

    const realIncidentMemories =
        memories.filter(
            memory =>
                /^INC-\d+$/i.test(
                    memory.incident
                )
        );


    if (realIncidentMemories.length > 0) {

        return realIncidentMemories;
    }


    return memories;
}


/* =========================================================
   HINDSIGHT MEMORY
========================================================= */

function renderMemory(diagnosis) {

    const container =
        getElement("memoryContainer");


    const historicalContext =
        diagnosis.historical_context ||
        "";


    /*
     * -----------------------------------------------------
     * CURRENT INCIDENT
     * -----------------------------------------------------
     */

    const currentId =
        currentIncidentId;


    setText(
        "currentMemoryIncident",
        currentId
    );


    const serviceElement =
        getElement("serviceName");


    const currentService =
        serviceElement
            ? serviceElement.textContent.trim()
            : "service";


    setText(
        "currentMemoryService",
        currentService
    );


    /*
     * -----------------------------------------------------
     * EXTRACT REAL HISTORICAL INCIDENT IDS
     * -----------------------------------------------------
     *
     * We intentionally extract actual incident IDs directly
     * from the Hindsight context.
     *
     * This prevents UNKNOWN from appearing as a historical
     * incident and prevents duplicate memory cards.
     */

    const incidentMatches =
        historicalContext.match(
            /INC-\d{3}/gi
        ) || [];


    const historicalIncidentIds =
        [
            ...new Set(
                incidentMatches
                    .map(
                        id => id.toUpperCase()
                    )
                    .filter(
                        id =>
                            id !== currentId.toUpperCase()
                    )
            )
        ];


    const memoryFound =
        historicalIncidentIds.length > 0;


    /*
     * -----------------------------------------------------
     * MEMORY MATCH
     * -----------------------------------------------------
     */

    setText(
        "memoryMatch",
        memoryFound
            ? "FOUND"
            : "NO MATCH"
    );


    /*
     * -----------------------------------------------------
     * HISTORICAL MEMORY INCIDENTS
     * -----------------------------------------------------
     */

    setText(
        "historicalMemoryIncident",
        memoryFound
            ? historicalIncidentIds.join(" + ")
            : "NO PRIOR MATCH"
    );


    /*
     * -----------------------------------------------------
     * LEARNED FIX
     * -----------------------------------------------------
     */

    let learnedFix =
        "Previous incidents provide relevant operational context.";


    if (
        /increase|increased|pool size|pool capacity|connection pool/i.test(
            historicalContext
        )
    ) {

        learnedFix =
            "Increase database connection pool capacity and restart the affected service.";
    }


    /*
     * -----------------------------------------------------
     * HISTORICAL CONTEXT
     * -----------------------------------------------------
     */

    const historicalContextElement =
        getElement("historicalContext");


    if (historicalContextElement) {

        if (memoryFound) {

            historicalContextElement.textContent =
                historicalContext;

        } else {

            historicalContextElement.textContent =
                "No similar historical incidents found.";
        }
    }


    /*
     * Show historical context only when an actual
     * previous incident was found.
     */

    if (memoryFound) {

        showElement(
            "historicalContextSection"
        );

    } else {

        hideElement(
            "historicalContextSection"
        );
    }


    /*
     * -----------------------------------------------------
     * MEMORY CONTAINER
     * -----------------------------------------------------
     */

    if (!container) {
        return;
    }


    if (!memoryFound) {

        container.innerHTML = `
            <div class="memory-card">

                <div class="memory-card-header">

                    <strong>
                        NO PRIOR MATCH
                    </strong>

                    <span>
                        HINDSIGHT
                    </span>

                </div>


                <div class="memory-card-learning">

                    <strong>
                        MEMORY STATUS
                    </strong>

                    <p>
                        No directly relevant historical
                        incident was found for this investigation.
                    </p>

                </div>

            </div>
        `;

        return;
    }


    /*
     * -----------------------------------------------------
     * CLEAN HINDSIGHT MEMORY CARD
     * -----------------------------------------------------
     */

    container.innerHTML = `

        <div class="memory-card">

            <div class="memory-card-header">

                <strong>
                    HISTORICAL MEMORY
                </strong>

                <span>
                    HINDSIGHT
                </span>

            </div>


            <div class="memory-card-incidents">

                <div class="memory-incident">

                    <strong>
                        ${escapeHtml(
                            historicalIncidentIds.join(" + ")
                        )}
                    </strong>

                    <span>
                        Similar ${escapeHtml(
                            currentService
                        )} incident
                    </span>

                </div>

            </div>


            <div class="memory-card-learning">

                <strong>
                    LEARNED FIX
                </strong>

                <p>
                    ${escapeHtml(
                        learnedFix
                    )}
                </p>

            </div>


            <div class="memory-card-source">

                <strong>
                    MEMORY CONTEXT
                </strong>

                <p>
                    ${escapeHtml(
                        historicalContext
                    )}
                </p>

            </div>

        </div>
    `;
}


/* =========================================================
   RUNBOOK
========================================================= */

function renderRunbook(diagnosis) {

    const runbook =
        diagnosis.runbook;


    if (!runbook) {
        return;
    }


    setText(
        "runbookTitle",
        runbook.title ||
        "Recommended Runbook"
    );


    setText(
        "runbookDescription",
        "OpsMind recommends the following remediation sequence based on the current evidence and historical outcomes."
    );


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

                            <div class="step-content">

                                <strong>
                                    ${escapeHtml(
                                        step.action
                                    )}
                                </strong>

                                <span>
                                    Simulated operation
                                </span>

                            </div>

                            <div class="step-state">
                                Ready
                            </div>

                        </div>
                    `
                )
                .join("");
    }


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
                verification.length
                    ? verification
                        .map(
                            item => `
                                <div class="verification-item">
                                    ✓
                                    ${escapeHtml(item)}
                                </div>
                            `
                        )
                        .join("")
                    : `
                        <div class="verification-item">
                            ✓ API health and error rate verification
                        </div>

                        <div class="verification-item">
                            ✓ Database connection utilization verification
                        </div>
                    `
            }
        `;
    }
}


/* =========================================================
   RESOLVE / SIMULATE
========================================================= */

async function resolveIncident() {

    const button =
        getElement("resolveButton");


    if (!currentDiagnosis) {

        showError(
            "Analyze the incident before approving remediation."
        );

        return;
    }


    if (button) {

        button.disabled = true;

        button.innerHTML = `
            <span class="action-button-icon">⟳</span>
            Simulating remediation...
        `;
    }


    setText(
        "incidentStatus",
        "Running simulated remediation..."
    );


    try {

        const response =
            await apiRequest(
                `/incidents/${encodeURIComponent(
                    currentIncidentId
                )}/resolve`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        diagnosis:
                            currentDiagnosis
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


        setText(
            "incidentStatus",
            "Resolved — learning retained"
        );


        if (button) {

            button.innerHTML = `
                <span class="action-button-icon">✓</span>
                Resolution Simulated
            `;

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


        setText(
            "incidentStatus",
            "Resolution simulation failed"
        );


        if (button) {

            button.disabled = false;

            button.innerHTML = `
                <span class="action-button-icon">↗</span>
                Approve & Simulate Resolution
            `;
        }


        showError(
            `OpsMind could not resolve the incident: ${error.message}`
        );
    }
}


/* =========================================================
   RESOLUTION
========================================================= */

function renderResolution(result) {

    setText(
        "resolutionOutcome",
        result.outcome ||
        "Simulated remediation completed."
    );


    const resolutionActions =
        getElement("resolutionActions");


    if (
        resolutionActions &&
        Array.isArray(result.actions)
    ) {

        resolutionActions.innerHTML =
            result.actions
                .map(
                    action => `
                        <div class="learning-card">

                            <strong>
                                ${escapeHtml(action)}
                            </strong>

                        </div>
                    `
                )
                .join("");
    }


    setText(
        "resolutionIncident",
        currentIncidentId
    );


    const serviceElement =
        getElement("serviceName");


    if (serviceElement) {

        setText(
            "learningService",
            serviceElement.textContent
        );
    }


    setText(
        "learningIncident",
        currentIncidentId
    );


    setText(
        "learningRootCause",
        currentDiagnosis?.likely_root_cause ||
        "Database connection pool exhaustion"
    );
}


/* =========================================================
   RESET
========================================================= */

function resetInvestigationState() {

    currentDiagnosis = null;


    hideElement("diagnosisSection");
    hideElement("memorySection");
    hideElement("runbookSection");
    hideElement("approvalSection");
    hideElement("resolutionSection");
    hideElement("historicalContextSection");


    setText(
        "memoryMatch",
        "—"
    );


    setText(
        "historicalMemoryIncident",
        "—"
    );


    setText(
        "historicalContext",
        "Historical memory will appear here."
    );


    setText(
        "evidenceCount",
        "—"
    );


    const memoryContainer =
        getElement("memoryContainer");


    if (memoryContainer) {

        memoryContainer.innerHTML = `
            <div class="memory-card">

                <strong>
                    Ready to investigate
                </strong>

                <p>
                    OpsMind will inspect telemetry,
                    logs, runbooks and Hindsight memory.
                </p>

            </div>
        `;
    }


    const button =
        getElement("analyzeButton");


    if (button) {

        button.disabled = false;

        button.innerHTML = `
            <span class="action-button-icon">✦</span>
            Analyze Incident
            <span class="action-arrow">→</span>
        `;
    }


    setText(
        "incidentStatus",
        "Awaiting investigation"
    );
}


/* =========================================================
   ERROR
========================================================= */

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


    Object.assign(
        errorBox.style,
        {
            position: "fixed",
            bottom: "20px",
            left: "20px",
            right: "20px",
            zIndex: "9999",
            padding: "14px 18px",
            border: "1px solid rgba(255,92,108,0.3)",
            borderRadius: "10px",
            background: "#211015",
            color: "#ff9da7",
            fontSize: "12px",
            boxShadow: "0 15px 40px rgba(0,0,0,0.35)"
        }
    );


    errorBox.textContent =
        message;


    document.body.appendChild(
        errorBox
    );


    setTimeout(
        () => {

            if (errorBox.parentNode) {
                errorBox.remove();
            }

        },
        7000
    );
}


/* =========================================================
   ESCAPE HTML
========================================================= */

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }


    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/* =========================================================
   SCROLL
========================================================= */

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


/* =========================================================
   EVENTS
========================================================= */

function setupEventListeners() {

    const analyzeButton =
        getElement("analyzeButton");


    if (analyzeButton) {

        analyzeButton.addEventListener(
            "click",
            analyzeIncident
        );
    }


    const resolveButton =
        getElement("resolveButton");


    if (resolveButton) {

        resolveButton.addEventListener(
            "click",
            resolveIncident
        );
    }


    const incidentSelect =
        getElement("incidentSelect");


    if (incidentSelect) {

        incidentSelect.addEventListener(
            "change",
            event => {

                const selectedId =
                    event.target.value;


                if (selectedId) {

                    loadIncident(
                        selectedId
                    );
                }
            }
        );
    }
}


/* =========================================================
   INITIALIZE
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        setupEventListeners();


        const selector =
            getElement("incidentSelect");


        if (
            selector &&
            selector.value
        ) {

            loadIncident(
                selector.value
            );

        } else {

            loadIncident(
                currentIncidentId
            );
        }
    }
);