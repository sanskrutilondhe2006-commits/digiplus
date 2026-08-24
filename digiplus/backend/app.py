import random
from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# --- DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./logs.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class LogEntry(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String, index=True)
    severity = Column(String, index=True)
    source = Column(String, index=True)
    event = Column(String, index=True)
    score = Column(Float, default=0.0)
    message = Column(String)
    reason = Column(String)
    ai_analysis = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)

# --- SYNTHETIC LOG GENERATOR ---
def generate_synthetic_logs():
    base_time = datetime.now() - timedelta(hours=1)
    return [
        {
            "timestamp": (base_time + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "source": "10.0.0.45",
            "severity": "CRITICAL",
            "event": "AUTH_FAILURE",
            "score": 0.94,
            "message": "Repeated 401 Unauthorized access on admin route",
            "reason": "High score: Brute force request pattern detected.",
            "ai_analysis": "<strong>Root Cause:</strong> Malicious IP attempting credential stuffing against <code>/api/v1/login</code>.<br><br><strong>Remediation:</strong> Ban IP 10.0.0.45 and trigger automated password reset for affected user."
        },
        {
            "timestamp": (base_time + timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "source": "192.168.1.10",
            "severity": "INFO",
            "event": "HTTP_GET",
            "score": 0.12,
            "message": "GET /api/v1/health status 200",
            "reason": "Standard metric payload.",
            "ai_analysis": "No anomalous behavior detected. System operating well within expected baseline parameters."
        },
        {
            "timestamp": (base_time + timedelta(minutes=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "source": "db-cluster-01",
            "severity": "ERROR",
            "event": "DB_TIMEOUT",
            "score": 0.88,
            "message": "Connection pool exhausted (max_connections=100)",
            "reason": "Sudden spike in connection duration compared to baseline.",
            "ai_analysis": "<strong>Root Cause:</strong> Long-running unindexed SQL query blocking worker threads.<br><br><strong>Remediation:</strong> Terminate stagnant DB process #4481 and scale pool size temporarily."
        },
        {
            "timestamp": (base_time + timedelta(minutes=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "source": "api-gateway",
            "severity": "WARN",
            "event": "RATE_LIMIT",
            "score": 0.45,
            "message": "Rate limit threshold reached for client app-99",
            "reason": "Normal spike during peak schedule hours.",
            "ai_analysis": "Expected system load behavior. Client app-99 has auto-scaling triggers pending."
        },
        {
            "timestamp": "",  # Validation test: Missing timestamp
            "source": "unknown-source",
            "severity": "ERROR",
            "event": "MALFORMED_ENTRY",
            "score": 0.99,
            "message": "Log packet structure validation failed: Missing timestamp",
            "reason": "Schema validation error during ingestion pipeline.",
            "ai_analysis": "<strong>Root Cause:</strong> Malformed payload sent by legacy shipper agent.<br><br><strong>Remediation:</strong> Update syslog forwarding daemon configuration."
        }
    ]

# --- FASTAPI APP ---
app = FastAPI(title="SentinelLog AI API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    init_db()
    db = SessionLocal()
    if db.query(LogEntry).count() == 0:
        for log_data in generate_synthetic_logs():
            db.add(LogEntry(**log_data))
        db.commit()
    db.close()

@app.get("/api/logs")
def get_logs(search: str = None, flagged_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(LogEntry)
    if flagged_only:
        query = query.filter(LogEntry.score >= 0.7)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (LogEntry.source.ilike(search_term)) |
            (LogEntry.event.ilike(search_term)) |
            (LogEntry.severity.ilike(search_term)) |
            (LogEntry.message.ilike(search_term))
        )
    logs = query.all()
    total_count = db.query(LogEntry).count()
    anomaly_count = db.query(LogEntry).filter(LogEntry.score >= 0.7).count()
    
    return {
        "total_ingested": total_count,
        "flagged_anomalies": anomaly_count,
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp if log.timestamp else "N/A (Malformed)",
                "severity": log.severity,
                "source": log.source,
                "event": log.event,
                "score": log.score,
                "message": log.message,
                "reason": log.reason,
                "ai": log.ai_analysis
            } for log in logs
        ]
    }

# Serve the complete frontend dashboard directly from FastAPI
@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    return """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Log Anomaly Dashboard | SentinelLog AI</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen font-sans flex flex-col selection:bg-indigo-500 selection:text-white">

  <header class="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4 flex justify-between items-center">
    <div class="flex items-center gap-3">
      <div class="p-2 bg-indigo-500/10 border border-indigo-500/20 rounded-lg">
        <i data-lucide="shield-alert" class="w-6 h-6 text-indigo-400"></i>
      </div>
      <div>
        <h1 class="text-lg font-bold tracking-wide text-white">SentinelLog AI</h1>
        <p class="text-xs text-slate-400">Autonomous Threat Intelligence</p>
      </div>
    </div>
    <span class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-sm">
      <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Pipeline Active
    </span>
  </header>

  <main class="flex-1 p-6 max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-3 gap-6">
    <div class="lg:col-span-2 flex flex-col gap-6">
      <div class="grid grid-cols-3 gap-4">
        <div class="bg-slate-800/40 border border-slate-800 p-4 rounded-xl backdrop-blur-sm">
          <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Ingested</p>
          <p class="text-2xl font-extrabold text-slate-100 mt-1" id="metric-total">0</p>
        </div>
        <div class="bg-slate-800/40 border border-red-500/20 p-4 rounded-xl backdrop-blur-sm bg-gradient-to-br from-slate-800/40 to-red-950/10">
          <p class="text-xs font-medium text-red-400 uppercase tracking-wider">Flagged Anomalies</p>
          <p class="text-2xl font-extrabold text-red-400 mt-1" id="metric-anomalies">0</p>
        </div>
        <div class="bg-slate-800/40 border border-slate-800 p-4 rounded-xl backdrop-blur-sm">
          <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">System Health</p>
          <p class="text-2xl font-extrabold text-emerald-400 mt-1">98.4%</p>
        </div>
      </div>

      <div class="bg-slate-800/40 border border-slate-800 p-4 rounded-xl flex flex-wrap gap-4 items-center justify-between">
        <div class="relative flex-1 min-w-[240px]">
          <i data-lucide="search" class="w-4 h-4 absolute left-3.5 top-3 text-slate-500"></i>
          <input type="text" id="search-input" oninput="handleSearch()" placeholder="Search logs by IP, event, or severity..." class="w-full bg-slate-900 border border-slate-700/80 rounded-lg pl-10 pr-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 transition">
        </div>
        <button onclick="toggleAnomalyFilter()" id="btn-filter" class="px-4 py-2 text-sm font-medium bg-red-500/10 text-red-400 border border-red-500/20 rounded-lg hover:bg-red-500/20 transition flex items-center gap-2">
          <i data-lucide="filter" class="w-4 h-4"></i> Show Flagged Only
        </button>
      </div>

      <div class="bg-slate-800/40 border border-slate-800 rounded-xl overflow-hidden flex-1 shadow-lg">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead class="bg-slate-950/60 text-slate-400 uppercase text-[11px] tracking-wider border-b border-slate-800">
              <tr>
                <th class="p-4">Timestamp</th>
                <th class="p-4">Severity</th>
                <th class="p-4">Source</th>
                <th class="p-4">Event</th>
                <th class="p-4 text-right">Anomaly Score</th>
              </tr>
            </thead>
            <tbody id="log-table-body" class="divide-y divide-slate-800/60 text-slate-300"></tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="bg-slate-800/40 border border-slate-800 rounded-xl p-6 flex flex-col justify-between shadow-lg">
      <div id="detail-container">
        <div class="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
          <h2 class="text-base font-bold text-white flex items-center gap-2">
            <i data-lucide="cpu" class="w-5 h-5 text-indigo-400"></i> AI Diagnostics Panel
          </h2>
          <span id="detail-score-badge" class="px-2.5 py-1 text-xs font-bold rounded-full bg-slate-800 text-slate-400 border border-slate-700">Select Log</span>
        </div>
        <div id="detail-content" class="space-y-4">
          <div class="flex flex-col items-center justify-center py-12 text-center">
            <div class="p-3 bg-slate-800/50 rounded-full border border-slate-700/50 mb-3 text-slate-400">
              <i data-lucide="mouse-pointer-click" class="w-6 h-6"></i>
            </div>
            <p class="text-slate-400 text-sm">Click on any log entry row to inspect details and view AI root-cause analysis.</p>
          </div>
        </div>
      </div>
      <div class="border-t border-slate-800/80 pt-4 mt-6 text-xs text-slate-500 flex justify-between items-center">
        <span>Model: SentinelLLM-v3</span>
        <span class="text-emerald-400 flex items-center gap-1"><i data-lucide="check-circle-2" class="w-3.5 h-3.5"></i> Fully Optimized</span>
      </div>
    </div>
  </main>

  <script>
    let logs = [];
    let filterAnomalyOnly = false;
    let searchQuery = "";

    async function fetchLogs() {
      try {
        const flagParam = filterAnomalyOnly ? "?flagged_only=true" : "";
        const searchParam = searchQuery ? `${flagParam ? '&' : '?'}search=${encodeURIComponent(searchQuery)}` : "";
        const response = await fetch(`/api/logs${flagParam}${searchParam}`);
        const data = await response.json();
        
        logs = data.logs;
        document.getElementById("metric-total").innerText = data.total_ingested;
        document.getElementById("metric-anomalies").innerText = data.flagged_anomalies;
        renderTable();
      } catch (error) {
        console.error("Error fetching logs:", error);
      }
    }

    function renderTable() {
      const tbody = document.getElementById("log-table-body");
      tbody.innerHTML = "";
      if (logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="p-8 text-center text-slate-500 italic">No matching log entries found.</td></tr>`;
        return;
      }

      logs.forEach(log => {
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
          <td class="p-4 font-mono text-xs text-slate-400">${log.timestamp}</td>
          <td class="p-4"><span class="px-2.5 py-0.5 rounded text-[11px] font-semibold border ${sevColors[log.severity] || 'text-slate-400'}">${log.severity}</span></td>
          <td class="p-4 font-mono text-xs">${log.source}</td>
          <td class="p-4 font-medium">${log.event}</td>
          <td class="p-4 text-right font-bold font-mono ${isAnomaly ? 'text-red-400' : 'text-slate-400'}">${log.score}</td>
        `;
        tbody.appendChild(row);
      });
    }

    function selectLog(log) {
      const badge = document.getElementById("detail-score-badge");
      const content = document.getElementById("detail-content");
      const isAnomaly = log.score >= 0.7;

      badge.innerText = `Score: ${log.score}`;
      badge.className = `px-2.5 py-1 text-xs font-bold rounded-full ${isAnomaly ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'}`;

      content.innerHTML = `
        <div class="space-y-4">
          <div>
            <span class="text-xs text-slate-400 block mb-1">Raw Event Message</span>
            <p class="font-mono text-xs bg-slate-950 p-3 rounded-lg border border-slate-800 text-slate-200">${log.message}</p>
          </div>
          <div>
            <span class="text-xs text-slate-400 block mb-1">Detection Trigger</span>
            <p class="text-sm text-slate-300">${log.reason}</p>
          </div>
          <div class="pt-2 border-t border-slate-800">
            <span class="text-xs font-semibold text-indigo-400 block mb-2 flex items-center gap-1.5">
              <i data-lucide="sparkles" class="w-3.5 h-3.5"></i> AI Root Cause & Next Steps
            </span>
            <div class="text-sm text-slate-300 bg-indigo-950/20 border border-indigo-900/40 p-3.5 rounded-lg leading-relaxed">
              ${log.ai}
            </div>
          </div>
        </div>
      `;
      lucide.createIcons();
    }

    function toggleAnomalyFilter() {
      filterAnomalyOnly = !filterAnomalyOnly;
      const btn = document.getElementById("btn-filter");
      btn.classList.toggle("bg-red-500/30", filterAnomalyOnly);
      fetchLogs();
    }

    function handleSearch() {
      searchQuery = document.getElementById("search-input").value;
      fetchLogs();
    }

    document.addEventListener("DOMContentLoaded", () => {
      fetchLogs();
      lucide.createIcons();
    });
  </script>
</body>
</html>
    """