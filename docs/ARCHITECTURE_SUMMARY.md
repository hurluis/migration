# 🎯 Resumen Ejecutivo de Arquitectura

> **Documento de referencia rápida para stakeholders técnicos y de negocio**

---

## 📊 Vista de Alto Nivel

```mermaid
graph TB
    Users[👥 10,000+ Usuarios] -->|HTTPS| Frontend[🎨 Frontend<br/>Nginx + HTML/CSS<br/>TailwindCSS]
    Frontend -->|REST API| Backend[⚡ Backend<br/>FastAPI Python 3.11<br/>Async/Await]
    Backend -->|ORM| Database[(🗄️ PostgreSQL 15<br/>Relational DB)]
    Backend -.->|Métricas| Monitoring[📊 Prometheus + Grafana<br/>Real-time Observability]

    style Users fill:#4A90E2,color:#fff
    style Frontend fill:#50C878,color:#fff
    style Backend fill:#E67E22,color:#fff
    style Database fill:#9B59B6,color:#fff
    style Monitoring fill:#E74C3C,color:#fff
```

---

## 🔑 Características Clave

| Categoría | Características |
|-----------|----------------|
| **🎨 Frontend** | 6 páginas HTML, TailwindCSS, Responsive design, SPA-like experience |
| **⚡ Backend** | FastAPI, Async I/O, OAuth 2.0, REST API, Background tasks |
| **🗄️ Database** | PostgreSQL 15 (prod), SQLite (dev), Connection pooling |
| **📊 Observability** | Prometheus metrics, Grafana dashboards, Custom business metrics |
| **🔐 Security** | OAuth Google, Session management, CORS, Secrets encryption |
| **🚀 Deployment** | Docker Compose, Kubernetes, GitHub Actions CI/CD |
| **📈 Scalability** | Horizontal scaling ready, HPA support, StatefulSet for DB |

---

## 💼 Métricas de Negocio

### KPIs Monitoreados en Tiempo Real

```mermaid
graph LR
    A[📊 Métricas de Negocio] --> B[Total Reservas<br/>✅ Success / ❌ Conflict]
    A --> C[Cancelaciones<br/>Razones clasificadas]
    A --> D[Distribución Estadías<br/>Histogram de noches]
    A --> E[Estado Sistema<br/>Database UP/DOWN]

    style A fill:#E67E22,color:#fff
    style B fill:#50C878,color:#fff
    style C fill:#E74C3C,color:#fff
    style D fill:#4A90E2,color:#fff
    style E fill:#9B59B6,color:#fff
```

**Métricas expuestas**:
- `booking_reservations_total{outcome="success|conflict|invalid"}` - Counter
- `booking_cancellations_total{outcome="success|too_late"}` - Counter
- `booking_reservation_nights` - Histogram (distribución)
- `booking_database_up` - Gauge (0 o 1)

---

## 🏗️ Stack Tecnológico

### Backend
```
Python 3.11
├── FastAPI (Framework web moderno)
├── Uvicorn (ASGI server)
├── SQLAlchemy (ORM)
├── Pydantic (Validación de datos)
├── Authlib (OAuth 2.0)
├── Prometheus Client (Métricas)
└── Pytest (Testing)
```

### Frontend
```
HTML5 + CSS3 + JavaScript
├── TailwindCSS (Styling framework)
├── Fetch API (HTTP client)
└── Nginx (Web server)
```

### Infrastructure
```
Containerización: Docker
Orquestación: Kubernetes/Minikube
CI/CD: GitHub Actions
Registry: Docker Hub
Monitoring: Prometheus + Grafana
Database: PostgreSQL 15
```

---

## 🌐 Arquitectura de 3 Capas

