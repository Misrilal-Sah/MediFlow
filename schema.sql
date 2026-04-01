-- Hospital Management System – Database Schema
-- Run this once to set up the database:
--   mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS hospital_management
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE hospital_management;

-- ──────────────────────────────────────────────
-- Users (admin / staff accounts)
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INT          AUTO_INCREMENT PRIMARY KEY,
    first_name    VARCHAR(80)  NOT NULL,
    last_name     VARCHAR(80)  NOT NULL,
    email         VARCHAR(160) NOT NULL UNIQUE,
    phone         VARCHAR(20)  NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email_verified TINYINT(1)  NOT NULL DEFAULT 0,
    created_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- ──────────────────────────────────────────────
-- Doctors
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS doctors (
    id             INT          AUTO_INCREMENT PRIMARY KEY,
    name           VARCHAR(120) NOT NULL,
    specialty      VARCHAR(120) NOT NULL,
    available_days VARCHAR(120) NOT NULL,
    phone          VARCHAR(20)  NOT NULL,
    created_at     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- ──────────────────────────────────────────────
-- Patients
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS patients (
    id         INT          AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(120) NOT NULL,
    age        TINYINT UNSIGNED NOT NULL,
    gender     ENUM('Male','Female','Other') NOT NULL,
    phone      VARCHAR(20)  NOT NULL,
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- ──────────────────────────────────────────────
-- Appointments
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS appointments (
    id               INT     AUTO_INCREMENT PRIMARY KEY,
    patient_id       INT     NOT NULL,
    doctor_id        INT     NOT NULL,
    appointment_date DATE    NOT NULL,
    appointment_time TIME    NOT NULL,
    status           ENUM('Scheduled','Completed','Cancelled') DEFAULT 'Scheduled',
    symptoms         TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_apt_patient FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    CONSTRAINT fk_apt_doctor  FOREIGN KEY (doctor_id)  REFERENCES doctors(id)  ON DELETE CASCADE
);
