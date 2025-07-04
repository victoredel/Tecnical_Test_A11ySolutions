# Gestión de Suscripciones de Clientes (Modular y Organizada con Seguridad JWT)

Este proyecto es un sistema de backend para gestionar suscripciones de clientes a productos, implementado con Python (Flask) y MongoDB. La estructura está modularizada en directorios para una mejor organización y mantenibilidad, e incorpora un sistema de seguridad basado en JSON Web Tokens (JWT).

## Estructura del Proyecto

* `app.py`: Punto de entrada de la aplicación Flask y definición de las rutas de la API.
* `config.py`: Maneja la configuración de la aplicación (e.g., URI de MongoDB, clave secreta JWT).
* `database.py`: Gestiona la conexión y desconexión con la base de datos MongoDB.
* `models/`: Directorio que contiene las definiciones de las estructuras de datos.
    * `customer.py`: Define el modelo de datos para los clientes, incluyendo ahora la contraseña hasheada.
    * `product.py`: Define el modelo de datos para los productos.
    * `subscription.py`: Define el modelo de datos para las suscripciones.
    * `__init__.py`: (vacío) Indica que `models` es un paquete Python.
* `services/`: Directorio que contiene la lógica de negocio.
    * `auth_service.py`: **[NUEVO]** Contiene la lógica para el registro y login de clientes, y la generación de JWTs.
    * `subscription_service.py`: Contiene la lógica de negocio principal para las operaciones relacionadas con productos y suscripciones.
    * `__init__.py`: (vacío) Indica que `services` es un paquete Python.
* `utils/`: Directorio para utilidades y funciones auxiliares.
    * `auth.py`: **[MODIFICADO]** Implementa el decorador para la verificación de JWT.
    * `security.py`: **[NUEVO]** Contiene funciones para el hashing y verificación de contraseñas.
    * `__init__.py`: (vacío) Indica que `utils` es un paquete Python.
* `requirements.txt`: Lista las dependencias del proyecto.
* `.env`: Almacena variables de entorno (e.g., credenciales de la DB, clave secreta JWT).
* `Dockerfile`: Define cómo construir la imagen de Docker para la aplicación.
* `docker-compose.yml`: Orquesta los contenedores Docker (aplicación y base de datos).
* `README.md`: Este documento con instrucciones y detalles del proyecto.

## Requisitos

* Docker y Docker Compose (recomendado para un setup sencillo)
* Python 3.9+ (si no usas Docker)
* MongoDB (si no usas Docker)

## Configuración del Entorno (con Docker Compose - Recomendado)

1.  **Clona el repositorio:**
    ```bash
    git clone <URL_TU_REPOSITORIO>
    cd <nombre_del_repositorio>
    ```

2.  **Crea el archivo de variables de entorno `.env`:**
    Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:
    ```
    MONGO_URI=mongodb://mongodb:27017/
    MONGO_DB_NAME=subscription_manager
    JWT_SECRET_KEY=super_secreta_jwt_key_que_debes_cambiar_EN_SERIO # ¡Usa una clave fuerte y cámbiala!
    JWT_ACCESS_TOKEN_EXPIRES_SECONDS=3600 # Token expira en 1 hora
    ```

3.  **Inicia los servicios con Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    Esto construirá la imagen de Docker para el backend, instalará las nuevas dependencias (`PyJWT`, `bcrypt`), iniciará el contenedor de MongoDB y el contenedor del backend. La aplicación estará disponible en `http://localhost:5000`.

## Configuración del Entorno (local sin Docker)

1.  **Instala Python:** Asegúrate de tener Python 3.9 o superior instalado.

2.  **Instala MongoDB:** Instala MongoDB en tu sistema y asegúrate de que esté corriendo (normalmente en `mongodb://localhost:27017/`).

3.  **Crea un entorno virtual (recomendado):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

4.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Crea el archivo de variables de entorno `.env`:**
    Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:
    ```
    MONGO_URI=mongodb://localhost:27017/ # Ajusta si tu Mongo no está en localhost
    MONGO_DB_NAME=subscription_manager
    JWT_SECRET_KEY=super_secreta_jwt_key_que_debes_cambiar_EN_SERIO # ¡Usa una clave fuerte y cámbiala!
    JWT_ACCESS_TOKEN_EXPIRES_SECONDS=3600
    ```

6.  **Inicia la aplicación:**
    ```bash
    python app.py
    ```
    La aplicación se ejecutará en `http://localhost:5000`.

## Endpoints de la API

Todos los endpoints base son `http://localhost:5000`.

### Seguridad de la API (JSON Web Tokens - JWT)

La mayoría de los endpoints que modifican o consultan datos sensibles ahora requieren autenticación mediante JWT.

**Flujo de Autenticación:**

