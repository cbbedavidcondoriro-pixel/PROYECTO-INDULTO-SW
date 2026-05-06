from flask import render_template, request, redirect
from models.db import mysql

def reos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM reos")
    data = cur.fetchall()
    cur.close()

    return render_template("reos.html", reos=data)

def agregar_reo():
    nombre = request.form['nombre']
    delito = request.form['delito']
    fecha = request.form['fecha']

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO reos(nombre, delito, fecha_ingreso) VALUES (%s,%s,%s)",
        (nombre, delito, fecha)
    )
    mysql.connection.commit()
    cur.close()

    return redirect("/reos")

def eliminar_reo(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM reos WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    return redirect("/reos")