# Django Project Setup

## Prerequisites

- Git installed on your machine
- Python and pip installed
- Virtualenv installed (optional but recommended)

## Getting Started

1. Clone the repository:

   ```bash
   git clone <repository_url>
   ```

i. Navigate to the project directory:

```bash
cd <project_directory>
```

ii. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate #linux users, check online resources for windows

```

iii. Install dependencies
```bash
pip install -r requirements.txt

```

iv. Create a copy of the .env.example file and rename it to .env.

v. Run the Django development server:

```bash
python manage.py runserver

```

### Note:
Access the live URL:

The live URL can be found at: [Live URL](https://fozy-sms.onrender.com/api)
Visit[API Docs](https://fozy-sms.onrender.com/api/swagger) for API documentation.

## Additional Notes
- Make sure to set up your database configurations in the .env file.
- Customize any additional settings or configurations as needed.