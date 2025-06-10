from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv



app = Flask(__name__)
load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    available = db.Column(db.Integer, nullable=False)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event', backref=db.backref('reservations', lazy=True))


# Na początek przykładowe wydarzenia na sztywno
events = [
    {"id": 1, "title": "Improwizacja 3000", "date": "2025-06-15", "available": 12},
    {"id": 2, "title": "Wieczór z Poezją Absurdu", "date": "2025-06-18", "available": 8},
    {"id": 3, "title": "Teatr w Ciemnościach", "date": "2025-06-22", "available": 0},
]

@app.route("/")
def index():
    events = Event.query.all()
    return render_template("index.html", events=events)


from flask import request, redirect, url_for

# Na razie przechowujmy rezerwacje w pamięci (tymczasowo)
reservations = []

@app.route("/reserve/<int:event_id>", methods=["GET", "POST"])
def reserve(event_id):
    event = Event.query.get_or_404(event_id)
    if not event:
        return "Nie znaleziono wydarzenia", 404


# TODO: dodać liczbę biletów dla osoby, domyślnie 1
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        if event.available > 0:
            if event.available > 0:
                event.available -= 1
                db.session.add(event)
            reservation = Reservation(name=name, email=email, event=event)
            db.session.add(reservation)
            db.session.commit()

            return render_template("confirm.html", name=name, event=event)
        else:
            return "Brak miejsc!", 400

    return render_template("reserve.html", event=event)


if __name__ == "__main__":
    app.run(debug=True)



