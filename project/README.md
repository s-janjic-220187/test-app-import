# Test Load App

A modern Flask web application for importing, viewing, and managing test user data from XML files. Designed for both desktop and mobile browsers with a responsive, engaging UI.

## Features
- **Landing Page:** Welcoming home page with modern design.
- **User Table:** View and sort users from either the `user` or `test_user` tables.
- **Import Users:** Dedicated page with documentation and example XML format. Import users from an XML file into the `test_user` table.
- **Responsive Design:** Works well on both web and Android/mobile browsers.
- **Modern UI:** Uses Bootstrap and custom CSS for a clean, attractive look.

## Usage
1. **Home:** Visit `/` to see the landing page.
2. **User Management:** Go to `/users` to view and sort user data. Use the sidebar to switch between tables.
3. **Import Users:** Click "Import Users" in the sidebar or visit `/import` for documentation and to upload your XML file.

## XML Import Format Example
```
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
├── /templates
│     ├── landing.html
│     ├── users.html
│     └── import.html
├── /static
│     └── style.css
├── /db_data
│     └── ...
└── ...
```

## Requirements
- Python 3.x
- Flask
- mysql-connector-python
- MariaDB or MySQL server

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

---

**Enjoy managing your test user data!**
