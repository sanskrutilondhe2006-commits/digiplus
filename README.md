# digiplus
FastAPI log monitoring &amp; threat detection pipeline featuring custom rule-based anomaly scoring, SQLite/PostgreSQL persistence, and live LLM root-cause diagnostics.
Technology Stack Overview

🛠️Frontend (User Interface & Interactivity)
HTML5: Semantic markup structure for the threat intelligence dashboard and ingestion modals.
Vanilla JavaScript (ES6+): Client-side scripting for asynchronous API communications (fetch), dynamic DOM manipulation, modal handling, and automatic log selection.
Tailwind CSS (v3 via CDN): Utility-first CSS framework for dark-mode UI styling, responsive layouts, badge highlights, and animations.

Backend (REST API & Business Logic)
Python 3.9+: Core programming language powering the backend services.
FastAPI: Modern, high-performance web framework for constructing the REST API endpoints (/api/logs).
Uvicorn: Lightning-fast ASGI web server implementation used to run the FastAPI application.
Pydantic: Data validation and settings management library used to enforce strict schema validation for incoming log payloads.

 Install Dependencies
Install the required Python packages:

pip install fastapi uvicorn sqlalchemy openai pydantic
pip install -r requirements.txt

# Clone the repository
git clone https://github.com/YOUR_USERNAME/sentinel-log-ai.git
cd sentinel-log-ai

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate
