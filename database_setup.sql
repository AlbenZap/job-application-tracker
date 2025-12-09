-- SQL Script for Job Tracker Database

-- Drop existing tables
DROP TABLE IF EXISTS status_history;
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS users;

-- Create tables

-- Table: users
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(60) NOT NULL
);

-- Table: companies
CREATE TABLE IF NOT EXISTS companies (
    company_id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    industry VARCHAR(100),
    location VARCHAR(100),
    logo_url VARCHAR(500) DEFAULT 'https://storage.googleapis.com/simplify-imgs/company/default/logo.png'
);

-- Table: jobs
CREATE TABLE IF NOT EXISTS jobs (
    job_id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE ON UPDATE CASCADE,
    title VARCHAR(150) NOT NULL,
    job_type VARCHAR(20) CHECK (job_type IN ('Full-time', 'Part-time', 'Internship', 'Contract', 'Other')),
    location VARCHAR(100),
    posted_date DATE,
    UNIQUE(company_id, title)
);

-- Table: applications
CREATE TABLE IF NOT EXISTS applications (
    application_id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE ON UPDATE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    status_changed_date DATE NOT NULL,
    current_status VARCHAR(20) NOT NULL CHECK (current_status IN ('Saved', 'Applied', 'Interview', 'Offer', 'Rejected')),
    notes TEXT
);

-- Table: status_history
CREATE TABLE IF NOT EXISTS status_history (
    history_id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE ON UPDATE CASCADE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('Saved', 'Applied', 'Interview', 'Offer', 'Rejected')),
    status_date DATE NOT NULL,
    notes TEXT
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_applications_user_id ON applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_job_id ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(current_status);
CREATE INDEX IF NOT EXISTS idx_applications_date ON applications(status_changed_date);
CREATE INDEX IF NOT EXISTS idx_status_history_app_id ON status_history(application_id);
CREATE INDEX IF NOT EXISTS idx_status_history_date ON status_history(status_date);


-- Insert sample users
INSERT INTO users (name, email, password_hash)
VALUES
    ('Alice Johnson', 'alice@example.com', 'hashed_password_1'),
    ('Bob Smith', 'bob@example.com', 'hashed_password_2');

-- Insert sample companies
INSERT INTO companies (name, industry, location, logo_url)
VALUES
    ('TechCorp', 'Technology', 'San Francisco, CA', 'https://example.com/logo1.png'),
    ('HealthInc', 'Healthcare', 'New York, NY', 'https://example.com/logo2.png');

-- Insert sample jobs
INSERT INTO jobs (company_id, title, job_type, location, posted_date)
VALUES
    (1, 'Software Engineer', 'Full-time', 'Remote', '2025-10-15'),
    (2, 'Data Analyst', 'Part-time', 'New York, NY', '2025-10-20');

-- Insert sample applications
INSERT INTO applications (job_id, user_id, status_changed_date, current_status, notes)
VALUES
    (1, 1, '2025-11-01', 'Applied', 'Looking forward to this opportunity'),
    (2, 2, '2025-11-02', 'Applied', 'Excited to join the team');

-- Insert sample status history
INSERT INTO status_history (application_id, status, status_date, notes)
VALUES
    (1, 'Applied', '2025-11-01', 'Initial application submitted'),
    (2, 'Applied', '2025-11-02', 'Initial application submitted');

-- Update application status
UPDATE applications
SET current_status = 'Interview', status_changed_date = '2025-11-06'
WHERE application_id = 1;

-- Log status change
INSERT INTO status_history (application_id, status, status_date, notes)
VALUES (1, 'Interview', '2025-11-06', 'Phone interview scheduled');

-- Delete operations (CASCADE automatically deletes child records)
-- Deleting a user removes all their applications and related status history
DELETE FROM users WHERE user_id = 2;

-- Deleting a company removes all its jobs, applications, and status history
DELETE FROM companies WHERE company_id = 2;