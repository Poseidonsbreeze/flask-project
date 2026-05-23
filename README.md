# ScholarFind — Full-Stack Scholarship Finder

AI-powered scholarship matching app with a Flask backend and React + Vite frontend.

---

## Project Structure

```
scholarfind-fullstack/
├── backend/              ← Flask API
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routes/
│   │   │   ├── auth_routes.py
│   │   │   └── scholarship_routes.py
│   ├── .env              ← DATABASE_URL (SQLite by default)
│   ├── init_db.py
│   ├── requirements.txt
│   └── run.py
│
└── frontend/             ← React + Vite
    ├── src/
    │   ├── api/client.js       ← All API calls
    │   ├── components/
    │   │   ├── Sidebar.jsx
    │   │   ├── ScholarshipCard.jsx
    │   │   ├── ScholarshipModal.jsx
    │   │   └── Toasts.jsx
    │   ├── hooks/useToast.js
    │   ├── pages/
    │   │   ├── AuthPage.jsx    ← Login + Register
    │   │   ├── Dashboard.jsx
    │   │   ├── ScholarshipsPage.jsx
    │   │   ├── MatchesPage.jsx
    │   │   └── ProfilePage.jsx
    │   ├── App.jsx
    │   ├── index.css
    │   └── main.jsx
    ├── index.html
    ├── package.json
    └── vite.config.js      ← Proxies /api → localhost:5000
```

---

## Quick Start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt

# Create tables (uses SQLite by default)
python init_db.py

# Run Flask
python run.py
# → http://localhost:5000
```

**To use PostgreSQL instead:** edit `.env`:
```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/scholarship_db
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

The Vite dev server proxies all `/api` requests to `http://localhost:5000`.

---

## API Endpoints

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| POST | /api/register | — | Register new user |
| POST | /api/login | — | Login, returns JWT |
| GET | /api/profile | JWT | Get user profile |
| PUT | /api/profile/text | JWT | Update profile text |
| GET | /api/scholarships | — | List all scholarships |
| GET | /api/scholarships/:id | — | Single scholarship |
| POST | /api/scholarships/seed | — | Seed 8 sample scholarships |
| GET | /api/matches | JWT | Get user's matches |
| POST | /api/match | JWT | Run cosine similarity matching |

---

## How Matching Works

1. User fills in their **Profile Text** (field of study, country, interests)
2. Click **Run Matching** on the Dashboard or Matches page
3. Backend runs **TF-IDF cosine similarity** between the profile text and every scholarship's title + description + eligibility
4. Results are saved in the `matches` table with a `similarity_score` (0–1)
5. Frontend displays scores as a percentage with a visual ring indicator

---

## Features

- JWT authentication (login / register)
- Browse and search all scholarships
- AI matching engine with cosine similarity (scikit-learn)
- Match score visualised as a ring chart
- Urgent deadline highlighting
- Profile page to update matching text
- One-click data seeding for development
- Toast notifications throughout
- Clean dark-green design system

