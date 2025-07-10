import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from workout_generator import WorkoutGenerator

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Initialize workout generator
workout_gen = WorkoutGenerator()

@app.route('/')
def index():
    """Render the main page with equipment selection and duration input."""
    return render_template('index.html')

@app.route('/workout', methods=['POST'])
def generate_workout():
    """Generate and display a workout plan based on user input."""
    try:
        # Get form data
        equipment = request.form.getlist('equipment')
        duration = request.form.get('duration', type=int)
        
        # Validate inputs
        if not duration or duration < 15 or duration > 90:
            flash('Please select a duration between 15 and 90 minutes.', 'error')
            return redirect(url_for('index'))
        
        if not equipment:
            flash('Please select at least one equipment option.', 'error')
            return redirect(url_for('index'))
        
        # Generate workout plan
        workout_plan = workout_gen.generate_workout(equipment, duration)
        
        if not workout_plan['exercises']:
            flash('No exercises found for the selected equipment. Please try different options.', 'error')
            return redirect(url_for('index'))
        
        return render_template('workout.html', 
                             workout=workout_plan, 
                             equipment=equipment, 
                             duration=duration)
    
    except Exception as e:
        logging.error(f"Error generating workout: {str(e)}")
        flash('An error occurred while generating your workout. Please try again.', 'error')
        return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logging.error(f"Internal server error: {str(error)}")
    flash('An internal error occurred. Please try again.', 'error')
    return render_template('index.html'), 500
