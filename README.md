# PrintReady
Overview
PrintReady is a hobby full-stack web application designed to significantly improve the efficiency and user experience of campus printing services. Developed to address the common problem of long and disorganized printing queues at a B.Tech campus store, PrintReady provides a seamless digital platform for students to manage their print jobs and for staff to oversee the entire printing workflow. By digitalizing the printing process, PrintReady reduces wait times, enhances transparency, and optimizes resource management within the campus printing environment.

Key Components
The application is built with distinct user interfaces and functionalities tailored for both students and staff:

Student Module
Description: This module provides the interface for students to interact with the printing service. It focuses on submission, tracking, and personal history.

Functionality: Students can securely log in, upload documents, specify print parameters (number of copies, print type like color/B&W), and view the current status of all their submitted jobs, from "Queued" to "Completed."

Staff Module
Description: This module serves as the administrative dashboard for printing store personnel. It provides comprehensive control over the print queue and job management.

Functionality: Staff members can log in to view all active print jobs, update the status of jobs (e.g., from "Queued" to "Processing" or "Completed"), mark jobs as finished, and view a history of recently completed tasks. This module also allows staff to access uploaded files for printing.

Application Workflow
User Registration & Login: New users (students or staff) can sign up, and existing users can log in using their credentials. The system distinguishes roles to direct users to appropriate dashboards.

Student Job Submission: Logged-in students navigate to their dashboard, where they can upload their document file, enter the desired number of copies, and select the print type. Upon submission, the job enters the "Queued" status.

Staff Job Management: Staff access their dashboard, which displays all pending print jobs. They can view job details, download the uploaded files, and update the status of a job as it progresses through the printing process. When a job is completed, staff mark it as "Completed," and the system records the completion timestamp and the staff member who completed it.

Status Tracking: Students can continuously monitor the status of their submitted jobs from their personal dashboard.

Features
Secure User Authentication (Student and Staff roles).

Role-based dashboards for tailored user experience.

Document upload functionality for students.

Print job parameter selection (copies, print type).

Real-time job status tracking for students.

Centralized print queue management for staff.

Ability for staff to update job statuses to "Completed".

Secure file access: Only the submitting user or staff can download an uploaded file.

Database initialization via Flask CLI command.

Technologies Used
Backend: Python, Flask, Flask-SQLAlchemy (for ORM), Flask-Login (for user session management), Werkzeug (for security utilities and file handling).

Database: SQLite (for development and local storage).

Frontend: HTML, CSS, JavaScript (for user interfaces and interactions).
