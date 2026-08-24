import random
from datetime import datetime, timedelta


def generate_synthetic_logs():
  sources = ["192.168.1.10", "10.0.0.45", "db-cluster-01", "api-gateway", "203.0.113.42"]
  base_time = datetime.now() - timedelta(hours=1)

  raw_dataset = [
      {
          "timestamp": (base_time + timedelta(minutes=1)).strftime(
              "%Y-%m-%d %H:%M:%S"
          ),
          "source": "10.0.0.45",
          "severity": "CRITICAL",
          "event": "AUTH_FAILURE",
          "score": 0.94,
          "message": "Repeated 401 Unauthorized access on admin route",
          "reason": "High score: Brute force request pattern detected.",
          "ai": (
              "<strong>Root Cause:</strong> Malicious IP attempting credential"
              " stuffing against <code>/api/v1/login</code>.<br><br><strong>Remediation:</strong>"
              " Ban IP 10.0.0.45 and trigger automated password reset for"
              " affected user."
          ),
      },
      {
          "timestamp": (base_time + timedelta(minutes=2)).strftime(
              "%Y-%m-%d %H:%M:%S"
          ),
          "source": "192.168.1.10",
          "severity": "INFO",
          "event": "HTTP_GET",
          "score": 0.12,
          "message": "GET /api/v1/health status 200",
          "reason": "Standard metric payload.",
          "ai": (
              "No anomalous behavior detected. System operating well within"
              " expected baseline parameters."
          ),
      },
      {
          "timestamp": (base_time + timedelta(minutes=3)).strftime(
              "%Y-%m-%d %H:%M:%S"
          ),
          "source": "db-cluster-01",
          "severity": "ERROR",
          "event": "DB_TIMEOUT",
          "score": 0.88,
          "message": "Connection pool exhausted (max_connections=100)",
          "reason": (
              "Sudden spike in connection duration compared to baseline."
          ),
          "ai": (
              "<strong>Root Cause:</strong> Long-running unindexed SQL query"
              " blocking worker threads.<br><br><strong>Remediation:</strong>"
              " Terminate stagnant DB process #4481 and scale pool size"
              " temporarily."
          ),
      },
      {
          "timestamp": (base_time + timedelta(minutes=4)).strftime(
              "%Y-%m-%d %H:%M:%S"
          ),
          "source": "api-gateway",
          "severity": "WARN",
          "event": "RATE_LIMIT",
          "score": 0.45,
          "message": "Rate limit threshold reached for client app-99",
          "reason": "Normal spike during peak schedule hours.",
          "ai": (
              "Expected system load behavior. Client app-99 has auto-scaling"
              " triggers pending."
          ),
      },
      {
          "timestamp": "",  # Validation test: Missing timestamp
          "source": "unknown-source",
          "severity": "ERROR",
          "event": "MALFORMED_ENTRY",
          "score": 0.99,
          "message": "Log packet structure validation failed: Missing timestamp",
          "reason": "Schema validation error during ingestion pipeline.",
          "ai": (
              "<strong>Root Cause:</strong> Malformed payload sent by legacy"
              " shipper agent.<br><br><strong>Remediation:</strong> Update"
              " syslog forwarding daemon configuration."
          ),
      },
  ]
  return raw_dataset