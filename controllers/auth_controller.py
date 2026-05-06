from flask import render_template, request, redirect, session
from models.db import mysql

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT * FROM usuarios WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['id'] = user[0]
            session['nombre'] = user[1]
            session['rol'] = user[4]

            return redirect('/admin')
        else:
            return "Usuario o contraseña incorrectos"

    return render_template('login.html')