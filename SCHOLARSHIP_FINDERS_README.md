# ScholarFind Project Documentation

## Overview

ScholarFind is a comprehensive scholarship matching platform that helps students find suitable academic opportunities based on their profile and interests. The system features AI-powered matching, calendar management, profile optimization, and real-time scraping of scholarship opportunities.

## Key Features

### 1. Scholarship Matching Engine
- AI-powered cosine similarity matching
- Natural language processing for profile analysis
- Field-specific preference scoring
- Deadline-based ranking and filtering

### 2. Calendar UI
- Interactive calendar with scholarship deadlines
- Urgent deadline highlighting
- Date-based event filtering
- Mobile-responsive design

### 3. Profile Management & Optimization
- Intelligent profile text generation
- Field preference analysis
- Text validation and optimization
- Profile-to-scholarship matching

### 4. Scholarship Scraping & Data Management
- Multi-source scholarship scraping
- Detail page extraction (full scholarship details)
- Deadline and eligibility parsing
- Duplicate detection and deduplication

### 5. User Authentication & Security
- JWT-based authentication
- Secure password hashing
- Role-based access control
- Session management

## Backend API

### Base URL
`http://localhost:5000/api`

### Authentication Endpoints

#### Register
```http
POST /api/register
```
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

#### Login
```http
POST /api/login
```
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

#### Get Profile
```http
GET /api/profile
```
```json
{
  "id": 1,
  "full_name": "John Doe",
  "email": "john@example.com",
  "profile_text": "Computer science student with programming experience...",
  "created_at": "2026-06-23T09:51:59.123Z"
}
```

#### Update Profile Text
```http
PUT /api/profile/text
```
```json
{
  "profile_text": "Computer science student with programming experience..."
}
```

#### Analyze Profile
```http
POST /api/profile/analyze
```
```json
{
  "profile_text": "Computer science student with programming experience..."
}
```

**Response:**
```json
{
  "profile_text": "Computer science student with programming experience...",
  "field_scores": {
    "computer_science": 0.85,
    "data_science": 0.45,
    "engineering": 0.30,
    "business": 0.20,
    "arts": 0.10,
    "sciences": 0.15
  }
}
```

#### Generate Profile from Scholarships
```http
POST /api/profile/generate
```
```json
{
  "scholarship_ids": [1, 2, 3]
}
```

**Response:**
```json
{
  "generated_text": "With strong computer science background and solid data science skills, seeking relevant opportunities. Based in USA, seeking suitable academic opportunities and funding support.",
  "validation": {
    "length": 156,
    "word_count": 28,
    "has_education_keywords": true,
    "has_experience_keywords": true,
    "has_goals_keywords": true,
    "score": 0.85,
    "suggestions": []
  }
}
```

#### Validate Profile Text
```http
POST /api/profile/validate
```
```json
{
  "profile_text": "Computer science student with programming experience..."
}
```

#### Optimize Profile Text
```http
POST /api/profile/optimize
```
```json
{
  "profile_text": "Computer science student"
}
```

**Response:**
```json
{
  "optimized_text": "Computer science student with programming experience and machine learning background, seeking relevant opportunities. I am actively seeking academic and professional development opportunities.",
  "validation": {
    "length": 198,
    "word_count": 35,
    "has_education_keywords": true,
    "has_experience_keywords": true,
    "has_goals_keywords": true,
    "score": 0.90,
    "suggestions": []
  }
}
```

### Scholarship Management Endpoints

#### Get All Scholarships
```http
GET /api/scholarships
```

#### Create Scholarship
```http
POST /api/scholarships
```

#### Get Calendar
```http
GET /api/calendar
```

**Response:**
```json
{
  "upcoming": [
    {
      "id": 2093,
      "title": "Test Future Deadline",
      "provider": "Test",
      "country": "USA",
      "degree_level": null,
      "deadline": "2026-06-25",
      "application_link": "http://example.com",
      "days_until": 2,
      "is_urgent": false
    }
  ],
  "past": [
    {
      "id": 1,
      "title": "AI Research Scholarship",
      "provider": "Tech Corp",
      "country": "USA",
      "degree_level": "Masters",
      "deadline": "2025-12-31",
      "application_link": "http://example.com/1",
      "days_until": -193,
      "is_urgent": false
    }
  ],
  "total_upcoming": 1,
  "total_past": 3
}
```

#### Get Upcoming Deadlines
```http
GET /api/deadlines/upcoming?days=30
```

### Matching Endpoint

#### Get Matches
```http
GET /api/match
```

**Response:**
```json
[
  {
    "id": 2093,
    "title": "Test Future Deadline",
    "provider": "Test",
    "country": "USA",
    "degree_level": null,
    "eligibility": null,
    "description": null,
    "deadline": "2026-06-25",
    "application_link": "http://example.com",
    "score": 0.823
  }
]
```

### Scrape Endpoint

#### Run Scrapers
```http
GET /api/scrape/run
```

## Frontend Components

### Dashboard
- Overview of scholarships and matches
- Quick actions for seeding and matching
- Statistics cards

### Scholarships Page
- Browse all available scholarships
- Filter and search functionality
- Scholarship details view

### Calendar View
- Interactive calendar with deadline visualization
- Date-based event filtering
- Detailed event cards
- Mobile-responsive design

