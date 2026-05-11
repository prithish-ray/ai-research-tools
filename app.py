import os
import yaml
from flask import Flask, render_template, abort, url_for

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def load_tools():
    """Load tool metadata from YAML."""
    data_path = os.path.join(os.path.dirname(__file__), "data", "tools.yaml")
    with open(data_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def load_build_log():
    """Load build log entries from YAML, sorted by date descending."""
    data_path = os.path.join(os.path.dirname(__file__), "data", "build_log.yaml")
    with open(data_path, "r", encoding="utf-8") as f:
        entries = yaml.safe_load(f) or []
    return sorted(entries, key=lambda x: x.get("date", ""), reverse=True)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    tools = load_tools()
    featured = [t for t in tools if t.get("featured")]
    workflow_stages = [
        "Idea Intake",
        "Thesis Extraction",
        "Variant Perception",
        "Red-Team Challenge",
        "News / Document Monitoring",
        "Kill-Switch Tracking",
        "Behavioural Guardrails",
        "Portfolio Review",
    ]
    # Map tools to their workflow stage for the workflow section
    stage_map = {}
    for stage in workflow_stages:
        stage_map[stage] = [t for t in tools if t.get("workflow_stage") == stage]
    return render_template(
        "index.html",
        tools=tools,
        featured=featured,
        workflow_stages=workflow_stages,
        stage_map=stage_map,
    )


@app.route("/tools")
def tools():
    all_tools = load_tools()
    categories = sorted({t.get("category", "") for t in all_tools if t.get("category")})
    stages = sorted({t.get("workflow_stage", "") for t in all_tools if t.get("workflow_stage")})
    statuses = sorted({t.get("status", "") for t in all_tools if t.get("status")})
    return render_template(
        "tools.html",
        tools=all_tools,
        categories=categories,
        stages=stages,
        statuses=statuses,
    )


@app.route("/tools/<slug>")
def tool_detail(slug):
    all_tools = load_tools()
    tool = next((t for t in all_tools if t.get("slug") == slug), None)
    if tool is None:
        abort(404)
    return render_template("tool_detail.html", tool=tool)


@app.route("/build-log")
def build_log():
    builds = load_build_log()
    return render_template("build_log.html", builds=builds)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/health")
def health():
    return "OK", 200


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template("500.html"), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
