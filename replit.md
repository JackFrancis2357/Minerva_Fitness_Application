# Daily Workout Planner

## Overview

The Daily Workout Planner is a web application that generates personalized workout plans based on user-selected equipment and desired workout duration. Built with Flask and Python, it provides a simple, user-friendly interface for creating customized fitness routines without requiring user accounts or complex authentication.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Technology**: Server-side rendered HTML templates using Jinja2
- **Styling**: Bootstrap 5 with dark theme and custom CSS
- **Interactivity**: Vanilla JavaScript for form handling and UI enhancements
- **Design Pattern**: Traditional multi-page application with form submissions

### Backend Architecture
- **Framework**: Flask (Python) - chosen for simplicity and rapid development
- **Architecture Pattern**: Monolithic web application
- **Request Handling**: Standard HTTP POST/GET requests
- **Business Logic**: Separated into dedicated `WorkoutGenerator` class

### Data Storage
- **Exercise Data**: JSON file (`exercises.json`) containing exercise definitions
- **Session Management**: Flask sessions with configurable secret key
- **No Database**: Stateless application without persistent user data storage

## Key Components

### 1. Flask Application (`app.py`)
- **Purpose**: Main application entry point and route handling
- **Key Routes**:
  - `/` - Renders equipment selection and duration input form
  - `/workout` - Processes form data and generates workout plan
- **Error Handling**: Form validation with user feedback via Flask flash messages

### 2. Workout Generator (`workout_generator.py`)
- **Purpose**: Core business logic for workout generation
- **Key Features**:
  - Equipment-based exercise filtering
  - Duration calculation and optimization
  - Exercise selection algorithms
- **Equipment Mapping**: Maps user-friendly equipment names to exercise requirements

### 3. Exercise Database (`exercises.json`)
- **Purpose**: Structured exercise data repository
- **Schema**: Each exercise includes:
  - Basic info (name, type, muscle group)
  - Equipment requirements
  - Timing data (duration per rep, sets, rest periods)
  - Descriptive text

### 4. Template System
- **Base Template**: Common layout with Bootstrap navigation and flash message handling
- **Index Template**: Equipment selection form with checkboxes and duration slider
- **Workout Template**: Generated workout plan display with exercise details

### 5. Static Assets
- **CSS**: Custom styling complementing Bootstrap theme
- **JavaScript**: Form validation, slider synchronization, and UI enhancements

## Data Flow

1. **User Input**: User selects equipment and duration via web form
2. **Form Submission**: POST request to `/workout` endpoint
3. **Validation**: Server validates equipment selection and duration range (15-90 minutes)
4. **Exercise Filtering**: WorkoutGenerator filters exercises based on available equipment
5. **Workout Generation**: Algorithm selects and organizes exercises to fit target duration
6. **Response**: Rendered workout plan page with exercise details and timing

## External Dependencies

### Frontend Dependencies
- **Bootstrap 5**: UI framework (CDN-delivered)
- **Bootstrap Icons**: Icon library for visual elements
- **Custom CSS**: Additional styling for branding and UX

### Backend Dependencies
- **Flask**: Web framework
- **Python Standard Library**: JSON handling, logging, random selection

### Environment Configuration
- **SESSION_SECRET**: Environment variable for Flask session security
- **Development Mode**: Debug mode enabled for development environment

## Deployment Strategy

### Development
- **Entry Point**: `main.py` runs Flask development server
- **Host Configuration**: `0.0.0.0:5000` for container compatibility
- **Debug Mode**: Enabled for development with detailed error reporting

### Production Considerations
- **Static Files**: Served via Flask's built-in static file handling
- **Session Security**: Configurable secret key via environment variables
- **Error Handling**: Logging configured for debugging and monitoring
- **Scalability**: Stateless design allows for horizontal scaling

### File Structure
```
├── app.py                 # Main Flask application
├── main.py               # Application entry point
├── workout_generator.py  # Business logic
├── exercises.json        # Exercise database
├── templates/            # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   └── workout.html
└── static/              # Static assets
    ├── css/style.css
    └── js/script.js
```

The application is designed as a simple, self-contained web service that can be easily deployed to various hosting platforms without external database dependencies.