let logsStore = [];

function openModal() {
  document.getElementById("add-log-modal").classList.remove("hidden");
}

function closeModal() {
  document.getElementById("add-log-modal").classList.add("hidden");
  document.getElementById("add-log-form").reset();
}

// 1. SUBMIT LOG, FETCH UPDATED LOGS, AND DISPLAY AI RESULT
async function submitLog(event) {
  event.preventDefault();
  const btn = document.getElementById("btn-submit");
  btn.innerText = "Analyzing & Saving...";
  btn.disabled = true;

  const payload = {
    source: document.getElementById("log-source").value,
    severity: document.getElementById("log-severity").value,
    event: document.getElementById("log-event").value,
    score: parseFloat(document.getElementById("log-score").value),
    message: document.getElementById("log-message").value,
    reason: document.getElementById("log-reason").value
  };

  try {
    const res = await fetch("/api/logs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      const result = await res.json();
      closeModal();
      
      // Re-fetch database entries to sync the table view
      await fetchLogs();

      // Auto-select the newly added entry to present its AI analysis in the sidebar
      const createdLogId = result.log_id || (result.log && result.log.id);
      if (createdLogId) {
        const newlyCreatedLog = logsStore.find(l => l.id === createdLogId);
        if (newlyCreatedLog) selectLog(newlyCreatedLog);
      } else if (logsStore.length > 0) {
        selectLog(logsStore[0]);
      }
    } else {
      const errData = await res.json();
      alert("Ingestion Error: " + (errData.detail || "Failed to submit log"));
    }
  } catch (err) {
    console.error("Error submitting log:", err);
    alert("Network error submitting log.");
  } finally {
    btn.innerHTML = `<i data-lucide="sparkles" class="w-3.5 h-3.5"></i> Submit & Analyze`;
    btn.disabled = false;
    lucide.createIcons();
  }
}

// 2. FETCH LOGS FROM GET /api/logs API
async function fetchLogs() {
  try {
    const res = await fetch("/api/logs");
    const data = await res.json();
    logsStore = data.logs || data;
    renderTable(logsStore);
  } catch (err) {
    console.error("Error fetching logs:", err);
  }
}

// 3. RENDER LOG ENTRIES IN HTML TABLE
function renderTable(logs) {
  const tbody = document.getElementById("log-table-body");
  tbody.innerHTML = "";

  if (!logs || logs.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="p-8 text-center text-slate-500">No logs ingested yet.</td></tr>`;
    return;
  }

  logs.forEach((log) => {
    const isAnomaly = log.score >= 0.7;
    const row = document.createElement("tr");
    row.className = `cursor-pointer hover:bg-slate-800/80 transition ${isAnomaly ? 'bg-red-950/10' : ''}`;
    row.onclick = () => selectLog(log);

    const sevColors = {
      CRITICAL: "text-red-400 bg-red-400/10 border-red-500/20",
      ERROR: "text-orange-400 bg-orange-400/10 border-orange-500/20",
      WARN: "text-amber-400 bg-amber-400/10 border-amber-500/20",
      INFO: "text-blue-400 bg-blue-400/10 border-blue-500/20"
    };

    row.innerHTML = `
      <td class="p-4 font-mono text-slate-400">${log.timestamp || 'N/A'}</td>
      <td class="p-4"><span class="px-2 py-0.5 rounded text-[10px] font-semibold border ${sevColors[log.severity] || 'text-slate-400'}">${log.severity}</span></td>
      <td class="p-4 font-mono">${log.source}</td>
      <td class="p-4 font-medium">${log.event}</td>
      <td class="p-4 text-right font-bold font-mono ${isAnomaly ? 'text-red-400' : 'text-slate-400'}">${log.score}</td>
    `;
    tbody.appendChild(row);
  });
}

// 4. DISPLAY AI ANALYSIS AND LOG METADATA IN SIDEBAR
function selectLog(log) {
  const badge = document.getElementById("detail-score-badge");
  const content = document.getElementById("detail-content");
  const isAnomaly = log.score >= 0.7;

  badge.innerText = `Anomaly Score: ${log.score}`;
  badge.className = `px-2.5 py-1 text-xs font-bold rounded-full ${
    isAnomaly 
      ? 'bg-red-500/20 text-red-400 border border-red-500/30' 
      : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
  }`;

  content.innerHTML = `
    <div class="space-y-4">
      <div>
        <span class="text-[11px] font-semibold text-slate-400 block mb-1">Raw Log Message</span>
        <p class="font-mono text-xs bg-slate-950 p-3 rounded-lg border border-slate-800 text-slate-200">${log.message}</p>
      </div>
      <div>
        <span class="text-[11px] font-semibold text-slate-400 block mb-1">Detection Trigger</span>
        <p class="text-xs text-slate-300 bg-slate-900 p-2.5 rounded border border-slate-800">${log.reason}</p>
      </div>
      <div class="pt-2 border-t border-slate-800">
        <span class="text-xs font-semibold text-indigo-400 block mb-2 flex items-center gap-1.5">
          <i data-lucide="sparkles" class="w-3.5 h-3.5"></i> AI Root Cause & Recommendation
        </span>
        <div class="text-xs text-slate-200 bg-indigo-950/20 border border-indigo-900/40 p-3.5 rounded-lg leading-relaxed">
          ${log.ai_analysis || log.ai || "No AI explanation output returned."}
        </div>
      </div>
    </div>
  `;
  lucide.createIcons();
}

// INITIAL LOAD
document.addEventListener("DOMContentLoaded", () => {
  fetchLogs();
  lucide.createIcons();
});