# Flask Trash Can Monitoring System

A web-based dashboard for real-time monitoring of trash can fill levels, toxicity, and classification status, with automated email alerts for critical events.

## Features
- Live dashboard for Recyclable, Non-Biodegradable, and Biodegradable bins
- Toxic alert status monitoring
- Automated email notifications for:
  - Toxic status: "ABOVE NORMAL" or "TOXIC"
  - Non-Biodegradable and Recyclable fill levels: 80%, 90%, 100%
- Duplicate prevention: Only one email per threshold until the value changes

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd flask-material-dashboard
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root with the following content:
```ini
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your.email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=your.email@gmail.com
ALERT_RECIPIENTS=recipient1@email.com,recipient2@email.com
```
- For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) (not your regular password).
- `ALERT_RECIPIENTS` is a comma-separated list of emails to receive alerts.

### 4. Set Up the Database
- Ensure your MySQL database is running and configured in `backend/config.py` or via environment variables.
- The `sensor` table should have columns: `sensor_id`, `reading_value`, `timestamp`.
- The `trash` table should have columns: `category`, `timestamp`.

### 5. Run the Application
```bash
flask run
```
Or, if you use a custom entry point:
```bash
python app.py
```

## Usage
- Access the dashboard at [http://localhost:5000](http://localhost:5000)
- The dashboard auto-refreshes and triggers email alerts based on:
  - Toxic status: "ABOVE NORMAL" or "TOXIC"
  - Non-Biodegradable/Recyclable fill levels: 80, 90, or 100 (as int or string, e.g., `80` or `"80%"`)
- Only one email is sent per threshold until the value changes.

## Customization
- To change alert thresholds or add more bins, edit the logic in `home/routes.py`.
- To customize email content, edit `home/utils/email_notifications.py`.

## Troubleshooting
- Check your Flask server logs for debug output and errors.
- Ensure your email credentials and recipients are correct in `.env`.
- For Gmail, ensure you are using an App Password and have enabled "Less secure app access" if needed.

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