1.  **Registrar un cliente**: Usa el endpoint `/register_customer` con `email` y `password`.
2.  **Iniciar sesión**: Usa el endpoint `/login` con el `email` y `password` del cliente registrado. Recibirás un `access_token` JWT.
3.  **Hacer solicitudes protegidas**: Incluye el `access_token` en el encabezado `Authorization` de tus solicitudes, con el formato `Bearer <your_jwt_token>`.

**Endpoints Nuevos/Modificados:**

* **`POST /register_customer`** (Modificado)
    Registra un nuevo cliente con nombre, email y contraseña.
    * **Body:** `{"name": "Nombre Cliente", "email": "cliente@example.com", "password": "secure_password"}`
    * **Respuesta Exitosa (201 Created):** `{"message": "Customer registered successfully", "customer_id": "..."}`
    * **Respuesta de Error (400 Bad Request):** `{"error": "Name, email, and password are required"}`
    * **Respuesta de Error (409 Conflict):** `{"error": "Customer with this email already exists"}`

* **`POST /login`** (Nuevo)
    Inicia sesión de un cliente y retorna un JWT.
    * **Body:** `{"email": "cliente@example.com", "password": "secure_password"}`
    * **Respuesta Exitosa (200 OK):** `{"message": "Login successful", "access_token": "..."}`
    * **Respuesta de Error (400 Bad Request):** `{"error": "Email and password are required"}`
    * **Respuesta de Error (401 Unauthorized):** `{"error": "Invalid credentials"}`

**Endpoints Protegidos con JWT (requieren `Authorization: Bearer <token>`):**

* `POST /add_product`
    Añade un nuevo producto.
    * **Body:** `{"name": "Nombre Producto", "description": "Descripción", "customizable": true/false}`
    * **Respuesta Exitosa (201 Created):** `{"message": "Product added successfully", "product_id": "..."}`
    * **Respuesta de Error (400 Bad Request):** `{"error": "Name and description are required"}`
    * **Respuesta de Error (409 Conflict):** `{"error": "Product with this name already exists"}`

* `POST /subscribe`
    Permite a un cliente suscribirse a un producto.
    * **Body:** `{"customer_id": "...", "product_id": "...", "expiration_date": "YYYY-MM-DDTHH:MM:SS", "customization": {"key": "value"}}` (el campo `customization` es opcional y solo para productos personalizables)
    * **Respuesta Exitosa (201 Created):** `{"message": "Subscription created successfully", "subscription_id": "..."}`
    * **Respuestas de Error (400, 404, 409, 500):** Detalles en la sección de "Respuestas de Error relacionadas con JWT" y en el código de la API.

* **`GET /subscription_status/<subscription_id>`**
    Obtiene el estado (activo/expirado) de una suscripción.
    * **Respuesta Exitosa (200 OK):** `{"subscription_id": "...", "status": "active/expired"}`
    * **Respuestas de Error (400, 404):** Detalles en la sección de "Respuestas de Error relacionadas con JWT" y en el código de la API.

* **`GET /subscription_settings/<subscription_id>`**
    Obtiene la configuración específica de una suscripción (personalización).
    * **Respuesta Exitosa (200 OK):** `{"subscription_id": "...", "settings": {"key": "value"}}`
    * **Respuestas de Error (400, 404, 500):** Detalles en la sección de "Respuestas de Error relacionadas con JWT" y en el código de la API.

* **`PUT /edit_subscription_settings/<subscription_id>`**
    Modifica la configuración de una suscripción.
    * **Body:** `{"settings": {"new_key": "new_value"}}`
    * **Respuesta Exitosa (200 OK):** `{"message": "Subscription settings updated successfully"}` (o `{"message": "Settings already up to date, no changes made"}`)
    * **Respuestas de Error (400, 404, 500):** Detalles en la sección de "Respuestas de Error relacionadas con JWT" y en el código de la API.

* **`PUT /extend_subscription/<subscription_id>`**
    Establece una nueva fecha de caducidad para una suscripción.
    * **Body:** `{"new_expiration_date": "YYYY-MM-DDTHH:MM:SS"}`
    * **Respuesta Exitosa (200 OK):** `{"message": "Subscription extended successfully"}` (o `{"message": "Subscription expiration date already set to this value"}`)
    * **Respuestas de Error (400, 404, 500):** Detalles en la sección de "Respuestas de Error relacionadas con JWT" y en el código de la API.

### Respuestas de Error relacionadas con JWT:

* **401 Unauthorized**:
    * `{"error": "Authorization header is missing"}`
    * `{"error": "Invalid Authorization header format"}`
    * `{"error": "Unsupported authorization type"}`
    * `{"error": "Token has expired"}`
    * `{"error": "User specified in token not found"}`
* **401 Unauthorized**: `{"error": "Invalid token"}`

## Cómo Probar (Ejemplos con `curl`)

Asumiendo que la API está corriendo en `http://localhost:5000`.

