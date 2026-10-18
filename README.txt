FloodGuard PH 🌧️
Flood Monitoring and Disaster Risk Reduction Dashboard

FloodGuard PH is a web-based flood monitoring and disaster risk reduction (DRRM) project built with Python, Flask, SQLAlchemy, and SQLite. It provides a simple dashboard for monitoring simulated rainfall and water-level readings, viewing flood risk levels, finding evacuation centers, and broadcasting alerts.

This project is intended for educational use and demonstration. Its sensor readings and risk thresholds are simulations, not official emergency warnings.

Features

- Resident Dashboard — View flood risk levels, sensor readings, evacuation centers, and recent alerts.
- Admin Dashboard — View regional statistics, sensor information, and risk summaries.
- Sensor Simulation — Submit simulated rainfall or water-level readings.
- Automatic Risk Recalculation — Update a region's risk level based on its sensor readings.
- Broadcast Alerts — Create and save alerts for a selected region.
- SQLite Database — Store regions, sensors, sensor logs, evacuation centers, and alerts.
- Seed Data — Initialize the application with sample records for demonstration.

 Technology Stack

- Python
- Flask
- Flask-SQLAlchemy
- SQLAlchemy
- SQLite
- HTML and CSS
- Bootstrap, if included by the templates
- Flask-WTF for CSRF protection, if enabled in the application

 Prerequisites

Install the following before running the application:

1. Python 3.10 or newer — use a version compatible with the dependencies in `requirements.txt`.
2. Git — to clone the repository.
3. A modern web browser.

SQLite is included with most standard Python installations, so a separate SQLite installation is usually unnecessary.

 Installation and Setup

1. Clone the repository

Replace `YOUR-GITHUB-USERNAME` with your GitHub username or the repository owner's username.

git clone https://github.com/YOUR-GITHUB-USERNAME/FloodGuard-PH.git
cd FloodGuard-PH

Alternatively, download the repository as a ZIP file from GitHub and extract it.

2. Create a virtual environment

Windows — Command Prompt or PowerShell

python -m venv .venv
.venv\Scripts\activate

If `python` is not recognized, try using `py` instead.

macOS or Linux

python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies

With the virtual environment activated, run:

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

If installation fails, check your Python version and the error message before changing package versions.

4. Configure the application

If the application reads `SECRET_KEY` from an environment variable, set a unique secret for your local environment.

Windows PowerShell

$env:SECRET_KEY = "replace-with-a-random-local-secret"

macOS or Linux

export SECRET_KEY="replace-with-a-random-local-secret"

Use a different, securely generated secret for each deployment. Never commit real secrets to GitHub.

If the application currently uses a development fallback secret, replace it with an environment-based configuration before deployment.

5. Run the application

Start the Flask application from the project directory:

in terminal type: 
python app.py

If your entry point uses the standard Flask development server, the terminal will display a local address, usually:

`http://127.0.0.1:5000`

Open that address in your browser.

To stop the application, press `Ctrl+C` in the terminal.

 How to Use FloodGuard PH

Resident Dashboard

1. Open the application in your browser.
2. View the available regions or zones.
3. Select a region to see its risk level and sensor readings.
4. Review the listed evacuation centers.
5. Read the latest broadcast alerts.

Admin Dashboard

1. Open the admin dashboard using the application's navigation.
2. Review the regional statistics and sensor summaries.
3. Select a region and sensor in the simulation form.
4. Enter a valid, non-negative sensor reading.
5. Submit the form and check the updated sensor value and regional risk level.
6. Use the broadcast alert form to select a region, choose an alert level, and enter a message.
7. Confirm that the saved alert appears in the dashboard.

> Important: If administrator authentication has not been implemented, the admin dashboard is not access-controlled. Do not expose it to the public internet.

 Risk Classification

The application uses simulated thresholds to demonstrate risk classification.

The monitoring system categorizes sensor thresholds into four color-coded levels green, yellow, orange, and red—based on rainfall and water level measurements. For rainfall, a green status indicates readings below 10, yellow covers 10 to below 25, orange ranges from 25 to below 40, and red signifies 40 or above. Similarly, water level readings are categorized with green for values below 0.8, yellow for 0.8 to below 1.5, orange for 1.5 to below 2.2, and red for 2.2 or higher.

Rainfall and water-level readings use the units defined by the application. Confirm those units in the code and interface before interpreting the values.

The region's calculated risk is based on the highest risk classification among its sensors.

These thresholds are illustrative only. They must not be used to make real evacuation or emergency decisions.

 Database

FloodGuard PH uses SQLite to store application data. On startup, the application should initialize its database and create the tables and sample records when database initialization and seeding are enabled.

The database may contain tables for:

- Regions
- Evacuation centers
- Sensors
- Sensor logs
- Broadcast alerts

The actual database filename and location are determined by the application's configuration.

If you change database models after creating a database, the existing SQLite file may not automatically acquire the new schema. Back up your data before resetting the database or applying schema changes.

 Project Structure

The project should follow a structure similar to this:

FloodGuard-PH/
├── app.py
├── models.py
├── database.py
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── user_dashboard.html
│   └── admin_dashboard.html
└── static/
    └── style.css


The SQLite database file may be generated when the application initializes. Do not commit a database containing private, sensitive, or real-world personal data.

 Troubleshooting

`ModuleNotFoundError`

Make sure the virtual environment is activated and the dependencies are installed:

python -m pip install -r requirements.txt

`no such table`

Check that the database initialization function runs before database queries and that the configured database path is correct.

The dashboard does not show sample data

Confirm that database seeding is enabled and that the application has successfully initialized the database. If the database already exists, its existing records may be retained instead of being replaced by seed data.

The browser cannot connect

Confirm that `python app.py` is still running and that you are opening the exact local address printed in the terminal.

A form submission returns a CSRF error

If CSRF protection is enabled, ensure that the form includes the required CSRF token and that browser cookies and sessions are working.

Changes to the code do not appear

Refresh the browser. If necessary, stop and restart the development server. Avoid using Flask debug mode on a publicly accessible server.

 Security and Limitations

- This project is intended for local development, classroom demonstrations, and further development.
- Administrator authentication and authorization must be implemented before public deployment.
- CSRF protection does not replace authentication or authorization.
- Use a secure production secret key and disable debug mode in production.
- Validate sensor readings and form inputs.
- Do not store real personal data or confidential information in a public repository.
- Sensor data and risk levels are simulated and are not official emergency information.
- This project is not a substitute for official government advisories, professional flood forecasting, or emergency services.

 Contributing

Contributions and suggestions are welcome.
1. Fork the repository.
2. Create a branch for your changes.
3. Make and test your changes.
4. Submit a pull request describing the improvements.

 Acknowledgment

FloodGuard PH was developed as an educational project focused on flood monitoring, community preparedness, and disaster risk reduction and management.
