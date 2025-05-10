# TrashTech Dashboard

A real-time monitoring dashboard for smart trash cans, built with Flask and Material Dashboard.

## Features

- **Real-time Monitoring**
  - Toxic Alert System
  - Fill Level Tracking
  - Waste Classification
  - Network Status

- **Waste Categories**
  - Biodegradable
  - Non-Biodegradable
  - Recyclable

- **Visual Analytics**
  - Fill Level Bar Charts
  - Classification Distribution Pie Charts
  - Real-time Updates

## Tech Stack

- **Backend**
  - Flask (Python)
  - SQLAlchemy
  - Flask-Login

- **Frontend**
  - Material Dashboard
  - Bootstrap 5
  - ApexCharts
  - Vite

## Project Structure
```
flask-material-dashboard/
├── frontend/        # Frontend files
│   ├── static/     # Static files (CSS, JS, images)
│   ├── templates/  # HTML templates
│   │   ├── includes/    # Reusable components
│   │   ├── layouts/     # Base templates
│   │   └── pages/       # Page templates
│   ├── package.json     # Node.js dependencies
│   └── vite.config.js   # Vite configuration
├── home/            # Backend routes
├── env/             # Python virtual environment
└── app.py          # Main Flask application
```

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/KingsleyNathan/trashtech-dashboard.git
cd trashtech-dashboard
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv env

# Activate virtual environment
# On Windows:
.\env\Scripts\activate
# On Unix or MacOS:
source env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```
The application will be available at `http://localhost:5000`

## Development

### Frontend Development
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

### Backend Development
- The Flask application uses blueprints for route organization
- Main routes are in `home/routes.py`
- Templates are in the `frontend/templates` directory

## Features in Detail

### Toxic Alert System
- Monitors and alerts for toxic conditions
- Real-time status updates
- Visual indicators for alert levels

### Fill Level Monitoring
- Tracks fill levels for different waste categories
- Visual representation through bar charts
- Percentage-based monitoring

### Waste Classification
- Real-time waste type detection
- Classification distribution visualization
- Historical data tracking

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contact

Kingsley Nathan - [@KingsleyNathan](https://github.com/KingsleyNathan)

Project Link: [https://github.com/KingsleyNathan/trashtech-dashboard](https://github.com/KingsleyNathan/trashtech-dashboard)