1.  **Registrar un cliente (si no tienes uno):**
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"name": "Juan Perez", "email": "juan.perez@example.com", "password": "mipasswordseguro"}' http://localhost:5000/register_customer
    ```

2.  **Iniciar sesión para obtener el token:**
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"email": "juan.perez@example.com", "password": "mipasswordseguro"}' http://localhost:5000/login
    # La respuesta contendrá un campo "access_token". Copia ese valor para las siguientes solicitudes.
    ```
    Suponiendo que el token es `YOUR_JWT_TOKEN_HERE`.

3.  **Añadir un Producto (requiere token):**
    ```bash
    curl -X POST -H "Content-Type: application/json" \
         -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
         -d '{"name": "Widget Accesibilidad", "description": "Widget para mejorar la accesibilidad de tu web", "customizable": true}' \
         http://localhost:5000/add_product
    ```

4.  **Suscribir un Cliente a un Producto (requiere token):**
    (Necesitarás los `customer_id` y `product_id`. Reemplaza `CUST_ID`, `PROD_ID` y `YOUR_JWT_TOKEN_HERE`).
    ```bash
    curl -X POST -H "Content-Type: application/json" \
         -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
         -d '{
            "customer_id": "CUST_ID",
            "product_id": "PROD_ID",
            "expiration_date": "2026-12-31T23:59:59",
            "customization": {
                "topBarColor": "#FFFFFF",
                "topBarBackgroundColor": "#1A1A1A",
                "positionIndex": 1,
                "defaultLang": "es"
            }
        }' http://localhost:5000/subscribe
    ```

5.  **Obtener Estado de Suscripción (requiere token):**
    (Reemplaza `SUB_ID` y `YOUR_JWT_TOKEN_HERE`).
    ```bash
    curl -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" http://localhost:5000/subscription_status/SUB_ID
    ```

6.  **Obtener Configuración de Suscripción (requiere token):**
    (Reemplaza `SUB_ID` y `YOUR_JWT_TOKEN_HERE`).
    ```bash
    curl -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" http://localhost:5000/subscription_settings/SUB_ID
    ```

7.  **Editar Configuración de Suscripción (requiere token):**
    (Reemplaza `SUB_ID` y `YOUR_JWT_TOKEN_HERE`).
    ```bash
    curl -X PUT -H "Content-Type: application/json" \
         -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
         -d '{"settings": {"topBarColor": "#FF0000", "defaultLang": "en"}}' \
         http://localhost:5000/edit_subscription_settings/SUB_ID
    ```

8.  **Extender Suscripción (requiere token):**
    (Reemplaza `SUB_ID` y `YOUR_JWT_TOKEN_HERE`).
    ```bash
    curl -X PUT -H "Content-Type: application/json" \
         -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
         -d '{"new_expiration_date": "2027-12-31T23:59:59"}' \
         http://localhost:5000/extend_subscription/SUB_ID
    ```

## Consideraciones Adicionales y Puntos Extra

El documento original menciona varias ideas y puntos extra que pueden "boostear la posibilidad de ser aceptado para el puesto". Aunque no son requisitos estrictos, demuestran un conocimiento más profundo.

1.  [cite_start]**Contenedorización del Proyecto**: Ya implementado con Docker y Docker Compose. [cite: 51]
2.  [cite_start]**Creación de un Frontend**: Implementar una interfaz de usuario para el proyecto (React es un plus). [cite: 52]
3.  [cite_start]**Seguridad de la API**: Ya implementado con JWT. [cite: 53]
4.  [cite_start]**Métricas Financieras**: Incluir precio y periodicidad en la suscripción y modificar la API para calcular estadísticas como MRR, ARR, ARPU, CLV, CRR, CR, AOV, RPR. [cite: 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64]
5.  [cite_start]**Visualizaciones Frontend de las Métricas**: Si se implementan las estadísticas financieras, crear visualizaciones en el frontend. [cite: 65]
6.  [cite_start]**Pruebas (Testing)**: Añadir pruebas unitarias o de integración (`pytest` es altamente valorado). [cite: 66]
7.  [cite_start]**Pipelines de CI/CD**: Implementar pipelines de Integración Continua/Despliegue Continuo (e.g., con GitHub Actions). [cite: 67]

**Recomendaciones Finales del Documento:**

* [cite_start]No dudes en preguntar si tienes alguna duda. [cite: 69]
* [cite_start]La entrega no tiene una fecha límite estricta, pero se necesita aumentar el equipo lo antes posible, así que no intentes implementar todos los puntos extra. [cite: 73, 74]
* [cite_start]Haz lo que sabes hacer bien y el resto se puede discutir en la llamada de revisión. [cite: 75]
* [cite_start]Si te quedas atascado o crees que puedes enriquecer el proyecto, siéntete libre de añadir tus propias características o adaptar un poco los requisitos. [cite: 76]
* [cite_start]Puedes usar otras herramientas que no sean las recomendadas, siempre y cuando uses Python y MongoDB. [cite: 77]