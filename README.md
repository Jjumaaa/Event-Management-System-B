# Cristina made me delete everything!

...Juma this is for you .... 
if you want to know the routes that are in this backend... here they are 


## 🛠 API ROUTES SUMMARY

Here’s how to interact with the backend:

### 🔐 Auth

* `POST /register` — Create a new user account (email + password).
* `POST /login` — Log in and get a JWT token.
* `GET /me` — Get the currently logged-in user's info *(requires token)*.

---

### 👤 Users

* `GET /users` — Get a list of all users.
* `POST /users` — Add a new user manually.
* `GET /users/<id>` — Get a single user by ID.
* `PATCH /users/<id>` — Update a user's email or password.
* `DELETE /users/<id>` — Delete a user.

---

### 📅 Events *(requires login)*

* `GET /events` — View all events.
* `POST /events` — Create a new event.
* `GET /events/<id>` — View a single event.
* `PATCH /events/<id>` — Edit event details.
* `DELETE /events/<id>` — Delete an event.

---

### 📝 Registrations *(requires login)*

* `GET /registrations` — View all registrations.
* `POST /registrations` — Register for an event.
* `GET /registrations/<id>` — View a specific registration.
* `PATCH /registrations/<id>` — Update registration status.
* `DELETE /registrations/<id>` — Cancel a registration.

---

### 🧠 Notes

* Use JWT token in headers for protected routes:
  `Authorization: Bearer <your_token>`
* Data is sent and received as JSON.

---




