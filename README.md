# OmniPriceX
OmniPriceX is an AI-powered dynamic pricing system built with Django and React. It leverages machine learning, real-time data analysis, and automation to optimize pricing strategies. Designed for scalability, accuracy, and efficiency, it helps businesses maximize revenue through intelligent price adjustments.

## Project Structure
```
OmniPriceX
├── backend
│   ├── omnipricex
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── manage.py
│   └── requirements.txt
├── frontend
│   ├── public
│   │   ├── index.html
│   └── src
│       ├── App.js
│       ├── index.js
│       └── components
│           └── ExampleComponent.js
├── package.json
└── .gitignore
```

## Installation

### Backend
1. Navigate to the `backend` directory.
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the Django server:
   ```
   python manage.py runserver
   ```

### Frontend
1. Navigate to the `frontend` directory.
2. Install the required npm packages:
   ```
   npm install
   ```
3. Start the React application:
   ```
   npm start
   ```

## Features
- Dynamic pricing adjustments based on real-time data.
- Scalable architecture to handle varying loads.
- Machine learning algorithms for price optimization.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License.