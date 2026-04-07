# 💬 Real-Time Chat Application using Django Channels

A full-featured **real-time chat application** built using **Django**, **Django Channels**, and **WebSockets**.
This application allows authenticated users to create chat rooms, join shared rooms, send real-time messages, share attachments, and track user presence live.

---

# 🚀 Project Overview

This is a **real-time chat application** built on **Django** and **Django Channels**.

Authenticated users can:

* Create chat rooms
* Join rooms via shared links
* Send messages in real-time
* Share files and images
* See typing indicators
* Track online users
* Receive read receipts

Real-time communication is handled using **WebSockets**, ensuring instant message delivery.

---

# 🛠️ Tech Stack

## Backend

* Django
* Django Channels
* SQLite
* Django Authentication System
* WebSockets

## Frontend

* HTML Templates
* Tailwind CSS
* JavaScript

---

## Channel Layer

This project uses:

* **InMemoryChannelLayer** for development
* WebSocket communication handled using Django Channels

Note:
For production deployment, Redis can be used as the channel layer.

---

# 🔐 Authentication Flow

* User Signup
* User Login
* User Logout
* Protected routes for authenticated users
* Redirect to `/rooms/` after successful login
* Only logged-in users can access chat rooms

---

# 🏠 Room Management

Users can:

* Create their own chat rooms
* Join rooms using shared links
* Leave joined rooms
* Delete rooms (only room creator)

### Default Rooms

These rooms are always available:

* **work**
* **tech**

Custom rooms are:

* Owned by creator
* Joinable by shared URL
* Removable by owner
* Leaveable by members

---

# 🔗 Join Through Shared Link

Users can join rooms by:

1. Copying the shared room link
2. Pasting it into the **Join Room Box**
3. Automatically becoming a room member

---

# ⚡ Real-Time Messaging

Real-time messaging is powered by:

* Django Channels
* WebSocket connections
* Room-based message broadcasting

### How it works:

1. WebSocket connection opens using room slug
2. Message sent from frontend
3. Consumer receives message
4. Message saved in database
5. Broadcasted to all connected users

Instant delivery across all connected users.

---

# 🟢 Presence System (Online Users)

Room-level presence tracking:

* User added when room opens
* User removed when disconnected
* Shows:

  * Online users list
  * Total online count

---

# ⌨️ Typing Indicator

Typing indicator shows:

* When a user starts typing
* Displays **"typing..."** message
* Uses debounce logic to avoid spam

---

# 👁️ Read Receipts

Message status includes:

* ✅ Sent (Gray double tick)
* 👀 Seen (Blue double tick)

Seen status updates automatically when another user views the message.

---

# 📎 Attachment Sharing

Users can share:

* Images
* Files

Features:

* Media saved to backend storage
* Images shown with preview
* Files shown as clickable links
* Attachments broadcast in real-time

---

# 🗄️ Database Design

Main Models:

## ChatRoom

Stores:

* Room name
* Slug
* Owner
* Members

## ChatMessage

Stores:

* Sender
* Room
* Message content
* Timestamp
* Seen status
* Optional attachment

## Django User

Handles:

* Authentication
* User identity

---

# 🔒 Security & Access Control

Security rules:

* Login required for room access
* Only owner can delete room
* Default rooms are protected
* Members can leave rooms
* Non-members cannot access rooms

---

# 📂 Project Structure

```
chatapp/
│
├── mysite/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│
├── chat/
│   ├── models.py
│   ├── views.py
│   ├── consumers.py
│   ├── routing.py
│   ├── urls.py
│
├── templates/
├── static/
├── media/
├── db.sqlite3
└── manage.py
```

---

# ⚙️ Installation Guide

Follow these steps to run locally:

## 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

## 2️⃣ Create Virtual Environment

```bash
python -m venv env
```

Activate:

```bash
env\Scripts\activate
```

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

## 4️⃣ Apply Migrations

```bash
python manage.py migrate
```

## 5️⃣ Run Server

```bash
python manage.py runserver
```

Open:

```
http://127.0.0.1:8000/
```

---

# 📸 Features Summary

✔ Real-time messaging
✔ Room-based chat
✔ Authentication system
✔ WebSocket integration
✔ Typing indicator
✔ Online users tracking
✔ Read receipts
✔ File & image sharing
✔ Secure room access
✔ Tailwind UI

---

# 🎯 Future Improvements

Possible upgrades:

* Redis integration (Production)
* Message reactions
* Voice messages
* Video calling
* Notifications system

---

# 👨‍💻 Author

**Abhay Sharma**
B.Tech Student | Python & Django Developer

---

# ⭐ Why This Project Matters

This project demonstrates:

* Django Channels knowledge
* Real-time WebSocket handling
* Authentication system design
* Database modeling
* Frontend integration
* Full-stack project capability

Suitable for:

* Placement portfolio
* Resume projects
* Internship showcase

---

