from flask import Flask, render_template, request, redirect, url_for, session, jsonify 
import os
from werkzeug.utils import secure_filename
from PIL import Image
from flask import send_from_directory 

app = Flask(__name__)
app.secret_key = "actor_scanner_secret"
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "bmp"}

MINIMUM_WIDTH = 100
MINIMUM_HEIGHT = 100

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def allowed_file(filename):
    """Check the file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

def validate_image_resolution(filepath):
    """Check the image meets minimum resolution requirements."""
    try:
        img = Image.open(filepath)
        width, height = img.size
        return width >= MINIMUM_WIDTH and height >= MINIMUM_HEIGHT
    except Exception:
        return False

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scanner")
def scanner():
    return render_template("scanner.html")

@app.route("/loading")
def loading():
    return render_template("loading.html")

@app.route("/result")
def result():
    actor_name = session.get("actor_name", None)
    confidence = session.get("confidence", None)
    films = session.get("films", [])
    actor_dob = session.get("actor_dob", "Unknown")
    actor_nationality = session.get("actor_nationality", "Unknown")
    actor_image = session.get("actor_image", "")
    return render_template("result.html",
                           actor_name=actor_name,
                           confidence=confidence,
                           films=films,
                           actor_dob=actor_dob,
                           actor_nationality=actor_nationality,
                           actor_image=actor_image)

@app.route("/no_match")
def no_match():
    return render_template("no_match.html")

@app.route("/upload", methods=["POST"])
def upload():
    image = request.files.get("image")

    # Validation check 1 — no file submitted
    if not image or image.filename == "":
        return redirect(url_for("scanner"))

    # Validation check 2 — wrong file type
    if not allowed_file(image.filename):
        return redirect(url_for("scanner"))

    filename = secure_filename(image.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image.save(save_path)

    # Validation check 3 — image resolution too low
    if not validate_image_resolution(save_path):
        os.remove(save_path)    
        return redirect(url_for("scanner"))

    # Store the path in session for the recognition step
    session["uploaded_image"] = save_path
    return redirect(url_for("loading"))

from recognition import preprocess_image, detect_face_locations, extract_face_encoding, find_best_match
from database import setup_database, load_all_actor_encodings, get_actor_details, get_filmography

setup_database()  # called once on startup

@app.route("/process")
def process():
    image_path = session.get("uploaded_image")
    if not image_path or not os.path.exists(image_path):
        return redirect(url_for("scanner"))

    # Stage 1 — Preprocess
    rgb_image, err = preprocess_image(image_path)
    if err:
        return redirect(url_for("no_match"))

    # Stage 2 — Detect
    face_locations, err = detect_face_locations(rgb_image)
    if err:
        return redirect(url_for("no_match"))

    # Stage 3 — Encode
    encoding, err = extract_face_encoding(rgb_image, face_locations)
    if err:
        return redirect(url_for("no_match"))

    # Stage 4 — Match against database
    actors = load_all_actor_encodings()
    matched_actor, confidence = find_best_match(encoding, actors)

    if matched_actor is None:
        return redirect(url_for("no_match"))

    # Stage 5 — Retrieve details
    details = get_actor_details(matched_actor["id"])
    films = get_filmography(matched_actor["id"])

    session["actor_name"] = matched_actor["name"]
    session["confidence"] = confidence
    session["actor_dob"] = details[1] if details else "Unknown"
    session["actor_nationality"] = details[2] if details else "Unknown"
    session["actor_image"] = matched_actor["name"].replace(" ", "_") + ".jpg"
    session["films"] = [{"title": f["title"], "year": f["year"], "genre": f["genre"], "role": f["role"]} for f in films] 

    return redirect(url_for("result")) 

@app.route("/film/<int:index>")
def film_detail(index):
    films = session.get("films", [])
    if index >= len(films) or index < 0:
        return redirect(url_for("result"))
    film = films[index]
    actor_name = session.get("actor_name", "")
    actor_image = session.get("actor_image", "")
    return render_template("film_detail.html", film=film, actor_name=actor_name, actor_image=actor_image)

@app.route("/actor_images/<filename>")
def actor_image(filename):
    return send_from_directory("actor_images", filename)

from flask import jsonify

@app.route("/search")
def search():
    from database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM actors")
    count = cursor.fetchone()[0]
    conn.close()
    return render_template("search.html", actor_count=count)

@app.route("/api/search")
def api_search():
    """Returns JSON list of matching actors for autocomplete."""
    print("API SEARCH HIT")
    query = request.args.get("q", "").strip()
    if len(query) < 2:
        return jsonify([])
    from database import search_actors_by_name
    results = search_actors_by_name(query)
    return jsonify(results)

@app.route("/actor/<int:actor_id>")
def actor_profile(actor_id):
    from database import get_actor_details, get_filmography
    details = get_actor_details(actor_id)
    if not details:
        return redirect(url_for("no_match"))
    films = get_filmography(actor_id)
    session["actor_name"] = details[0]
    session["actor_dob"] = details[1]
    session["actor_nationality"] = details[2]
    session["confidence"] = "N/A"
    session["actor_image"] = details[0].replace(" ", "_") + ".jpg"
    session["films"] = [{"title": f["title"], "year": f["year"], "genre": f["genre"], "role": f["role"]} for f in films]
    return redirect(url_for("result"))

@app.route("/service_worker.js")
def service_worker():
    return app.send_static_file("service_worker.js"), 200, {
        "Content-Type": "application/javascript"
    }

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)