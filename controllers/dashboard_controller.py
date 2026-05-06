from flask import render_template
from models.db import mysql

def dashboard():
    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM reos")
    total_reos = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cur.fetchone()[0]

    return render_template(
        "admin.html",
        total_reos=total_reos,
        total_usuarios=total_usuarios
    )