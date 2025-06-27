# 🏨 Hotel Management System – Multi-Class Scheduling
## 🔍 Overview
This Hotel Management System is a Python-based desktop application that allows hotels to manage service requests across multiple room classes using classical CPU scheduling algorithms. The interface supports adding, tracking, and completing service requests for VIP, Mid-Range, and Economy classes, each with its service priorities.

The system is designed to simulate real-time scheduling and task management in a hotel environment, helping staff prioritize services efficiently.

## ⚙️ Key Technologies & Concepts
- Python (GUI framework like Tkinter/PyQt)
- Object-Oriented Programming
- CPU Scheduling Algorithms (Priority, Round Robin , FCFS , SJF)
- Multi-Class Service Simulation
- Dynamic Queues and Progress Tracking

## ✨ Features
**📝 Create New Service Request**
Input fields for Room Class, Room Number, Service Type, Estimated Time, and Description

**Calculates service charge dynamically**

**Manual or quick-add buttons to add service requests to the queue**

## ⚡ Quick Add by Class
- **One-click service request buttons for each room class:**

- **Economy: Housekeeping, Room Service**

- **Mid-Range: Premium Clean, Premium Service**

- **VIP: Butler Service, Concierge**

## 🧠 Multi-Class Scheduling Control
- Choose a scheduling algorithm (e.g., Priority)
- Set Time Quantum for Round Robin scheduling
- Start, Stop, or Clear the service queue
- Color-coded service levels:

🟢 Economy – Regular Priority

🟡 Mid-Range – Standard Priority

🔴 VIP – Immediate Priority

### Here is the picture of what I made

![image](https://github.com/user-attachments/assets/b79e6f40-a9e8-4703-b1f2-01bb4d02d68e)


## 📊 Real-Time Service Queue
Displays all pending services with the following details:

Class, Room, Service Type

Priority Level

Estimated Time

Service Charge

Description

## 🔄 Service Execution and Status
- Shows current running service
- Displays room, class, staff member (if assigned), and charge
- Real-time progress tracking
- Service statistics panel

## ✅ Completed Services
- Once a service is completed, it's logged with:
- Room Class, Number, Service Type
- Staff, Actual Time, Final Charge, Status

## 🧠 Algorithms Implemented
Priority Scheduling
Round Robin (with configurable time quantum)
FCFS
SJF


## 🚀 Future Enhancements
Staff assignment and login system
Add database (e.g., SQLite) for persistent records
Generate performance reports using matplotlib
Export completed service data to CSV
Add speech or notification alerts for service status