```mermaid
graph TB
    subgraph "Presentation Layer"
        A1[Landing Page]
        A2[Catálogo Propiedades]
        A3[Sistema Reservas]
        A4[Panel Usuario]
        A5[Reviews]
        A6[Admin Panel]
    end

    subgraph "Business Logic Layer"
        B1[Authentication Service]
        B2[Booking Service]
        B3[Property Service]
        B4[Feedback Service]
        B5[Validation Engine]
        B6[Background Tasks]
    end

    subgraph "Data Access Layer"
        C1[(Users Table)]
        C2[(Properties Table)]
        C3[(Reservations Table)]
        C4[(Feedback Table)]
        C5[(Sessions Table)]
    end

    A1 & A2 & A3 & A4 & A5 & A6 --> B1 & B2 & B3 & B4
    B1 & B2 & B3 & B4 --> B5
    B2 --> B6
    B1 --> C1 & C5
    B2 --> C2 & C3
    B3 --> C2
    B4 --> C4

    style A1 fill:#4A90E2,color:#fff
    style B1 fill:#50C878,color:#fff
    style C1 fill:#9B59B6,color:#fff
```

---

## 🔄 Flujo de Usuario Principal

### Proceso de Reserva (Happy Path)

```mermaid
sequenceDiagram
    autonumber
    actor Usuario
    Usuario->>Frontend: Selecciona propiedad y fechas
    Frontend->>Backend: POST /api/reserve
    Backend->>DB: Verifica disponibilidad
    DB-->>Backend: Fechas disponibles ✅
    Backend->>DB: Crea reserva
    DB-->>Backend: Reserva confirmada
    Backend->>Prometheus: Incrementa métrica success
    Backend-->>Frontend: 200 OK + datos
    Frontend-->>Usuario: Confirmación visual 🎉
```

**Tiempo promedio**: < 200ms (p95)

---

## 📦 Entornos de Deployment

| Entorno | Infraestructura | Base de Datos | Réplicas | Costo/mes |
|---------|----------------|---------------|----------|-----------|
| **Desarrollo** | Docker Compose | SQLite / PostgreSQL | 1 de cada | $0 |
| **Testing** | Minikube (K8s) | PostgreSQL 15 | 1 de cada | $0 |
| **Producción** | EKS/GKE/AKS | RDS/Cloud SQL (Multi-AZ) | 5-20 (HPA) | ~$750 |

---

## 🚀 Pipeline CI/CD

```mermaid
graph LR
    A[Git Push] --> B{GitHub Actions}
    B --> C[Run Tests<br/>pytest]
    C -->|✅ Pass| D[Build Docker<br/>Backend + Frontend]
    C -->|❌ Fail| Z[Notificar Error]
    D --> E[Tag Images<br/>latest + SHA]
    E --> F[Push to<br/>Docker Hub]
    F --> G[Auto Deploy Dev]
    F --> H{Manual Approve<br/>Production?}
    H -->|✅ Yes| I[Canary Deploy<br/>10% traffic]
    I --> J{Métricas OK?}
    J -->|✅ Yes| K[Full Deploy<br/>100%]
    J -->|❌ No| L[Auto Rollback]

    style C fill:#E67E22
    style K fill:#50C878
    style L fill:#E74C3C
```

**Tiempo de deployment**: ~5-10 minutos (dev) | ~15-20 minutos (prod)

---

## 🔒 Seguridad

### Capas de Seguridad Implementadas

```mermaid
mindmap
  root((🔒 Seguridad))
    Autenticación
      OAuth 2.0 Google
      Session Management
      JWT Tokens futuro
    Autorización
      Role-based permisos
      API Key validation
    Network
      CORS configurado
      HTTPS only prod
      WAF futuro
    Data
      Secrets K8s
      Encrypted at rest
      Connection pooling
    Monitoring
      Audit logs
      Failed login tracking
      Anomaly detection futuro
```

---

## 📈 Escalabilidad y Rendimiento

### Capacidad Actual vs Objetivo

| Métrica | Desarrollo | Testing | Producción |
|---------|-----------|---------|------------|
| **Usuarios concurrentes** | 10 | 50 | 10,000+ |
| **Requests/segundo** | 10 | 50 | 1,000+ |
| **Latencia p95** | < 500ms | < 300ms | < 200ms |
| **Disponibilidad** | N/A | 95% | 99.9% |
| **Réplicas Backend** | 1 | 1 | 5-20 (HPA) |
| **DB Connections** | 5 | 20 | 100+ (pool) |

### Estrategias de Scaling

