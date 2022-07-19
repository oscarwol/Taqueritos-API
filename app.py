"""
- API Facturas Taqueritos 
- Version: 1.0
- Created for: WOL Media & Digital Division (soportedev@wol.group)
- License: Wol Media Copyrighted Software
- Author: Oscar E. Morales (oscarmoralesgt.com)

- Rights reserved, This program and code is issued for the purposes that the interested party deems appropriate.
"""

from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from functools import wraps
from jwt import encode, decode
from werkzeug.utils import secure_filename
import os

host = ""
app = Flask(__name__)
CORS(app)
url = "mysql+pymysql://sql3506490:tb9TZcCU7W@sql3.freemysqlhosting.net/sql3506490"
app.config["SQLALCHEMY_DATABASE_URI"] = url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "TAQUERITOS"


# Directorio donde se guardaran las imagenes de factuaras:

# app.config['UPLOAD_FOLDER'] = r"C:\Users\omorales\Desktop\Facturas_Taqueritos\src\Facturas"

db = SQLAlchemy(app)
ma = Marshmallow(app)

""" 
Modelos y Esquemas
"""

# Modelo de Usuarios
class Usuarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    identificacion = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.Integer)
    email = db.Column(db.String(80), unique=True, nullable=False)
    pais = db.Column(db.String(100), nullable=False)
    departamento = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True))

    def __init__(
        self,
        nombres,
        apellidos,
        identificacion,
        telefono,
        email,
        pais,
        departamento,
        created_at,
    ):
        self.nombres = nombres
        self.apellidos = apellidos
        self.identificacion = identificacion
        self.telefono = telefono
        self.email = email
        self.pais = pais
        self.departamento = departamento
        self.created_at = created_at

    def __repr__(self):
        return self.email


# Modelo de Facturas
class Facturas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imagen = db.Column(db.String(100), nullable=False)
    ubicacion = db.Column(db.String(100), nullable=False)
    usuario_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True))

    def __init__(self, imagen, usuario_id, ubicacion, created_at):
        self.imagen = imagen
        self.usuario_id = usuario_id
        self.ubicacion = ubicacion
        self.created_at = created_at

    def __repr__(self):
        return self.id


# Modelos de Mapas
class Mapas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    long = db.Column(db.Float, nullable=False)
    locations = db.Column(db.String(1000), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime)

    def __init__(self, name, lat, long, locations, status, created_at):
        self.name = name
        self.lat = lat
        self.long = long
        self.locations = locations
        self.status = status
        self.created_at = created_at

    def __repr__(self):
        return self.id


db.create_all()
db.session.commit()

# Esquema de Usuarios
class Usuarios_Schema(ma.Schema):
    class Meta:
        fields = (
            "nombres",
            "apellidos",
            "identificacion",
            "telefono",
            "email",
            "pais",
            "departamento",
            "created_a",
        )


usuario_schema = Usuarios_Schema()
usuarios_schema = Usuarios_Schema(many=True)

# Esquema de Factuas
class Facturas_Schema(ma.Schema):
    class Meta:
        fields = ("imagen", "usuario_id", "ubicacion", "created_at")


factura_schema = Facturas_Schema()
facturas_schema = Facturas_Schema(many=True)


# Esquemad de Mapas
class Mapas_Schema(ma.Schema):
    class Meta:
        fields = ("name", "lat", "long", "locations", "status", "created_at")


mapa_schema = Mapas_Schema()
mapas_schema = Mapas_Schema(many=True)


""" 
Funciones del Token y JWT
"""

# Expirar token
def expire_date(days: int):
    now = datetime.now()
    new_date = now + timedelta(days)
    return new_date


# Escribir Token
def write_token(data: dict):
    token = encode(
        payload={**data, "exp": expire_date(1)},
        key=app.config["SECRET_KEY"],
        algorithm="HS256",
    )
    return token.encode("UTF-8")


# Endpoint para verificar si un token esta activo y/o valido
@app.route("/active/<token>", methods=["GET"])
def is_active(token):
    try:
        data = decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        current_user = Usuarios.query.filter_by(id=data["id"]).first()
        experation = datetime.fromtimestamp(data["exp"]).strftime("%Y-%m-%d %H:%M:%S")
        datos = {
            "user_id": current_user.id,
            "email": current_user.email,
            "active_session": True,
            "expiration": experation,
        }
        return datos
    except:
        return jsonify({"message": "Token is invalid !!"}), 401


# decorator para verificar el JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]
        if not token:
            return {"message": "Token no existente"}, 401

        try:
            data = decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = Usuarios.query.filter_by(id=data["id"]).first()
        except:
            return jsonify({"message": "El token no es valido!"}), 401

        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)

    return decorated


