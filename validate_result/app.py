from flask import Flask, render_template, request, redirect, url_for
from config import Config
from services import DataService
from models import Annotation
from datetime import datetime

app = Flask(__name__)
data_service = DataService(Config.SYSTEM_OUTPUT_PATH, Config.ANNOTATED_PATH)

@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("pending_annotations"))

@app.route("/pending", methods=["GET"])
def pending_annotations():
    annotated, pending = data_service.get_split_data()
    return render_template(
        "index.html",
        pending_data=pending,
        annotated_data=[],
        active_tab="pending",
        classifications=Config.CLASSIFICATION_CHOICES,
        categories=Config.CATEGORY_CHOICES
    )

@app.route("/annotated", methods=["GET"])
def completed_annotations():
    annotated, pending = data_service.get_split_data()
    return render_template(
        "index.html",
        pending_data=[],
        annotated_data=annotated,
        active_tab="annotated",
        classifications=Config.CLASSIFICATION_CHOICES,
        categories=Config.CATEGORY_CHOICES
    )

@app.route("/annotate", methods=["POST"])
def handle_annotation():
    annotations = data_service.read_annotations()
    
    file_id = request.form["file_id"]
    annotations[file_id] = Annotation(
        file_id=file_id,
        final_classification=request.form.get("final_classification"),
        final_category=request.form.get("final_category"),
        excluded=request.form.get("excluded") == "on",
        exclusion_note=request.form.get("exclusion_note", ""),
        annotation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    data_service.write_annotations(annotations)
    return redirect(url_for("pending_annotations"))

if __name__ == "__main__":
    app.run(debug=True)