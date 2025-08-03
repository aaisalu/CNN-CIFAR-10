# 🧠 CIFAR-10 Image Classifier Web App

A full-stack web application for real-time image classification using a Convolutional Neural Network (CNN) trained on the CIFAR-10 dataset. Users can register, log in (via email or Google), upload images, and receive instant predictions.

The project features a modern, responsive UI, social login integration, an admin dashboard, and PDF export of prediction history.

---

## 🚀 Quick Start

1. **Clone the repository**
2. **Install dependencies**
3. **Configure `.env` and initialize the database**
4. **Run the development server**

```sh
uv run python manage.py runserver
```

5. **Upload an image to receive a prediction**

---

## ✨ Features

- **🔐 User Authentication:**
  Email/password login, password reset, and Google OAuth integration.

- **👤 Profile Management:**
  Users can update their email and password directly from the dashboard.

- **🖼️ Image Upload & Prediction:**
  Upload `.jpg` or `.png` images (up to 10MB) for real-time classification using a TensorFlow CNN.

- **📄 Prediction History:**
  View and export your prediction history as downloadable PDFs with image previews.

- **🛠️ Admin Dashboard:**
  Superusers can view user statistics and analytics.

- **💻 Modern UI:**
  Built with Tailwind CSS and AOS animations for a clean, responsive experience.

---

## 📁 Project Structure

```txt
.
├── manage.py
├── main.py
├── pyproject.toml
├── db.sqlite3
├── .env                     # Environment variables
├── sample.env               # Sample environment file
├── README.md
├── account/                 # Authentication and user logic
├── imgpredict/              # Django project configuration
├── prediction/              # Image classification logic
├── static/                  # CSS and JS assets
├── collected_static/        # Collected static files (via collectstatic)
├── media/                   # Uploaded media files
├── templates/               # HTML templates
└── notebook/
    └── cnn_tf.ipynb         # CNN model training notebook
```

---

## 🛠️ Installation Guide

### 1. Clone the Repository

```sh
git clone https://github.com/aaisalu/CNN_CIFAR_10.git
cd CNN_CIFAR_10
```

### 2. Set Up Python Environment

Make sure **Python 3.12** is installed.

Create and activate a virtual environment (recommended: [`uv`](https://github.com/astral-sh/uv)):

```sh
uv venv --python 3.12
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Remaining Dependencies

```sh
uv sync
```

Install TensorFlow separately due to native dependencies:

```sh
uv pip install tensorflow==2.18.0
```

### 4. Configure Environment Variables

Copy the sample environment file:

```sh
cp sample.env .env
```

Edit `.env` to include your project-specific values:

```ini
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GOOGLE_OAUTH2_KEY=your-google-oauth-client-id
GOOGLE_OAUTH2_SECRET=your-google-oauth-client-secret
EMAIL_HOST=smtp.mailtrap.io
EMAIL_HOST_USER=your-mailtrap-username
EMAIL_HOST_PASSWORD=your-mailtrap-password
EMAIL_PORT=2525
```

| Variable               | Description                              |
| ---------------------- | ---------------------------------------- |
| `SECRET_KEY`           | Django’s cryptographic key               |
| `DEBUG`                | Set to `False` in production             |
| `ALLOWED_HOSTS`        | Comma-separated list of allowed hosts    |
| `GOOGLE_OAUTH2_KEY`    | Google OAuth2 Client ID                  |
| `GOOGLE_OAUTH2_SECRET` | Google OAuth2 Client Secret              |
| `EMAIL_*`              | SMTP mail configuration (e.g., Mailtrap) |

### 5. Initialize the Database

```sh
uv run python manage.py makemigrations
uv run python manage.py migrate
```

To reset the database:

```sh
rm db.sqlite3 -f
uv run python manage.py migrate
uv run python manage.py createsuperuser
```

### 6. Collect Static Files

```sh
python manage.py collectstatic
```

### 7. Start the Server

```sh
uv run python manage.py runserver
```

Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 🧬 CNN Model Details

- Trained on the CIFAR-10 dataset using TensorFlow.
- Architecture and training code is located in [`notebook/cnn_tf.ipynb`](notebook/cnn_tf.ipynb).
- The trained model is loaded at runtime from a `.keras` file.

To retrain or update the model:

1. Modify and retrain it in the notebook.
2. Export the model as a `.keras` file.
3. Update `prediction/naive.py` with the new file path if needed.

---

## 🧪 Running Tests

To run tests:

```sh
uv run python manage.py test
```

---

## 🚀 Deployment Notes

- Set `DEBUG=False` in production.
- Add your domain to `ALLOWED_HOSTS`.
- Use a WSGI server (e.g., **Gunicorn**) behind **Nginx** or deploy via platforms like **Railway** or **Heroku**.
- Ensure media/static files are properly served.
- Collect static files before deploying:

```sh
python manage.py collectstatic --noinput
```

---

## 📂 Static & Media Files

- **Media Uploads:** Stored in `media/images/`
- **Static Assets:** Found in `static/` and `collected_static/`

---

## ⚙️ Customization

- **Django Settings:** Modify `imgpredict/settings.py`
- **UI Templates:** Customize templates in the `templates/` directory.
- **Model:** Retrain or replace the CNN model using the Jupyter notebook.

---

## 🛨️ Troubleshooting

- Open the Django database shell:

```sh
uv run python manage.py dbshell
```

- Static files not displaying?

```sh
python manage.py collectstatic
```

---

## 📄 License

- Source Code: [MIT License](LICENSE)
- Icons: Font Awesome ([details](collected_static/admin/img/README.txt))

---

## 🙌 Acknowledgements

Built using:

- **Django** – Backend web framework
- **TensorFlow** – Deep learning framework
- **Tailwind CSS** – Utility-first CSS framework
- **AOS** – Animate On Scroll library

---

## 💬 Support

For help or feature requests:

- Open an issue on GitHub
- Contact the project maintainer