def validar_creacion_usuario(identificacion, telefono, email):
    user = Usuarios.query.filter(
        (Usuarios.identificacion == identificacion)
        | (Usuarios.email == email)
        | (Usuarios.telefono == telefono)
    ).first()
    if user:
        return False  # El usuario ya existe, no pasa la validacion
    return True  # El usuario no existe, pasa la validacion


""" 
Funciones de Usuarios (Login, register)
"""


@app.route("/register", methods=["POST"])
def nuevo_usuario():
    try:
        nombres = request.json["nombres"]
        apellidos = request.json["apellidos"]
        identificacion = request.json["identificacion"]
        telefono = request.json["telefono"]
        email = request.json["email"]
        pais = request.json["pais"]
        departamento = request.json["departamento"]
        created_at = datetime.now()

        if validar_creacion_usuario(identificacion, telefono, email):
            nuevo_usurio = Usuarios(
                nombres,
                apellidos,
                identificacion,
                telefono,
                email,
                pais,
                departamento,
                created_at,
            )

            db.session.add(nuevo_usurio)
            db.session.commit()

            guide = Usuarios.query.get(nuevo_usurio.id)

            return usuario_schema.jsonify(guide)
        else:
            response = jsonify(
                {"error": "El registro no pudo ser completado, usuario existente"}
            )
            response.status_code = 409
            return response
    except:
        response = jsonify(
            {"error": "El registro no pudo ser completado, intenta nuevamente"}
        )
        response.status_code = 500
        return response


@app.route("/login", methods=["POST"])
def login():
    identificacion = request.json["identificacion"]
    email = request.json["email"]
    user = Usuarios.query.filter_by(identificacion=identificacion, email=email).first()
    if user:
        id = user.id
        data = request.get_json()
        data["id"] = id
        token_final = str(write_token(data))
        return {"token": token_final}
    else:
        response = jsonify({"message": "El usuario no fue encontrado"})
        response.status_code = 404
        return response


"""
Funciones de facturas:

"""

# Extensiones permitidas
ALLOWED_EXTENSIONS = set(["txt", "pdf", "png", "jpg", "jpeg", "gif"])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_extension(filename):
    return filename.rsplit(".", 1)[1].lower()


# Nueva Factura:
@app.route("/factura", methods=["POST"])
@token_required
def create_factura(current_user):
    if "file" not in request.files:
        resp = jsonify({"message": "No file part in the request"})
        resp.status_code = 400
        return resp
    file = request.files["file"]
    if file.filename == "":
        resp = jsonify({"message": "No file selected for uploading"})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        now = datetime.now()
        current_time = now.strftime("%m:%d:%H:%M:%S")
        file_id = current_time.replace(":", "")
        usuario_id = current_user.id
        created_at = now
        ubicacion = current_user.pais
        new_file_name = (
            str(usuario_id) + "_" + file_id + "." + get_file_extension(file.filename)
        )
        filename = secure_filename(new_file_name)
        # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        nueva_factura = Facturas(filename, usuario_id, ubicacion, created_at)

        db.session.add(nueva_factura)
        db.session.commit()
        guide = Facturas.query.get(nueva_factura.id)
        return factura_schema.jsonify(guide)
    else:
        resp = jsonify(
            {"message": "Allowed file types are txt, pdf, png, jpg, jpeg, gif"}
        )
        resp.status_code = 400
        return resp


# Obtener listado de facturas:
@app.route(host + "/facturas", methods=["GET"])
def get_facturas():
    facs = Facturas.query.all()
    if facs:
        return facturas_schema.jsonify(facs), 200
    return "No hay resultados", 404


""" 
Funciones de Mapas
"""

# Endpoint para crear un nuevo mapa
@app.route("/nuevomapa", methods=["POST"])
def nuevo_mapa():
    try:
        name = request.json["name"]
        lat = request.json["lat"]
        long = request.json["long"]
        locations = request.json["locations"]
        created_at = datetime.now()
        status = 1
        nuevomapa = Mapas(name, lat, long, locations, status, created_at)
        db.session.add(nuevomapa)
        db.session.commit()
        guide = Mapas.query.get(nuevomapa.id)
        return mapa_schema.jsonify(guide)
    except:
        response = jsonify({"error": "El mapa no se guardo correctamente"})
        response.status_code = 500
        return response


# Endpoint para obtener el lsitado de mapas
@app.route(host + "/mapas", methods=["GET"])
def get_mapas():
    maps = Mapas.query.all()
    if maps:
        return mapas_schema.jsonify(maps), 200
    return "No hay resultados", 404


if __name__ == "__main__":
    app.run(debug=True)
