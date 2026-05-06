from flask import Flask, render_template, request, redirect, session
from models.db import mysql

app = Flask(__name__, template_folder='views')

# ======================
# MYSQL CONFIG
# ======================
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'david0309'
app.config['MYSQL_DB'] = 'indulto_proyecto'

app.secret_key = "indulto_secret"

mysql.init_app(app)

@app.route('/')
def bienvenida():
    return render_template('bienvenida.html')

# ======================
# LOGIN
# ======================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE username=%s AND password=%s", (user, password))
        data = cur.fetchone()
        cur.close()

        if data:
            session['user'] = user
            return redirect('/admin')
        else:
            return "Usuario o contraseña incorrectos"

    return render_template('login.html')


# ======================
# LOGOUT
# ======================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ======================
# DASHBOARD ADMIN
# ======================
@app.route('/admin')
def admin():

    if 'user' not in session:
        return redirect('/')

    cur = mysql.connection.cursor()

    # CONTADORES
    cur.execute("SELECT COUNT(*) FROM reos")
    total_reos = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cur.fetchone()[0]

    # LISTA REOS
    cur.execute("SELECT * FROM reos")
    reos = cur.fetchall()

    # ✅ VISITAS (100% acorde a tu BD)
    cur.execute("""
        SELECT v.id, v.nombre_visitante, v.ci,
               r.nombre, v.fecha, v.parentesco
        FROM visitas v
        JOIN reos r ON v.id_reo = r.id
    """)
    visitas = cur.fetchall()

    cur.close()

    return render_template(
        "admin_dashboard.html",
        total_reos=total_reos,
        total_usuarios=total_usuarios,
        reos=reos,
        visitas=visitas
    )

# ======================
# REOS (LISTAR)
# ======================
@app.route('/reos')
def reos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM reos")
    data = cur.fetchall()
    cur.close()

    return render_template("reos.html", reos=data)


# ======================
# AGREGAR REO
# ======================
@app.route('/reos/agregar', methods=['POST'])
def agregar_reo():

    nombre = request.form['nombre']
    apellido = request.form['apellido']
    ci = request.form['ci']
    delito = request.form['delito']
    fecha = request.form['fecha']
    tiempo = request.form['tiempo']
    estado = request.form['estado']

    cur = mysql.connection.cursor()

    cur.execute("""
        INSERT INTO reos(nombre, apellido, ci, delito, fecha_ingreso, tiempo_condena, estado)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (nombre, apellido, ci, delito, fecha, tiempo, estado))

    mysql.connection.commit()
    cur.close()

    return redirect('/reos')

# ======================
# ELIMINAR REO
# ======================
@app.route('/reos/eliminar/<int:id>')
def eliminar_reo(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM reos WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    return redirect('/admin')


# ======================
# VISITAS (LISTAR)
# ======================
@app.route('/visitas')
def visitas():
    cur = mysql.connection.cursor()

    # 🔥 CORREGIDO
    cur.execute("""
        SELECT v.id_visita, v.nombre_visitante, v.ci_visitante,
               r.nombre, v.fecha_visita, v.parentesco
        FROM visitas v
        JOIN reos r ON v.id_interno = r.id
    """)
    data = cur.fetchall()

    cur.execute("SELECT * FROM reos")
    reos = cur.fetchall()

    cur.close()

    return render_template("visitas.html", visitas=data, reos=reos)


# ======================
# AGREGAR VISITA
# ======================

@app.route('/visitas/agregar', methods=['POST'])
def agregar_visita():
    nombre = request.form['nombre']
    ci = request.form['ci']
    id_reo = request.form['id_reo']
    fecha = request.form['fecha']
    parentesco = request.form['parentesco']

    cur = mysql.connection.cursor()

    cur.execute("""
        INSERT INTO visitas(nombre_visitante, ci, id_reo, fecha, parentesco)
        VALUES (%s,%s,%s,%s,%s)
    """, (nombre, ci, id_reo, fecha, parentesco))

    mysql.connection.commit()
    cur.close()

    return redirect('/admin')

@app.route('/indultos', methods=['GET', 'POST'])
def indultos():

    cur = mysql.connection.cursor()

    # =====================
    # CREAR INDULTO
    # =====================
    if request.method == 'POST':
        id_interno = request.form['id_interno']
        motivo = request.form['motivo']

        cur.execute("""
            INSERT INTO indultos (id_interno, motivo)
            VALUES (%s, %s)
        """, (id_interno, motivo))

        mysql.connection.commit()

    # =====================
    # INTERNOS (SELECT PRO)
    # =====================
    cur.execute("""
        SELECT id_interno, nombre, apellido, ci, delito
        FROM internos
    """)
    internos = cur.fetchall()

    # =====================
    # INDULTOS COMPLETOS
    # =====================
    cur.execute("""
        SELECT 
            i.id_indulto,
            CONCAT(inr.nombre, ' ', inr.apellido) as interno,
            inr.ci,
            inr.delito,
            i.motivo,
            i.estado,
            i.fecha_solicitud
        FROM indultos i
        JOIN internos inr ON i.id_interno = inr.id_interno
        ORDER BY i.id_indulto DESC
    """)

    indultos = cur.fetchall()

    # =====================
    # ESTADÍSTICAS
    # =====================
    cur.execute("SELECT COUNT(*) FROM indultos")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM indultos WHERE estado='pendiente'")
    pendientes = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM indultos WHERE estado='aprobado'")
    aprobados = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM indultos WHERE estado='rechazado'")
    rechazados = cur.fetchone()[0]

    cur.close()

    return render_template(
        "indultos.html",
        indultos=indultos,
        internos=internos,
        total=total,
        pendientes=pendientes,
        aprobados=aprobados,
        rechazados=rechazados
    )
# ======================
# RUN
# ======================
if __name__ == '__main__':
    app.run(debug=True)