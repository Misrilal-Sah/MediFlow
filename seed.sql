-- Seed file: truncate all tables and insert dummy data
-- Run with:  mysql -u root -p hospital_management < seed.sql

USE hospital_management;

-- Disable FK checks so truncation order doesn't matter
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE appointments;
TRUNCATE TABLE patients;
TRUNCATE TABLE doctors;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

-- ──────────────────────────────────────────────
-- Users (staff accounts) — 5 records
-- All accounts use password: Password@123
-- ──────────────────────────────────────────────
INSERT INTO users (first_name, last_name, email, phone, password_hash, email_verified) VALUES
('Admin',   'User',    'admin@mediflow.com',   '+1-800-000-0001', '$2b$12$V0ajBzoI7BAfmP5S3oofu.9XdKQgH4brHDodR1aesatWA4l3Qmawy', 1),
('Sarah',   'Johnson', 'sarah@mediflow.com',   '+1-800-000-0002', '$2b$12$V0ajBzoI7BAfmP5S3oofu.9XdKQgH4brHDodR1aesatWA4l3Qmawy', 1),
('Michael', 'Brown',   'michael@mediflow.com', '+1-800-000-0003', '$2b$12$V0ajBzoI7BAfmP5S3oofu.9XdKQgH4brHDodR1aesatWA4l3Qmawy', 1),
('Emily',   'Davis',   'emily@mediflow.com',   '+1-800-000-0004', '$2b$12$V0ajBzoI7BAfmP5S3oofu.9XdKQgH4brHDodR1aesatWA4l3Qmawy', 1),
('James',   'Wilson',  'james@mediflow.com',   '+1-800-000-0005', '$2b$12$V0ajBzoI7BAfmP5S3oofu.9XdKQgH4brHDodR1aesatWA4l3Qmawy', 1);

-- ──────────────────────────────────────────────
-- Doctors — 35 records
-- ──────────────────────────────────────────────
INSERT INTO doctors (name, specialty, available_days, phone) VALUES
('Dr. Alice Morgan',     'Cardiology',           'Monday,Wednesday,Friday',         '+1-555-101-0001'),
('Dr. Robert Patel',     'Neurology',            'Tuesday,Thursday',                '+1-555-101-0002'),
('Dr. Susan Lee',        'Orthopedics',          'Monday,Tuesday,Wednesday',        '+1-555-101-0003'),
('Dr. David Kim',        'Pediatrics',           'Monday,Wednesday,Friday',         '+1-555-101-0004'),
('Dr. Karen White',      'Dermatology',          'Tuesday,Thursday,Saturday',       '+1-555-101-0005'),
('Dr. James Taylor',     'Oncology',             'Monday,Thursday',                 '+1-555-101-0006'),
('Dr. Linda Harris',     'Gynecology',           'Wednesday,Friday,Saturday',       '+1-555-101-0007'),
('Dr. Mark Thompson',    'Urology',              'Monday,Tuesday,Friday',           '+1-555-101-0008'),
('Dr. Nancy Clark',      'Endocrinology',        'Tuesday,Wednesday,Thursday',      '+1-555-101-0009'),
('Dr. Paul Walker',      'Gastroenterology',     'Monday,Wednesday',                '+1-555-101-0010'),
('Dr. Rachel Scott',     'Pulmonology',          'Tuesday,Thursday,Friday',         '+1-555-101-0011'),
('Dr. Steven Young',     'Nephrology',           'Monday,Tuesday,Wednesday',        '+1-555-101-0012'),
('Dr. Patricia Hall',    'Ophthalmology',        'Wednesday,Thursday,Saturday',     '+1-555-101-0013'),
('Dr. Brian Adams',      'Psychiatry',           'Monday,Friday',                   '+1-555-101-0014'),
('Dr. Sandra Nelson',    'Rheumatology',         'Tuesday,Thursday',                '+1-555-101-0015'),
('Dr. Christopher Baker','Emergency Medicine',   'Monday,Tuesday,Wednesday,Thursday,Friday', '+1-555-101-0016'),
('Dr. Ashley Carter',    'General Surgery',      'Monday,Wednesday,Friday',         '+1-555-101-0017'),
('Dr. Kevin Mitchell',   'Radiology',            'Tuesday,Thursday',                '+1-555-101-0018'),
('Dr. Megan Perez',      'Anesthesiology',       'Monday,Tuesday,Friday',           '+1-555-101-0019'),
('Dr. Jason Roberts',    'Hematology',           'Wednesday,Thursday,Saturday',     '+1-555-101-0020'),
('Dr. Stephanie Turner', 'Infectious Disease',   'Tuesday,Friday',                  '+1-555-101-0021'),
('Dr. Justin Phillips',  'Allergy & Immunology', 'Monday,Wednesday,Thursday',       '+1-555-101-0022'),
('Dr. Amber Campbell',   'Family Medicine',      'Monday,Tuesday,Wednesday,Friday', '+1-555-101-0023'),
('Dr. Ryan Parker',      'Sports Medicine',      'Tuesday,Thursday,Saturday',       '+1-555-101-0024'),
('Dr. Melissa Evans',    'Geriatrics',           'Monday,Wednesday,Friday',         '+1-555-101-0025'),
('Dr. Eric Edwards',     'Plastic Surgery',      'Tuesday,Thursday',                '+1-555-101-0026'),
('Dr. Jessica Collins',  'Neonatology',          'Monday,Tuesday,Thursday',         '+1-555-101-0027'),
('Dr. Andrew Stewart',   'Vascular Surgery',     'Wednesday,Friday,Saturday',       '+1-555-101-0028'),
('Dr. Heather Morris',   'Palliative Care',      'Monday,Friday',                   '+1-555-101-0029'),
('Dr. Timothy Rogers',   'Internal Medicine',    'Monday,Tuesday,Wednesday,Thursday','+ 1-555-101-0030'),
('Dr. Diane Reed',       'Dental Surgery',       'Tuesday,Thursday,Saturday',       '+1-555-101-0031'),
('Dr. Gregory Cook',     'Toxicology',           'Monday,Wednesday',                '+1-555-101-0032'),
('Dr. Carolyn Morgan',   'Physical Medicine',    'Tuesday,Thursday,Friday',         '+1-555-101-0033'),
('Dr. Frank Bailey',     'Trauma Surgery',       'Monday,Tuesday,Friday',           '+1-555-101-0034'),
('Dr. Angela Rivera',    'Microbiology',         'Wednesday,Thursday',              '+1-555-101-0035');

