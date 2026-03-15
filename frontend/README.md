# PredProf Frontend

Multi-page frontend на HTML/CSS/JS с интеграцией backend API:
- `POST /api/auth/create`
- `POST /api/auth/login`
- `POST /api/civilization/` (mp3)
- `GET /api/analytics/summary` (если нет, используется mock)

## Запуск
Откройте `login.html` через локальный static server (рекомендуется):

```powershell
# пример с Python
python -m http.server 5500
```

После этого откройте `http://localhost:5500/login.html`.

По умолчанию API base url: `http://localhost:8000`.
Можно переопределить в браузере:

```js
localStorage.setItem('apiBaseUrl', 'http://localhost:8000')
```

## Тесты

```powershell
npm test
```
