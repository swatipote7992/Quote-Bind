-- Seed sample applicants.
-- id is SERIAL (auto-assigned); applicant_ref_id is a separate business
-- reference number supplied here, not the primary key.

INSERT INTO applicant (applicant_ref_id, first_name, last_name, email, phone, dob) VALUES
(1001, 'John', 'Smith', 'john.smith@example.com', '7700900123', '1990-03-22'),
(1002, 'Emily', 'Clark', 'emily.clark@example.com', '7700900456', '1985-11-02'),
(1003, 'Test', 'User', 'test.user@example.com', '7700900789', '1995-07-15'),
(1004, 'Michael', 'Brown', 'michael.brown@example.com', '7700900111', '1988-01-19'),
(1005, 'Sarah', 'Davis', 'sarah.davis@example.com', '7700900222', '1992-06-30'),
(1006, 'David', 'Wilson', 'david.wilson@example.com', '7700900333', '1979-12-05'),
(1007, 'Laura', 'Taylor', 'laura.taylor@example.com', '7700900444', '1997-09-11'),
(1008, 'James', 'Anderson', 'james.anderson@example.com', '7700900555', '1983-04-27'),
(1009, 'Sophie', 'Thomas', 'sophie.thomas@example.com', '7700900666', '2000-02-14'),
(1010, 'Daniel', 'Moore', 'daniel.moore@example.com', '7700900777', '1991-10-08');
