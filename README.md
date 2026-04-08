# Finance Tracker (Pet Project)

> Учебный pet-проект на FastAPI: трекер личных финансов с JWT-аутентификацией, кошельками, операциями и базовой ролевой моделью.

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.11x-009688)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red)
![Alembic](https://img.shields.io/badge/Alembic-migrations-orange)
![Status](https://img.shields.io/badge/status-learning%20project-yellow)

---

## О проекте

**Finance Tracker** — это мой учебный backend-проект, для изучения:
- проектирования API на FastAPI;
- аутентификации/авторизации (JWT);
- работы с БД через SQLAlchemy (async);
- миграций Alembic;
- слоистой архитектуры (routers / services / repositories).

> ⚠️ **Важно:** это **pet project**, созданный в учебных целях.

---

- Backend-логика, архитектура и API реализуются мной в процессе обучения.
- **Frontend (HTML/CSS/JS) частично создан с помощью ИИ** для ускорения работы над интерфейсом.
- Этот репозиторий отражает мой прогресс, эксперименты и практику, включая рефакторинги по мере роста навыков.

---

## Основной функционал

- Регистрация и логин пользователей
- JWT access token
- Получение текущего пользователя (`/me`)
- Создание и управление кошельками
- Доходы, расходы, переводы
- Базовая ролевая модель (например, `admin` / `user`)
- Password reset flow (forgot/reset password)
- Email-шаблоны для восстановления доступа
- Миграции БД через Alembic
- Интеграции с ИИ и анализ ваших расходов

---

## Технологический стек

- **Backend:** FastAPI, Pydantic, Starlette
- **База данных:** SQLAlchemy 2.x (async), SQLite/PostgreSQL
- **Миграции:** Alembic
- **Auth/Security:** JWT, password hashing
- **Инфраструктура:** Uvicorn, Docker (частично)
- **Шаблоны:** Jinja2 templates (для UI и email)

---

## Архитектура (слои)

Проект организован по слоям:

- `app/api` — роутеры, HTTP-уровень
- `app/service` — бизнес-логика
- `app/repository` — доступ к данным
- `app/models` — ORM-модели
- `app/schemas` — Pydantic-схемы
- `app/core` — security/config/shared utils
- `alembic` — миграции


---

## Что планируется улучшить

- Полноценный RBAC (таблицы ролей/прав + проверки на ресурсы)
- Refresh token + revoke/logout strategy
- Аудит-действий пользователей
- Тесты

---

