from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)  # Allows frontend to interact with the backend

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///messages.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)

# Define Message model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Initialize the database
with app.app_context():
    db.create_all()

# Route to create a user
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if not data or "username" not in data:
        return jsonify({"error": "Username is required"}), 400

    user = User(username=data["username"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully", "id": user.id}), 201

# Route to send a message
@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.json
    sender_id = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    content = data.get("content")

    if not sender_id or not receiver_id or not content:
        return jsonify({"error": "Missing fields"}), 400

    message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.session.add(message)
    db.session.commit()
    return jsonify({"message": "Message sent"}), 201

# Route to get messages between two users
@app.route("/get_messages", methods=["GET"])
def get_messages():
    sender_id = request.args.get("sender_id")
    receiver_id = request.args.get("receiver_id")

    if not sender_id or not receiver_id:
        return jsonify({"error": "Sender and receiver IDs required"}), 400

    messages = Message.query.filter(
        ((Message.sender_id == sender_id) & (Message.receiver_id == receiver_id)) |
        ((Message.sender_id == receiver_id) & (Message.receiver_id == sender_id))
    ).order_by(Message.timestamp).all()

    return jsonify([{"sender_id": msg.sender_id, "receiver_id": msg.receiver_id, "content": msg.content, "timestamp": msg.timestamp} for msg in messages])

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
