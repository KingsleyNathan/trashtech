# TrashTech Flask Material Dashboard

A web dashboard for real-time monitoring of smart trash can sensors, built with Flask and Material Dashboard.

## Features
- Live monitoring of trash fill levels, toxicity, and classification status
- Real-time charts for trash counts and classification distribution
- Latest detection and update cards
- Auto-refresh for sensor data and dashboard cards
- MySQL database integration

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd flask-material-dashboard
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure the database
- Ensure you have a MySQL server running.
- Create a database (e.g., `trashtechdb`) and update your connection settings in `backend/routes/connection.py`.
- The `trash` table should have at least: `id`, `category`, `timestamp` columns.

### 4. Run the Flask app
```bash
flask run
```
Or:
```bash
python app.py
```

### 5. Access the dashboard
Open your browser and go to: [http://localhost:5000](http://localhost:5000)

## Dashboard Overview
- **Toxic Alert:** Shows current status for Biodegradable bin.
- **Fill Levels:** Shows fill percentage for Non-Biodegradable and Recyclable bins.
- **Latest Classification:** Shows the most recent trash detection and timestamp.
- **Detected Update for Sensors:** Shows the latest update timestamp for all sensors (auto-refreshes every 1 minute).
- **Charts:**
  - Bar chart for overall trash counts (Recyclable, Biodegradable, Non-Biodegradable)
  - Pie chart for classification distribution

## Auto-Refresh
- The "Detected Update for Sensors" card auto-refreshes every 1 minute.
- Charts and other dashboard data auto-refresh every 5 minutes.

## Troubleshooting
- **Database connection errors:** Check your MySQL credentials and that the server is running.
- **No data showing:** Ensure your `trash` table has data and category names match exactly: `Recyclable`, `Biodegradable`, `Non-Biodegradable`.
- **Frontend not updating:** Open the browser console (F12) to check for JavaScript errors or failed API requests.
- **Backend logs:** Check your terminal for Flask server output and errors.

## Customization
- To change refresh intervals, edit the JavaScript in `frontend/templates/pages/index.html`.
- To add more features or cards, edit the HTML and backend routes as needed.

## License
MIT

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