```mermaid
graph TB
    A[Tráfico Aumenta] --> B{CPU > 70%?}
    B -->|Sí| C[HPA escala pods]
    B -->|No| D[Mantener réplicas]

    C --> E{Nodes suficientes?}
    E -->|No| F[Cluster Autoscaler<br/>añade nodos]
    E -->|Sí| G[Distribuir carga]

    A --> H{Queries lentas?}
    H -->|Sí| I[Añadir índices DB]
    H -->|No| J[OK]

    A --> K{Cache miss alto?}
    K -->|Sí| L[Implementar Redis]
    K -->|No| M[OK]

    style C fill:#50C878
    style F fill:#E67E22
    style L fill:#4A90E2
```

---

## 🎯 Roadmap Técnico

### Q1 2025
- [x] Arquitectura base con FastAPI + PostgreSQL
- [x] Frontend responsive con TailwindCSS
- [x] Observabilidad con Prometheus + Grafana
- [x] CI/CD con GitHub Actions
- [x] Deployment en Kubernetes

### Q2 2025 (Propuesto)
- [ ] Implementar Redis para caching
- [ ] Añadir Elasticsearch para búsqueda
- [ ] WebSockets para notificaciones en tiempo real
- [ ] Sistema de pagos (Stripe/PayPal)
- [ ] Email notifications (SendGrid)

### Q3 2025 (Propuesto)
- [ ] Migración a microservicios
- [ ] Service mesh (Istio)
- [ ] GraphQL API
- [ ] Mobile app (React Native)
- [ ] Machine Learning para recomendaciones

---

## 💰 Análisis de Costos (Producción)

### Breakdown Mensual (AWS)

```mermaid
pie title Costos Mensuales AWS ($750/mes)
    "RDS PostgreSQL" : 280
    "EC2 Kubernetes Nodes" : 190
    "EKS Control Plane" : 75
    "ElastiCache Redis" : 100
    "CloudFront CDN" : 85
    "ALB + Route53" : 20
```

### Optimizaciones de Costo Futuras
1. **Reserved Instances**: Ahorro 30-40%
2. **Spot Instances** para workers: Ahorro 60-70%
3. **Auto-scaling agresivo**: Reduce costos en horas valle
4. **CDN caching**: Reduce origen requests 80%

---

## 🎓 Decisiones de Arquitectura (ADRs)

### 1. FastAPI sobre Flask/Django
**Razón**: Performance async/await, documentación automática OpenAPI, type hints nativos

### 2. PostgreSQL sobre MongoDB
**Razón**: Transacciones ACID para reservas, relaciones claras, madurez del ecosistema

### 3. Kubernetes sobre Docker Compose en producción
**Razón**: Auto-healing, scaling horizontal, rolling updates, ecosystem maduro

### 4. Prometheus sobre otros sistemas de métricas
**Razón**: Estándar de facto, integración nativa con K8s, PromQL potente

### 5. TailwindCSS sobre Bootstrap
**Razón**: Utility-first, bundle size menor, customización más flexible

---

## 📞 Contactos del Proyecto

| Rol | Responsabilidad | Contacto |
|-----|----------------|----------|
| **Tech Lead** | Arquitectura y decisiones técnicas | tech-lead@proyecto.com |
| **DevOps Lead** | Infraestructura y deployments | devops@proyecto.com |
| **Product Owner** | Priorización de features | po@proyecto.com |
| **Security Officer** | Auditorías y compliance | security@proyecto.com |

---

## 📚 Recursos Adicionales

- [📖 Documentación Completa](./README.md)
- [🔄 Diagramas de Flujo](./ARCHITECTURE_FLOWS.md)
- [🌍 Guía de Deployment](./DEPLOYMENT_ENVIRONMENTS.md)
- [🐙 Repositorio GitHub](https://github.com/JULILYHERRERA/AIRBNB_GESTION)
- [🐋 Docker Hub Images](https://hub.docker.com/u/julilyherrera)

---

**Versión**: 1.1.0
**Última actualización**: 2025-11-11
**Estado**: ✅ En producción (Minikube) | 🚧 Cloud en desarrollo

---

<div align="center">

### 🎯 Construido con excelencia técnica

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

</div>
