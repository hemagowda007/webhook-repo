from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # For frontend JS

# Connect to MongoDB (local or Atlas)
#client = MongoClient("mongodb://localhost:27017/")  # Replace with Atlas URI if needed\
client = MongoClient("mongodb+srv://hemagowda210502:UrYMZ7EVJknVLuIj@cluster0.4eb7stx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["github_events"]
collection = db["events"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    event_type = request.headers.get("X-GitHub-Event")
    data = request.json
    doc = {}

    if event_type == "push":
        doc = {
            "author": data["pusher"]["name"],
            "action_type": "push",
            "to_branch": data["ref"].split("/")[-1],
            "timestamp": datetime.utcnow().isoformat()
        }

    elif event_type == "pull_request":
        pr = data["pull_request"]
        doc = {
            "author": pr["user"]["login"],
            "action_type": "merge" if pr["merged"] else "pull_request",
            "from_branch": pr["head"]["ref"],
            "to_branch": pr["base"]["ref"],
            "timestamp": pr["created_at"]
        }

    if doc:
        collection.insert_one(doc)

    return jsonify({"status": "received"}), 200

@app.route("/logs")
def logs():
    logs = collection.find().sort("timestamp", -1).limit(10)
    return jsonify([
        {
            "author": l.get("author"),
            "action_type": l.get("action_type"),
            "from_branch": l.get("from_branch", ""),
            "to_branch": l.get("to_branch", ""),
            "timestamp": l.get("timestamp")
        } for l in logs
    ])

if __name__ == "__main__":
    app.run(debug=True, port=5000)
