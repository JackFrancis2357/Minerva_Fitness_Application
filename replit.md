# Weekly Workout Planner

## Overview

The Weekly Workout Planner is a web application that generates personalized workout plans based on user-selected equipment and desired workout duration. Built with Flask, Python, and OpenAI's GPT-4o, it provides both single workout sessions and intelligent weekly workout schedules. The application offers a simple, user-friendly interface for creating customized fitness routines without requiring user accounts or complex authentication.

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
  - `/` - Renders equipment selection, duration input, and plan type selection form
  - `/workout` - Processes form data and generates either single workout or weekly plan
- **Error Handling**: Form validation with user feedback via Flask flash messages
- **New Features**: Plan type selection (daily/weekly), weekly goal specification

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

### 5. OpenAI Integration (`openai_integration.py`)
- **Purpose**: GPT-4o integration for intelligent weekly workout planning
- **Key Features**:
  - Weekly plan generation based on goals and equipment
  - Structured 7-day workout schedules
  - Personalized fitness recommendations
- **Fallback Logic**: Provides basic weekly structure if OpenAI fails

### 6. Static Assets
- **CSS**: Custom styling complementing Bootstrap theme
- **JavaScript**: Form validation, slider synchronization, plan type selection, and UI enhancements

### 7. Template System
- **Base Template**: Common layout with Bootstrap navigation and flash message handling
- **Index Template**: Equipment selection form with plan type and weekly goal options
- **Workout Template**: Generated single workout plan display with exercise details
- **Weekly Workout Template**: AI-generated weekly schedule with daily workout summaries

## Data Flow

### Single Workout Generation
1. **User Input**: User selects equipment, duration, and "Single Workout" plan type
2. **Form Submission**: POST request to `/workout` endpoint
3. **Validation**: Server validates equipment selection and duration range (15-90 minutes)
4. **Exercise Filtering**: WorkoutGenerator filters exercises based on available equipment
5. **Workout Generation**: Algorithm selects and organizes exercises to fit target duration
6. **Response**: Rendered workout plan page with exercise details and timing

### Weekly Plan Generation
1. **User Input**: User selects equipment, duration, "Weekly Plan" type, and fitness goal
2. **Form Submission**: POST request to `/workout` endpoint with weekly parameters
3. **Validation**: Server validates all inputs including weekly goal specification
4. **OpenAI Integration**: GPT-4o generates intelligent 7-day workout schedule
5. **Plan Structure**: AI creates balanced weekly routine with rest days and progression
6. **Response**: Rendered weekly workout plan page with daily summaries and tips

## External Dependencies

### Frontend Dependencies
- **Bootstrap 5**: UI framework (CDN-delivered)
- **Bootstrap Icons**: Icon library for visual elements
- **Custom CSS**: Additional styling for branding and UX

### Backend Dependencies
- **Flask**: Web framework
- **OpenAI**: GPT-4o integration for weekly plan generation
- **Python Standard Library**: JSON handling, logging, random selection

### Environment Configuration
- **SESSION_SECRET**: Environment variable for Flask session security
- **OPENAI_API_KEY**: OpenAI API key for GPT-4o weekly plan generation
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
├── app.py                    # Main Flask application
├── main.py                  # Application entry point
├── workout_generator.py     # Single workout business logic
├── openai_integration.py    # GPT-4o weekly plan generation
├── exercises.json          # Exercise database
├── templates/              # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   ├── workout.html
│   └── weekly_workout.html
└── static/                # Static assets
    ├── css/style.css
    └── js/script.js
```

## Recent Changes (July 10, 2025)

✓ Added OpenAI GPT-4o integration for weekly workout planning
✓ Extended user interface to support plan type selection (daily vs. weekly)
✓ Implemented weekly goal specification with predefined options and custom input
✓ Created new weekly workout template with 7-day schedule display
✓ Enhanced JavaScript for dynamic form behavior and validation
✓ Added fallback logic for reliable weekly plan generation
✓ Updated application architecture to support both single and weekly workout modes

The application is designed as a simple, self-contained web service that can be easily deployed to various hosting platforms without external database dependencies.