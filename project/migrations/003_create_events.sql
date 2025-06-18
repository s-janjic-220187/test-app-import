CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    event_type ENUM('Rodjendan', 'Slava', 'Veselje') NOT NULL,
    event_date DATE NOT NULL
);