-- ──────────────────────────────────────────────
-- Patients — 40 records
-- ──────────────────────────────────────────────
INSERT INTO patients (name, age, gender, phone) VALUES
('John Smith',         34, 'Male',   '+1-555-200-0001'),
('Mary Johnson',       28, 'Female', '+1-555-200-0002'),
('William Brown',      52, 'Male',   '+1-555-200-0003'),
('Jennifer Davis',     45, 'Female', '+1-555-200-0004'),
('Charles Miller',     61, 'Male',   '+1-555-200-0005'),
('Linda Wilson',       39, 'Female', '+1-555-200-0006'),
('Richard Moore',      47, 'Male',   '+1-555-200-0007'),
('Barbara Taylor',     55, 'Female', '+1-555-200-0008'),
('Joseph Anderson',    22, 'Male',   '+1-555-200-0009'),
('Patricia Thomas',    68, 'Female', '+1-555-200-0010'),
('Thomas Jackson',     73, 'Male',   '+1-555-200-0011'),
('Susan White',        31, 'Female', '+1-555-200-0012'),
('Christopher Harris', 44, 'Male',   '+1-555-200-0013'),
('Jessica Martin',     27, 'Female', '+1-555-200-0014'),
('Daniel Garcia',      58, 'Male',   '+1-555-200-0015'),
('Sarah Martinez',     36, 'Female', '+1-555-200-0016'),
('Matthew Robinson',   19, 'Male',   '+1-555-200-0017'),
('Karen Clark',        49, 'Female', '+1-555-200-0018'),
('Anthony Rodriguez',  63, 'Male',   '+1-555-200-0019'),
('Lisa Lewis',         42, 'Female', '+1-555-200-0020'),
('Mark Lee',           56, 'Male',   '+1-555-200-0021'),
('Betty Walker',       71, 'Female', '+1-555-200-0022'),
('Donald Hall',        38, 'Male',   '+1-555-200-0023'),
('Margaret Allen',     25, 'Female', '+1-555-200-0024'),
('Paul Young',         67, 'Male',   '+1-555-200-0025'),
('Dorothy Hernandez',  53, 'Female', '+1-555-200-0026'),
('Steven King',        41, 'Male',   '+1-555-200-0027'),
('Helen Wright',       30, 'Female', '+1-555-200-0028'),
('Kenneth Lopez',      76, 'Male',   '+1-555-200-0029'),
('Sandra Hill',        48, 'Female', '+1-555-200-0030'),
('George Scott',       60, 'Male',   '+1-555-200-0031'),
('Donna Green',        35, 'Female', '+1-555-200-0032'),
('Edward Adams',       23, 'Male',   '+1-555-200-0033'),
('Carol Baker',        57, 'Female', '+1-555-200-0034'),
('Ronald Gonzalez',    69, 'Male',   '+1-555-200-0035'),
('Ruth Nelson',        44, 'Female', '+1-555-200-0036'),
('Brian Carter',       50, 'Male',   '+1-555-200-0037'),
('Sharon Mitchell',    33, 'Female', '+1-555-200-0038'),
('Kevin Perez',        77, 'Male',   '+1-555-200-0039'),
('Michelle Roberts',   29, 'Female', '+1-555-200-0040');

