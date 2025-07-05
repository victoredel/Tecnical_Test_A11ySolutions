# Sistema de Gestión de Suscripciones y Métricas

Este proyecto es una API RESTful desarrollada con Flask que permite gestionar clientes, productos, suscripciones y calcular métricas clave de negocio. Utiliza MongoDB como base de datos.

## 🚀 Características

* **Autenticación de Clientes**: Registro y login de clientes con JWT para acceso seguro a la API.

* **Gestión de Productos**: Añadir y listar productos con detalles como precio, periodicidad y si son personalizables.

* **Gestión de Suscripciones**:

    * Suscribir clientes a productos.

    * Verificar el estado de una suscripción (activa/expirada).

    * Obtener y editar la configuración de suscripciones personalizables.

    * Extender la fecha de expiración de las suscripciones.

* **Métricas de Negocio**:

    * **MRR** (Monthly Recurring Revenue): Ingreso recurrente mensual.

    * **ARR** (Annual Recurring Revenue): Ingreso recurrente anual.

    * **ARPU** (Average Revenue Per User): Ingreso promedio por usuario.

    * **CRR** (Customer Retention Rate): Tasa de retención de clientes.

    * **Churn Rate**: Tasa de abandono de clientes.

    * **AOV** (Average Order Value): Valor promedio del pedido.

    * **RPR** (Repeat Purchase Rate): Tasa de compra repetida.

    * **Purchase Frequency**: Frecuencia de compra.

* **CI/CD con GitHub Actions**: Integración continua para automatizar pruebas en cada push/pull request.

## 🛠️ Configuración e Instalación

### Requisitos Previos

* Docker y Docker Compose (recomendado para un setup rápido)

* Alternativamente: Python 3.8+ y MongoDB (si no usas Docker)

### Pasos de Instalación

1.  **Clonar el repositorio**:

    ```
    git clone https://github.com/victoredel/Tecnical_Test_A11ySolutions.git
    cd Tecnical_Test_A11ySolutions
    ```

2.  **Configurar variables de entorno**:
    Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

    ```
    MONGO_URI=mongodb://mongodb:27017/ # Usar el nombre del servicio de MongoDB de Docker Compose
    MONGO_DB_NAME=subscription_manager # Nombre de la base de datos configurado en docker-compose.yml
    JWT_SECRET_KEY=una_clave_secreta_fuerte_para_jwt
    JWT_ACCESS_TOKEN_EXPIRES_SECONDS=3600 # 1 hora
    ```

    **Importante**: Para Docker Compose, `MONGO_URI` debe apuntar al nombre del servicio de MongoDB (`mongodb`) definido en `docker-compose.yml`.

## 🚀 Ejecución de la Aplicación

### Usando Docker Compose (Recomendado)

Esta es la forma más sencilla de levantar la aplicación y la base de datos MongoDB:

1.  **Construir y levantar los servicios**:

    ```
    docker-compose up --build
    ```

    Esto construirá la imagen de Docker para tu backend (si es la primera vez o si hay cambios en el `Dockerfile`) y levantará tanto el servicio de la aplicación Flask como el de MongoDB.

La API estará disponible en `http://localhost:5000`.

### Ejecución Local (Alternativa, sin Docker)

Si prefieres ejecutar la aplicación directamente en tu máquina (asegurándote de tener MongoDB corriendo localmente):

1.  **Crear un entorno virtual** (recomendado):

    ```
    python -m venv venv
    source venv/bin/activate # En Linux/macOS
    # venv\Scripts\activate # En Windows
    ```

2.  **Instalar dependencias**:

    ```
    pip install -r requirements.txt
    ```

    (Si no tienes un `requirements.txt` aún, puedes generarlo con `pip freeze > requirements.txt` después de instalar las dependencias manualmente, o instalarlas directamente:
    `pip install Flask PyJWT pymongo python-dotenv bcrypt pytest pytest-mock`)

3.  **Asegúrate de que MongoDB esté corriendo localmente** y que tu `MONGO_URI` en `.env` apunte a `mongodb://localhost:27017/`.

4.  **Iniciar la aplicación Flask**:

    ```
    python app.py
    ```

    La API estará disponible en `http://0.0.0.0:5000`.

## 🧪 Ejecución de Tests

Para ejecutar las pruebas unitarias con `pytest`:
    
    pytest tests/
    
## ⚙️ CI/CD con GitHub Actions

Este proyecto incluye un flujo de trabajo de GitHub Actions configurado en `.github/workflows/python-app.yml`. Este workflow se ejecuta automáticamente en cada `push` y `pull request` a la rama `main`, instalando las dependencias y ejecutando los tests.

Puedes ver el estado de las ejecuciones de CI en la pestaña "Actions" de tu repositorio de GitHub.

## 🌐 Endpoints de la API

Aquí hay un resumen de los principales endpoints disponibles:

### Autenticación

* `POST /login`: Inicia sesión de un cliente.

* `POST /register_customer`: Registra un nuevo cliente.

### Productos

* `POST /add_product`: Añade un nuevo producto (requiere JWT).

### Suscripciones

* `POST /subscribe`: Suscribe a un cliente a un producto (requiere JWT).

* `GET /subscription_status/<subscription_id>`: Obtiene el estado de una suscripción (requiere JWT).

* `GET /subscription_settings/<subscription_id>`: Obtiene la configuración de una suscripción personalizable (requiere JWT).

* `PUT /edit_subscription_settings/<subscription_id>`: Modifica la configuración de una suscripción (requiere JWT).

* `PUT /extend_subscription/<subscription_id>`: Extiende la fecha de expiración de una suscripción (requiere JWT).

### Métricas

* `GET /metrics/mrr`: Obtiene el MRR actual (requiere JWT).

* `GET /metrics/arr`: Obtiene el ARR actual (requiere JWT).

* `GET /metrics/arpu`: Obtiene el ARPU actual (requiere JWT).

* `GET /metrics/retention?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`: Obtiene la tasa de retención (requiere JWT).

* `GET /metrics/churn?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`: Obtiene la tasa de abandono (requiere JWT).

* `GET /metrics/aov`: Obtiene el AOV (requiere JWT).

* `GET /metrics/rpr`: Obtiene la RPR (requiere JWT).

* `GET /metrics/purchase_frequency`: Obtiene la frecuencia de compra (requiere JWT).