# Frontend WebPredictor

Frontend estático (HTML/CSS/JS) para la API FastAPI de WebPredictor. Proporciona:
- Login para obtener token JWT (endpoint `/auth/login`).
- Consulta de scopes (`/auth/scopes`).
- Interfaz para entrenamiento y predicción tabular (`/tabular_regressor/train_predict`).
- Listado de modelos disponibles (`/tabular_regressor/available_models`).

## Estructura
```
frontend/
  index.html            # Página principal (login + tabular)
  styles/
    variables.css       # Variables de diseño (tema oscuro)
    main.css            # Estilos globales y layout responsive
  js/
    dom.js              # Helpers DOM + sanitización
    api.js              # Cliente API (fetch wrapper + token)
    auth.js             # Lógica de autenticación y navegación
    tabular_regressor.js# Lógica de entrenamiento y predicción
  README.md             # Este documento
```

## Uso en desarrollo
Asegúrate de tener la API corriendo en `http://localhost:8000`.

Abrir directamente `frontend/index.html` en el navegador (o servir con un servidor estático para evitar restricciones de CORS si se endurece CSP).

### Servir con un servidor simple
```bash
# Python 3
python -m http.server 5173 --directory frontend
# Luego visitar http://localhost:5173
```
Si cambias el puerto o dominio de la API, actualiza `API_BASE` en `js/api.js` y la directiva `connect-src` de la meta CSP en `index.html`.

## Seguridad
- CSP restrictiva: bloquea recursos de terceros por defecto. Ajusta `connect-src` para el dominio real en producción.
- No se usan scripts inline (permitiendo `script-src 'self'`).
- Sanitización básica de texto (`sanitizeText`) para evitar inyecciones simples al renderizar mensajes.
- Evita `innerHTML` salvo en tablas generadas de datos ya estructurados; si se añaden campos libres del usuario deben sanitizarse.
- Tokens se guardan sólo en memoria (no localStorage) reduciendo impacto de XSS persistente.
- Recomendado servir con cabeceras adicionales:
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy: interest-cohort=()`

## Flujo de Login
1. Usuario introduce credenciales y scopes opcionales.
2. Se envía `application/x-www-form-urlencoded` a `/auth/login`.
3. Respuesta: token JWT + scopes otorgados.
4. Token se añade a encabezados `Authorization: Bearer <token>` en peticiones posteriores.

## Entrenar y Predecir
- Usuario selecciona modelo y define columnas target y opcionalmente feature.
- Pega CSV de entrenamiento y predicción.
- Se construye payload acorde al schema `TrainPredictRequest`.
- Respuesta incluye métricas y predicciones, renderizadas en tablas.

## Adaptación / Escalabilidad
Para crecer:
- Separar vistas en más archivos HTML y usar build (ej. Vite) si se requiere bundling.
- Añadir router de cliente (History API) para mejorar navegación.
- Implementar almacenamiento protegido para token vía HTTP-only cookies (requiere cambios backend y CSRF).

## Producción
- Ajustar API_BASE.
- Revisar CSP (quitar `localhost:8000`, poner dominio oficial, añadir `https:`).
- Minificar CSS/JS (pipeline de build opcional).
- Configurar Nginx para servir `frontend/` como static root y proxy_pass API.

## TODO Mejoras Futuras
- Validación CSV más robusta y manejo de errores por campo.
- Descarga de resultados como CSV.
- Internacionalización.
- Gestión de sesiones con expiración y refresco.

---
© 2025 WebPredictor