-- ──────────────────────────────────────────────
-- Appointments — 40 records
-- ──────────────────────────────────────────────
INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, status, symptoms) VALUES
(1,  1,  '2026-04-01', '09:00:00', 'Scheduled',  'Chest pain and shortness of breath'),
(2,  4,  '2026-04-01', '09:30:00', 'Scheduled',  'Child routine checkup'),
(3,  2,  '2026-04-01', '10:00:00', 'Completed',  'Persistent headaches and dizziness'),
(4,  7,  '2026-04-01', '10:30:00', 'Scheduled',  'Regular gynecology follow-up'),
(5,  1,  '2026-04-02', '08:00:00', 'Scheduled',  'Palpitations after exercise'),
(6,  5,  '2026-04-02', '09:00:00', 'Completed',  'Skin rash on arms'),
(7,  3,  '2026-04-02', '10:00:00', 'Scheduled',  'Knee pain after jogging'),
(8,  9,  '2026-04-02', '11:00:00', 'Cancelled',  'High blood sugar levels'),
(9,  4,  '2026-04-03', '09:00:00', 'Scheduled',  'Fever and cold for 3 days'),
(10, 10, '2026-04-03', '09:30:00', 'Completed',  'Stomach cramps and bloating'),
(11, 2,  '2026-04-03', '10:00:00', 'Completed',  'Memory lapses and confusion'),
(12, 6,  '2026-04-03', '11:00:00', 'Scheduled',  'Follow-up after chemotherapy'),
(13, 8,  '2026-04-04', '08:30:00', 'Scheduled',  'Difficulty urinating'),
(14, 7,  '2026-04-04', '09:00:00', 'Scheduled',  'Irregular menstrual cycle'),
(15, 11, '2026-04-04', '10:00:00', 'Completed',  'Chronic cough and wheezing'),
(16, 14, '2026-04-04', '11:00:00', 'Scheduled',  'Anxiety and sleep disturbance'),
(17, 4,  '2026-04-05', '09:00:00', 'Scheduled',  'Vaccination and growth check'),
(18, 9,  '2026-04-05', '09:30:00', 'Completed',  'Thyroid function review'),
(19, 12, '2026-04-05', '10:00:00', 'Cancelled',  'Swollen legs and fatigue'),
(20, 5,  '2026-04-05', '10:30:00', 'Scheduled',  'Eczema flare-up'),
(21, 3,  '2026-04-07', '08:00:00', 'Scheduled',  'Lower back pain'),
(22, 13, '2026-04-07', '09:00:00', 'Completed',  'Blurry vision in right eye'),
(23, 17, '2026-04-07', '10:00:00', 'Scheduled',  'Appendix pain evaluation'),
(24, 14, '2026-04-07', '11:00:00', 'Scheduled',  'Depression follow-up'),
(25, 2,  '2026-04-08', '09:00:00', 'Completed',  'Seizure management review'),
(26, 10, '2026-04-08', '09:30:00', 'Scheduled',  'Acid reflux symptoms'),
(27, 1,  '2026-04-08', '10:00:00', 'Scheduled',  'Blood pressure check'),
(28, 5,  '2026-04-08', '10:30:00', 'Cancelled',  'Allergic reaction to medication'),
(29, 15, '2026-04-09', '08:00:00', 'Completed',  'Joint inflammation review'),
(30, 23, '2026-04-09', '09:00:00', 'Scheduled',  'Annual physical checkup'),
(31, 16, '2026-04-09', '10:00:00', 'Scheduled',  'Chest injury assessment'),
(32, 4,  '2026-04-10', '09:00:00', 'Scheduled',  'Infant feeding issues'),
(33, 8,  '2026-04-10', '09:30:00', 'Completed',  'Prostate screening'),
(34, 7,  '2026-04-10', '10:00:00', 'Scheduled',  'Prenatal visit'),
(35, 11, '2026-04-11', '08:30:00', 'Completed',  'Asthma medication review'),
(36, 25, '2026-04-11', '09:00:00', 'Scheduled',  'Elderly care assessment'),
(37, 6,  '2026-04-11', '10:00:00', 'Scheduled',  'Cancer screening'),
(38, 3,  '2026-04-12', '09:00:00', 'Cancelled',  'Hip replacement follow-up'),
(39, 20, '2026-04-12', '10:00:00', 'Scheduled',  'Low platelet count'),
(40, 22, '2026-04-12', '11:00:00', 'Completed',  'Diabetic retinopathy checkup');