### Matches Page
- View matched scholarships
- Re-run matching algorithm
- Scholarship details with scores

### Profile Page
- Edit profile text
- Generate profile from selected scholarships
- Validate and optimize profile text
- View profile statistics

## Technologies Used

### Backend (Python/Flask)
- **Framework**: Flask 3.1
- **Database**: PostgreSQL (via SQLAlchemy)
- **Authentication**: Flask-JWT-Extended
- **Scraping**: BeautifulSoup, Requests
- **ML**: scikit-learn (TF-IDF, Cosine Similarity)
- **Scheduling**: APScheduler
- **Security**: Password hashing, Input validation

### Frontend (React)
- **Framework**: React 18.3.1
- **Styling**: CSS3 with responsive design
- **Icons**: Lucide React
- **Calendar**: React Calendar with Moment.js
- **State Management**: React hooks

### Development Tools
- **Backend**: Python 3.13, pip
- **Frontend**: Node.js, npm, Vite
- **Database**: PostgreSQL

## Installation & Setup

### Backend Setup
```bash
# Clone repository
cd scholarfind-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Run the application
python run.py
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd scholarfind-frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Environment Variables
Create `.env` file in backend directory:
```env
DATABASE_URL=postgresql://postgres:1234@localhost:5432/scholarship_db
JWT_SECRET_KEY=your-secret-key-change-me
FLASK_DEBUG=1
```

## Development

### Running Scrapers
Scholars are automatically scraped every 6 hours via the built-in scheduler. To run them manually:

```bash
# From backend directory
python -c "from app.scraping.scraper_engine import run_all_scrapers; run_all_scrapers()"
```

### Testing
Run the Flask development server with:
```bash
python run.py
```

### Frontend Development
Run the Vite development server with:
```bash
npm run dev
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models.py
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── match_routes.py
│   │   ├── scholarship_routes.py
│   │   └── scrape_routes.py
│   ├── matching/
│   │   └── match_engine.py
│   ├── scraping/
│   │   └── scraper_engine.py
│   └── utils.py
├── init_db.py
├── run.py
└── requirements.txt

frontend/
├── public/
├── src/
│   ├── api/
│   │   └── client.js
│   ├── components/
│   │   ├── CalendarView.jsx
│   │   ├── ScholarshipCard.jsx
│   │   ├── ScholarshipModal.jsx
│   │   ├── Sidebar.jsx
│   │   └── Toasts.jsx
│   ├── hooks/
│   │   └── useToast.js
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   ├── MatchesPage.jsx
│   │   ├── ProfilePage.jsx
│   │   ├── ScholarshipsPage.jsx
│   │   ├── ArchivedPage.jsx
│   │   └── AuthPage.jsx
│   ├── App.jsx
│   └── index.css
├── package.json
└── vite.config.js
```

## Features Summary

### Production-Ready Features
- **Secure Authentication**: JWT-based with password hashing
- **Data Validation**: Comprehensive input validation and sanitization
- **Error Handling**: Robust error handling with proper HTTP status codes
- **Calendar Integration**: Full-featured calendar with responsive design
- **Profile Optimization**: Intelligent text generation and analysis
- **Scrapping**: Automated scholarship scraping with detail extraction

### User Experience
- **Responsive Design**: Mobile-first, accessible UI
- **Real-time Updates**: Live matching and calendar updates
- **Search & Filter**: Advanced filtering and search capabilities
- **Notifications**: Toast notifications for user actions

### Performance & Scalability
- **Caching**: Strategic caching for better performance
- **Async Operations**: Non-blocking I/O for better responsiveness
- **Database Optimization**: Efficient queries and indexing
- **Memory Management**: Proper resource cleanup

## API Rate Limiting

The API includes:
- Request validation and rate limiting
- Proper error handling for invalid requests
- Input sanitization to prevent injection attacks
- Secure session management

## Testing

While comprehensive unit and integration tests are recommended for production deployment, the current implementation includes:
- Manual testing of all endpoints
- Error handling validation
- Authentication flow verification
- Database operation testing

## Migration Notes

When upgrading from previous versions:
- Database schema changes: Run `init_db.py` to update
- API changes: Update frontend client.js accordingly
- Authentication: All user accounts need to reset passwords (if hashed)

## Troubleshooting

### Common Issues

1. **Connection Issues**
   - Ensure PostgreSQL is running
   - Verify database credentials in `.env` file
   - Check firewall settings

2. **Frontend Backend Mismatch**
   - Ensure both servers are running on correct ports
   - Check CORS configuration
   - Verify API base URLs

3. **Scrapper Issues**
   - Internet connection may affect external site access
   - Some websites may block automated requests
   - Consider adding delays between requests

### Support

For issues or questions:
- Check the project documentation
- Verify endpoint responses and status codes
- Review error messages for specific details
- Test individual endpoints separately

## License

This project is open-source. Feel free to contribute and improve the platform!

## Future Enhancements

Potential future improvements include:
- Machine learning model improvements for better matching
- Natural language generation for profile optimization
- Advanced filtering and recommendation systems
- Mobile app development
- Integration with university systems
- Automated deadline reminders

---

*Created with ❤️ for students seeking educational opportunities*