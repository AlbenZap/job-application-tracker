# Job Application Tracker

A web app to track job applications with status management, analytics, and history tracking. Built with Streamlit and Supabase.

## Features

- Track applications with multiple statuses (Saved, Applied, Interview, Offer, Rejected)
- Status history
- Dashboard with analytics and insights
- CSV export
- User authentication

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Supabase (PostgreSQL)
- **Libraries**: pandas, streamlit, supabase, plotly

## Quick Start

### Prerequisites

- Docker or Python 3.8+
- Supabase account

### Setup

1. Clone the repository
   ```bash
   git clone https://github.com/AlbenZap/job-application-tracker.git
   cd job-application-tracker
   ```

2. Set up Supabase
   - Create a project at [supabase.com](https://supabase.com)
   - Run the SQL from `database_setup.sql` in the SQL Editor
   - Get your project URL and anon key from Settings > API

3. Configure secrets
   
   Create `.streamlit/secrets.toml`:
   ```toml
   [supabase]
   url = "your-supabase-url"
   key = "your-supabase-key"
   ```

4. Run the app

   **With Docker:**
   ```bash
   docker compose up --build
   ```

   **Without Docker:**
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

See `setup_database.sql` for complete schema.
## Project Structure

```
├── app.py                      # Main entry point
├── pages/                      # Streamlit pages
│   ├── dashboard.py
│   ├── add_application.py
│   ├── view_applications.py
│   ├── login.py
│   └── signup.py
├── utils/                      # Utilities
│   ├── database.py             # Database operations
│   ├── auth.py                 # Authentication
│   ├── constants.py            # App constants
│   ├── logger_config.py        # Logging setup
│   └── company_api.py          # Company data API
├── database_setup.sql          # Database schema
├── docker-compose.yml          # Docker configuration
├── Dockerfile                  # Docker image
└── requirements.txt            # Dependencies
```

## Usage

### Pages

- **Dashboard** - Overview and analytics
- **Add Application** - Create new applications
- **View Applications** - Filter and export data, and view all status changes

### Configuration

Edit `utils/constants.py` to customize:
- Valid status values
- Job types
- Default company logo

## License

MIT License

---

Built for job seekers to stay organized during the job search process.