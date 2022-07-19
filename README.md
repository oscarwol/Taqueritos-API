# 🐍 Flask - Facturas Taqueritos API

## 💻 Instalación

Recomiendo utilizar un entorno virtual (virtualenv) para ejecturar este proyecto y no tener problemas de dependencias.

Para ejecutar el proyecto, es necesario clonar el repositorio:

```
git clone https://github.com/oscarwol/Taqueritos-API
cd Taqueritos-API
virtualenv -p python3 .
cd Scripts
activate
cd..
```

Despues, es necesario utilizar el gestor de paquetes de Python (PIP) [pip](https://pip.pypa.io/en/stable/) para instalar todas las dependencias y requerimientos necesarios para ejecutar el proyecto, estos se encuentran en el archivo "requirements.txt".

```
pip install -r requirements.txt
```

## 💾 Creando la Base de datos:
Para este proyecto se utilizo 'SQLAlchemy' un ORM desiñado para flask, por lo tanto; al ejecutar el proyecto todos los modelos serán migrados a la base de datos seleccionada.

No es necesario crear ninguna base de datos de manera manual, solo configurar la siguiente línea de código:

```
25. url = "mysql+pymysql://sql3506490:tb9TZcCU7W@sql3.freemysqlhosting.net/sql3506490"
```
Para configurar la base de datos, ver el ejemplo de arriba y seguir la nomenclatura de datos descrita a continuación:

Usuario: sql3506490
Contraseña: tb9TZcCU7W
Servidor: sql3.freemysqlhosting.net
Base de datos: sql3506490"


## 🚀 Iniciar el Proyecto
Una vez creado el entorno virtual, ejecutado e instaladas todas las dependencias y requerimientos, el proyecto puede ser ejecutado simplemente con la siguiente línea:
```
python app.py 
```


## ⚙️ Uso:

```
localhost:5000
```

El sistema cuenta con 7 'Endpoint' diferentes: 

| HTTP Type | Path | Used For |
| --- | --- | --- |
| `POST` | /login | Endpoint para autenticar y logear al usuario, una autenticación exitosa retornara un token|
| `POST` | /register | Nos permite registrar un nuevo usuario en el sistema |
| `POST` | /factura | Ingresa una nueva factura dentro del sistema |
| `GET` | /facturas | Nos muestra el total de las facturas generadas en el sistema |
| `POST` | /nuevomapa | Crea un nuevo mapa dentro de la base de datos |
| `GET` | /mapas | Retorna el listado total de mapas creados |
| `GET` | /active/{TOKEN} | Nos muestra si un token específico esta activo o no y la información del mismo |


#### Endpoint Login [/login]
```http
  POST /login/
```

Ejemplos de datos a enviar:
```
{
  "email": "usuario@email.com",
  "identificacion": "123456789"
} 
```
---


### Endpoint Register: [/register]
```http
  POST /register/
```

Ejemplos de datos a enviar:
```
{
    "nombres": "Oscar",
    "apellidos": "Morales",
    "identificacion": "12345",
    "telefono": 12345,
    "email": "oscar@oscar.com",
    "pais": "Guatemala",
    "departamento": "Guatemala"
}
```
---


### Endpoint Factura (Crear Factura): [/factura]
```http
  POST /factura
```

Es necesario enviar en el header el token en el campo 'x-access-token'
Ejemplo:
```
'x-access-token': ee4yJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9w2342342342343
```

Luego en el body, debemos enviar el 'File' que contiene la imagen de nuestra factura
```
{
  file: "archivo.jpg",
} 
```
---


### Endpoint Nuevo Mapa: [/nuevomapa]
```http
  POST /nuevomapa/
```

Ejemplos de datos a enviar:
```
{
    "name":"Nicaragua",
    "lat": 25.78341,
    "long": -10.230759,
    "locations": "['Nicaragua Ciudad',14.64072, -90.51327, 4],['Coban Nicaraguense', 15.4833,  -90.3667, 5],['Escuintlagua', 14.2978, -90.7869, 3],['QuetzNicaltenango',      14.7360257, -91.6152074, 2],['Izabal Nica', 15.7379098, -88.5888038, 1]]"
}
```
---

### Endpoint Mapas (Obtener Mapas): [/mapas]
Mediante la ejecución de un simple GET podemos obtener todos los mapas, no es necesario enviar ningun tipo de parametro.
```http
  GET /mapas/
```
---

### Endpoint Facturas (Obtener Facturas [/facturas]
Mediante la ejecución de un simple GET podemos obtener todas las facturas, no es necesario enviar ningun tipo de parametro.

```http
  GET /facturas
```

---

