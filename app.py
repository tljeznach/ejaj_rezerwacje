from flask import Flask, request, redirect, url_for, session, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from models import db, Event, Reservation  # <-- import modeli
from flask_mail import Mail, Message

load_dotenv()


app = Flask(__name__)
app.secret_key = os.urandom(24)
load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

def is_logged_in():
    return session.get("logged_in")

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

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")

        if event.available > 0:
            event.available -= 1
            db.session.add(event)

            reservation = Reservation(name=name, email=email, event=event)
            db.session.add(reservation)
            db.session.commit()

            # Wysyłanie maila z potwierdzeniem
            try:
                msg = Message(
                    subject="Potwierdzenie rejestracji na spektakl",
                    recipients=[reservation.email],
                    body=f"Cześć {reservation.name}!\n\nZarejestrowano Cię na spektakl „{event.title}” w dniu {event.date}.\n\nDo zobaczenia!",
                )
                mail.send(msg)
            except Exception as e:
                print("Błąd przy wysyłce maila:", e)

            return render_template("confirm.html", name=name, event=event)

        else:
            return "Brak miejsc!", 400

    return render_template("reserve.html", event=event)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == os.getenv("ADMIN_PASSWORD"):
            session["logged_in"] = True
            return redirect(url_for("admin_panel"))
        else:
            flash("Niepoprawne hasło", "error")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("logged_in", None)
    return redirect(url_for("admin_login"))

@app.route("/admin/delete/<int:reservation_id>", methods=["POST"])
def delete_reservation(reservation_id):
    if not is_logged_in():
        return redirect(url_for("admin_login"))

    reservation = Reservation.query.get_or_404(reservation_id)
    event = reservation.event
    db.session.delete(reservation)
    event.available += 1  # odzyskujemy jedno miejsce
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route("/admin/delete_event/<int:event_id>", methods=["POST"])
def delete_event(event_id):
    if not is_logged_in():
        return redirect(url_for("admin_login"))

    event = Event.query.get_or_404(event_id)

    # usuwamy powiązane rezerwacje
    Reservation.query.filter_by(event_id=event.id).delete()

    db.session.delete(event)
    db.session.commit()
    return redirect(url_for("admin_panel"))


@app.route("/admin")
def admin_panel():
    if not is_logged_in():
        return redirect(url_for("admin_login"))

    reservations = Reservation.query.all()
    events = Event.query.all()  # ← dodaj to
    return render_template("admin_panel.html", reservations=reservations, events=events)


@app.route("/admin/add_event", methods=["POST"])
def add_event():
    if not is_logged_in():
        return redirect(url_for("admin_login"))

    title = request.form.get("title")
    date = request.form.get("date")
    available = request.form.get("available")

    new_event = Event(title=title, date=date, available=int(available))
    db.session.add(new_event)
    db.session.commit()
    return redirect(url_for("admin_panel"))


if __name__ == "__main__":
    app.run(debug=True)



