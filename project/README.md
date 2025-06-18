# Slava Pivcu app !

A modern Flask web application for importing, viewing, and managing user data and events (Rodjendani, slave i veselja) from XML files. Designed for both desktop and mobile browsers with a responsive, engaging UI.

## Features
- **Landing Page:** Welcoming home page with modern design and new app name.
- **User Table:** View and sort users from either the `user` or `test_user` tables.
- **Import Users:** Dedicated page with documentation and example XML format. Import users from an XML file into the `test_user` table.
- **Events Calendar:** View, add, edit, and delete events (Rodjendan, Slava, Veselje) in a stylish calendar. User birthdays are automatically synced as 'Rodjendan' events. Clicking a birthday event opens a modern modal with full user info and edit option.
- **Modern Date Picker:** User date of birth uses a modern Flatpickr date picker for a better experience.
- **Responsive Design:** Works well on both web and Android/mobile browsers.
- **Modern UI:** Uses Bootstrap, FullCalendar, Flatpickr, and custom CSS for a clean, attractive look.
- **Database Healthcheck:** Docker Compose healthcheck for MariaDB now uses the correct root user and password, preventing access denied warnings and ensuring reliable startup.
- **Favicon:** Added a favicon for browser tab icon. No more 404 errors for /favicon.ico.
- **FullCalendar CSS:** FullCalendar is now styled using a local CSS file, ensuring robust and consistent appearance without CDN or CORS issues.
- **User import draft:** Imported users are first loaded into a draft table (formerly `test_user`).
- **Edit draft users:** You can edit draft user records inline before migration.
- **Migrate to User Table:** Click the 'Migrate to User Table' button to move all draft users to the main User table (skipping existing IDs).

## Usage
1. **Home:** Visit `/` to see the landing page.
2. **User Management:** Go to `/users` to view and sort user data. Use the sidebar to switch between tables.
3. **Import Users:** Click "Import Users" in the sidebar or visit `/import` for documentation and to upload your XML file.
4. **Events Calendar:** Click "Rodjendani, slave i veselja" in the sidebar or visit `/events` to view and manage events. Click a date to add, or click an event to edit/delete. User birthdays are color-coded and editable via a modern modal.

## XML Import Format Example
```xml
<users>
    <user>
        <id>1</id>
        <first_name>John</first_name>
        <middle_name>A.</middle_name>
        <last_name>Doe</last_name>
        <date_of_birth>1990-01-01</date_of_birth>
        <created_on>2023-01-01T12:00:00</created_on>
        <is_active>1</is_active>
    </user>
    ...
</users>
```

## Project Structure
```
project/
├── app.py
├── importer.py
├── requirements.txt
├── Dockerfile
├── compose.yaml
├── /templates
│     ├── landing.html
│     ├── users.html
│     ├── import.html
│     ├── events.html
│     └── _user_modal.html
├── /static
│     ├── style.css
│     ├── fullcalendar.min.css
│     └── favicon.ico
├── /db_data
│     └── ...
└── ...
```

## Requirements
- Python 3.x
- Flask
- mysql-connector-python
- MariaDB or MySQL server
- Docker (for containerized deployment)

## Setup
1. Install dependencies:
   ```sh
   pip install flask mysql-connector-python
   ```
2. Configure your database credentials in `app.py`.
3. Run the app:
   ```sh
   python app.py
   ```
4. Open your browser to `http://localhost:5000/`.

## Docker/Compose Deployment
1. Build and start everything with:
   ```sh
   docker compose up --build
   ```
2. Your app will be available on port 5000, and MariaDB on 3306.

## 🚀 Deploying to Railway.com

1. **Push your code to GitHub.**
2. **Create a new Railway project** and link your GitHub repo.
3. **Set the Root Directory** to `project` in Railway settings.
4. **Add these environment variables** in Railway (from your DB connection info):
   - `MYSQL_HOST`
   - `MYSQL_PORT`
   - `MYSQL_USER`
   - `MYSQL_PASSWORD`
   - `MYSQL_DATABASE`
5. **Deploy!** Railway will build your Dockerfile, run migrations, and start the app.
6. Your app will be live at the Railway-provided URL.

**Tip:** If you change your database, update the environment variables accordingly.

## Database migrations
All required tables are created automatically on app startup using SQL scripts in the `migrations/` folder. You can also run them manually:

```sh
python migrations/migrate.py
```

---

**Enjoy managing your user data and events with Slava Pivcu app !**
