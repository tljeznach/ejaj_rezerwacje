from flask import Flask, render_template

app = Flask(__name__)

# Na początek przykładowe wydarzenia na sztywno
events = [
    {"id": 1, "title": "Improwizacja 3000", "date": "2025-06-15", "available": 12},
    {"id": 2, "title": "Wieczór z Poezją Absurdu", "date": "2025-06-18", "available": 8},
    {"id": 3, "title": "Teatr w Ciemnościach", "date": "2025-06-22", "available": 0},
]

@app.route("/")
def index():
    return render_template("index.html", events=events)


from flask import request, redirect, url_for

# Na razie przechowujmy rezerwacje w pamięci (tymczasowo)
reservations = []

@app.route("/reserve/<int:event_id>", methods=["GET", "POST"])
def reserve(event_id):
    event = next((e for e in events if e["id"] == event_id), None)
    if not event:
        return "Nie znaleziono wydarzenia", 404

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        if event["available"] > 0:
            event["available"] -= 1
            reservations.append({"event_id": event_id, "name": name, "email": email})
            return render_template("confirm.html", name=name, event=event)
        else:
            return "Brak miejsc!", 400

    return render_template("reserve.html", event=event)


if __name__ == "__main__":
    app.run(debug=True)