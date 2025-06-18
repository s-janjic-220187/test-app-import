CREATE TABLE IF NOT EXISTS test_user (
    id INT PRIMARY KEY,
    first_name VARCHAR(50),
    middle_name VARCHAR(50),
    last_name VARCHAR(50),
    date_of_birth DATE,
    created_on DATETIME,
    is_active TINYINT
);
