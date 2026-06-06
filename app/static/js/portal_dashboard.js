const searchInput = document.querySelector("[data-portal-search]");
const appGrid = document.querySelector("[data-apps-grid]");
const appCards = [...document.querySelectorAll("[data-resource-card]")];
const appsEmptyStates = [...document.querySelectorAll("[data-apps-empty]")];
const viewButtons = [...document.querySelectorAll("[data-view-mode]")];
const launcherButtons = [...document.querySelectorAll("[data-open-launcher]")];
const terminalButtons = [...document.querySelectorAll("[data-open-terminal]")];
const terminalPanel = document.querySelector("[data-terminal-panel]");
const terminalClose = document.querySelector("[data-close-terminal]");
const terminalForm = document.querySelector("[data-terminal-form]");
const terminalInput = document.querySelector("[data-terminal-input]");
const terminalOutput = document.querySelector("[data-terminal-output]");
const monitorLines = document.querySelector("[data-monitor-lines]");
const appsSection = document.getElementById("apps-section");
const terminalSection = document.getElementById("terminal-section");
const viewStorageKey = "nasportal.appView";

function setViewMode(mode) {
    if (!appGrid) {
        return;
    }

    const nextMode = mode === "cards" ? "cards" : "icons";
    appGrid.dataset.view = nextMode;
    viewButtons.forEach((button) => {
        button.classList.toggle("is-active", button.dataset.viewMode === nextMode);
    });
    localStorage.setItem(viewStorageKey, nextMode);
}

function filterResources() {
    const query = (searchInput?.value || "").trim().toLowerCase();
    let visibleCount = 0;

    appCards.forEach((element) => {
        const haystack = (element.dataset.search || "").toLowerCase();
        const matches = !query || haystack.includes(query);
        element.classList.toggle("is-filtered", !matches);
        visibleCount += Number(matches);
    });

    if (appCards.length) {
        appsEmptyStates.forEach((element) => {
            element.classList.toggle("is-hidden", visibleCount !== 0);
        });
    }

    return visibleCount;
}

function firstVisibleApp() {
    return appCards.find((card) => !card.classList.contains("is-filtered"));
}

function focusSearch(event) {
    const target = event.target;
    if (target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement) {
        return;
    }

    if (event.key === "/" || (event.key.toLowerCase() === "k" && (event.ctrlKey || event.metaKey))) {
        event.preventDefault();
        searchInput?.focus();
        searchInput?.select();
    }
}

function appendTerminalLine(text, prompt = false) {
    if (!terminalOutput) {
        return;
    }

    const line = document.createElement("p");
    if (prompt) {
        const span = document.createElement("span");
        span.textContent = "nasportal:~$ ";
        line.append(span, text);
    } else {
        line.textContent = text;
    }
    terminalOutput.appendChild(line);
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

function openTerminal() {
    terminalPanel?.classList.remove("is-hidden");
    terminalSection?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    setTimeout(() => terminalInput?.focus(), 120);
}

function closeTerminal() {
    terminalPanel?.classList.add("is-hidden");
}

function listApps() {
    const names = appCards.map((card) => card.dataset.appTitle).filter(Boolean);
    appendTerminalLine(names.length ? names.join(", ") : "No apps available.");
}

function openAppByName(name) {
    const target = name.trim().toLowerCase();
    const match = appCards.find((card) => {
        return (card.dataset.appTitle || "").toLowerCase().includes(target);
    });

    if (!match) {
        appendTerminalLine(`App not found: ${name}`);
        return;
    }

    appendTerminalLine(`Opening ${match.dataset.appTitle}...`);
    window.open(match.href, "_blank", "noreferrer");
}

function runTerminalCommand(command) {
    const normalized = command.trim();
    if (!normalized) {
        return;
    }

    appendTerminalLine(normalized, true);
    const [verb, ...rest] = normalized.split(/\s+/);
    const argument = rest.join(" ");

    switch (verb.toLowerCase()) {
        case "help":
            appendTerminalLine("Commands: help, apps, open <name>, admin, logout");
            break;
        case "apps":
            listApps();
            break;
        case "open":
            argument ? openAppByName(argument) : appendTerminalLine("Usage: open <name>");
            break;
        case "admin":
            window.location.href = "/admin";
            break;
        case "logout":
        case "lock":
            window.location.href = "/auth/logout";
            break;
        default:
            openAppByName(normalized);
            break;
    }
}

function updateMetric(metric) {
    const card = document.querySelector(`[data-metric-card="${metric.key}"]`);
    if (!card) {
        return;
    }

    const value = card.querySelector("[data-metric-value]");
    const unit = card.querySelector("[data-metric-unit]");
    const fill = card.querySelector("[data-metric-fill]");
    if (value) {
        value.textContent = metric.display;
    }
    if (unit) {
        unit.textContent = metric.unit;
    }
    if (fill) {
        fill.style.width = `${Math.min(Math.max(metric.progress, 0), 100)}%`;
    }
}

async function refreshStatus() {
    try {
        const response = await fetch("/api/vps/status", {
            headers: { Accept: "application/json" },
        });
        if (!response.ok) {
            return;
        }

        const payload = await response.json();
        payload.metrics?.forEach(updateMetric);
        if (monitorLines && payload.monitor?.lines) {
            monitorLines.replaceChildren(
                ...payload.monitor.lines.map((line) => {
                    const node = document.createElement("p");
                    node.textContent = line;
                    return node;
                }),
            );
        }
    } catch {
        // Keep the last known values if the status endpoint is temporarily unavailable.
    }
}

setViewMode(localStorage.getItem(viewStorageKey) || "icons");
filterResources();
refreshStatus();
setInterval(refreshStatus, 5000);

searchInput?.addEventListener("input", filterResources);
searchInput?.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        const match = firstVisibleApp();
        if (match) {
            window.open(match.href, "_blank", "noreferrer");
        }
    }
});
document.addEventListener("keydown", focusSearch);

viewButtons.forEach((button) => {
    button.addEventListener("click", () => setViewMode(button.dataset.viewMode || "icons"));
});

launcherButtons.forEach((button) => {
    button.addEventListener("click", () => {
        appsSection?.scrollIntoView({ behavior: "smooth", block: "nearest" });
        searchInput?.focus();
    });
});

terminalButtons.forEach((button) => {
    button.addEventListener("click", openTerminal);
});
terminalClose?.addEventListener("click", closeTerminal);
terminalForm?.addEventListener("submit", (event) => {
    event.preventDefault();
    runTerminalCommand(terminalInput?.value || "");
    if (terminalInput) {
        terminalInput.value = "";
    }
});
