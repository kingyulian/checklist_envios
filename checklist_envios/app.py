from flask import Flask, render_template, redirect, request, send_file
from flask_sqlalchemy import SQLAlchemy
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)   # 👈 este nombre es obligatorio para Render

@app.route("/")
def home():
    return "Checklist funcionando 🚀"


# Configuración de SQLite
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "database.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Modelo de datos
class Pieza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    estado = db.Column(db.String(20), default="Pendiente")
    observaciones = db.Column(db.String(300), default="")

# Crear la BD si no existe
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    piezas = Pieza.query.all()
    return render_template("index.html", piezas=piezas)

@app.route("/agregar", methods=["POST"])
def agregar():
    nombre = request.form["nombre"]
    cantidad = request.form["cantidad"]
    observaciones = request.form.get("observaciones", "")
    nueva = Pieza(nombre=nombre, cantidad=cantidad, observaciones=observaciones)
    db.session.add(nueva)
    db.session.commit()
    return redirect("/")

@app.route("/marcar/<int:pieza_id>")
def marcar(pieza_id):
    pieza = Pieza.query.get(pieza_id)
    if pieza:
        pieza.estado = "Enviado" if pieza.estado == "Pendiente" else "Pendiente"
        db.session.commit()
    return redirect("/")

@app.route("/eliminar/<int:pieza_id>")
def eliminar(pieza_id):
    pieza = Pieza.query.get(pieza_id)
    if pieza:
        db.session.delete(pieza)
        db.session.commit()
    return redirect("/")

@app.route("/exportar_pdf")
def exportar_pdf():
    archivo = "checklist_envios.pdf"
    piezas = Pieza.query.all()

    c = canvas.Canvas(archivo, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(50, 750, "Checklist de Envíos")
    c.drawString(50, 735, "---------------------------------------------")

    y = 710
    for pieza in piezas:
        linea = f"{pieza.nombre} | Cantidad: {pieza.cantidad} | Estado: {pieza.estado} | Obs: {pieza.observaciones}"
        c.drawString(50, y, linea)
        y -= 20
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 750

    c.save()
    return send_file(archivo, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


