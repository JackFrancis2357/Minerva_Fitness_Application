import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from workout_generator import WorkoutGenerator
from openai_integration import generate_weekly_workout_plan, get_workout_goal_suggestions
from simple_weekly_generator import generate_simple_weekly_plan
from datetime import datetime, timedelta
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") or "sqlite:///fitness_app.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db.init_app(app)

# Create database tables
with app.app_context():
    import models
    db.create_all()

# Initialize workout generator
workout_gen = WorkoutGenerator()

# Subscription tier limits and pricing
SUBSCRIPTION_TIERS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'daily_workouts': 3,
        'weekly_plans': 1,
        'saved_plans': 2,
        'features': ['Basic workout generator', 'Limited equipment options', 'Basic weekly plans']
    },
    'premium': {
        'name': 'Premium',
        'price': 9.99,
        'daily_workouts': 15,
        'weekly_plans': 5,
        'saved_plans': 20,
        'features': ['Unlimited workout generator', 'All equipment options', 'Advanced weekly plans', 'Progress tracking', 'Workout history', 'Custom exercises']
    },
    'pro': {
        'name': 'Pro',
        'price': 19.99,
        'daily_workouts': 999,
        'weekly_plans': 999,
        'saved_plans': 999,
        'features': ['Everything in Premium', 'AI-powered nutrition plans', 'Personalized coaching tips', 'Advanced analytics', 'Export workout plans', 'Priority support']
    }
}


@app.route('/')
def index():
    """Render the main page with equipment selection and duration input."""
    goal_suggestions = get_workout_goal_suggestions()
    return render_template('index.html', 
                         goal_suggestions=goal_suggestions,
                         subscription_tiers=SUBSCRIPTION_TIERS)


@app.route('/pricing')
def pricing():
    """Display pricing and subscription options."""
    return render_template('pricing.html', subscription_tiers=SUBSCRIPTION_TIERS)


@app.route('/dashboard')
def dashboard():
    """User dashboard for premium features."""
    # For demo purposes, we'll simulate a user session
    user_id = session.get('user_id', 'demo_user')
    
    # Get user's saved workout plans
    from models import WorkoutPlan, WorkoutProgress
    saved_plans = WorkoutPlan.query.filter_by(user_id=user_id).limit(10).all()
    recent_progress = WorkoutProgress.query.filter_by(user_id=user_id).order_by(WorkoutProgress.date.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         saved_plans=saved_plans,
                         recent_progress=recent_progress,
                         subscription_tiers=SUBSCRIPTION_TIERS)


@app.route('/workout', methods=['POST'])
def generate_workout():
    """Generate and display a workout plan based on user input."""
    try:
        # Get form data
        equipment = request.form.getlist('equipment')
        duration = request.form.get('duration', type=int)
        plan_type = request.form.get('plan_type', 'daily')
        weekly_goal = request.form.get('weekly_goal', '')
        custom_goal = request.form.get('custom_weekly_goal', '')
        
        # Handle custom goal
        if weekly_goal == 'custom' and custom_goal.strip():
            weekly_goal = custom_goal.strip()
        
        # Validate inputs
        if not duration or duration < 15 or duration > 90:
            flash('Please select a duration between 15 and 90 minutes.', 'error')
            return redirect(url_for('index'))
        
        if not equipment:
            flash('Please select at least one equipment option.', 'error')
            return redirect(url_for('index'))
        
        if plan_type == 'weekly' and not weekly_goal.strip():
            flash('Please specify your weekly workout goal.', 'error')
            return redirect(url_for('index'))
        
        # Check subscription limits (simulated for demo)
        user_id = session.get('user_id', 'demo_user')
        subscription_tier = session.get('subscription_tier', 'free')
        
        # Demo usage limits check
        if subscription_tier == 'free' and plan_type == 'weekly':
            weekly_count = session.get('weekly_plans_count', 0)
            if weekly_count >= SUBSCRIPTION_TIERS['free']['weekly_plans']:
                flash('Free users are limited to 1 weekly plan. Upgrade to Premium for unlimited weekly plans!', 'warning')
                return redirect(url_for('pricing'))
        
        if plan_type == 'weekly':
            # Use fallback generator for reliability
            try:
                weekly_plan = generate_simple_weekly_plan(
                    equipment=equipment,
                    daily_duration=duration,
                    weekly_goal=weekly_goal
                )
                
                # Update usage counter for demo
                session['weekly_plans_count'] = session.get('weekly_plans_count', 0) + 1
                
                return render_template('weekly_workout.html',
                                     weekly_plan=weekly_plan,
                                     equipment=equipment,
                                     duration=duration,
                                     weekly_goal=weekly_goal,
                                     subscription_tier=subscription_tier)
            except Exception as e:
                logging.error(f"Simple weekly plan generation failed: {str(e)}")
                flash('Unable to generate weekly plan right now. Please try again or create a single workout instead.', 'error')
                return redirect(url_for('index'))
        else:
            # Generate single workout plan
            try:
                workout_plan = workout_gen.generate_workout(equipment, duration)
                
                # Update usage counter for demo
                session['daily_workouts_count'] = session.get('daily_workouts_count', 0) + 1
                
                return render_template('workout.html',
                                     workout_plan=workout_plan,
                                     equipment=equipment,
                                     duration=duration,
                                     subscription_tier=subscription_tier)
            except Exception as e:
                logging.error(f"Workout generation failed: {str(e)}")
                flash('Unable to generate workout plan right now. Please try again.', 'error')
                return redirect(url_for('index'))
    
    except Exception as e:
        logging.error(f"Error in generate_workout: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('index'))


@app.route('/save-workout', methods=['POST'])
def save_workout():
    """Save a workout plan for premium users."""
    try:
        user_id = session.get('user_id', 'demo_user')
        subscription_tier = session.get('subscription_tier', 'free')
        
        # Check if user has premium access
        if subscription_tier == 'free':
            return jsonify({'error': 'Premium feature. Please upgrade to save workouts.'}), 403
        
        # Get workout data from request
        workout_data = request.get_json()
        
        # Save to database
        from models import WorkoutPlan
        new_plan = WorkoutPlan(
            user_id=user_id,
            name=workout_data.get('name', 'My Workout'),
            plan_type=workout_data.get('plan_type', 'daily'),
            equipment=json.dumps(workout_data.get('equipment', [])),
            duration=workout_data.get('duration', 30),
            weekly_goal=workout_data.get('weekly_goal', ''),
            plan_data=json.dumps(workout_data.get('plan_data', {}))
        )
        
        db.session.add(new_plan)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Workout saved successfully!'})
    
    except Exception as e:
        logging.error(f"Error saving workout: {str(e)}")
        return jsonify({'error': 'Failed to save workout'}), 500


@app.route('/subscribe/<tier>')
def subscribe(tier):
    """Handle subscription upgrade (demo with placeholder Stripe integration)."""
    if tier not in SUBSCRIPTION_TIERS:
        flash('Invalid subscription tier.', 'error')
        return redirect(url_for('pricing'))
    
    # For demo purposes, we'll simulate successful subscription
    session['subscription_tier'] = tier
    session['user_id'] = 'demo_user'
    
    flash(f'Successfully upgraded to {SUBSCRIPTION_TIERS[tier]["name"]} plan! (Demo mode)', 'success')
    return redirect(url_for('dashboard'))


@app.route('/nutrition-planner')
def nutrition_planner():
    """Nutrition planning feature (Pro only)."""
    subscription_tier = session.get('subscription_tier', 'free')
    
    if subscription_tier != 'pro':
        flash('Nutrition planning is a Pro feature. Please upgrade to access this feature.', 'warning')
        return redirect(url_for('pricing'))
    
    return render_template('nutrition_planner.html')


@app.route('/progress-tracker')
def progress_tracker():
    """Progress tracking feature (Premium+)."""
    subscription_tier = session.get('subscription_tier', 'free')
    
    if subscription_tier == 'free':
        flash('Progress tracking is a Premium feature. Please upgrade to access this feature.', 'warning')
        return redirect(url_for('pricing'))
    
    # Get user's progress data
    user_id = session.get('user_id', 'demo_user')
    from models import WorkoutProgress
    progress_data = WorkoutProgress.query.filter_by(user_id=user_id).order_by(WorkoutProgress.date.desc()).limit(30).all()
    
    return render_template('progress_tracker.html', progress_data=progress_data)


@app.route('/custom-exercises')
def custom_exercises():
    """Custom exercise creation (Premium+)."""
    subscription_tier = session.get('subscription_tier', 'free')
    
    if subscription_tier == 'free':
        flash('Custom exercises is a Premium feature. Please upgrade to access this feature.', 'warning')
        return redirect(url_for('pricing'))
    
    # Get user's custom exercises
    user_id = session.get('user_id', 'demo_user')
    from models import CustomExercise
    custom_exercises = CustomExercise.query.filter_by(user_id=user_id).all()
    
    return render_template('custom_exercises.html', custom_exercises=custom_exercises)


@app.route('/api/usage-stats')
def usage_stats():
    """API endpoint to get user's usage statistics."""
    user_id = session.get('user_id', 'demo_user')
    subscription_tier = session.get('subscription_tier', 'free')
    
    # Get current usage (simulated for demo)
    daily_workouts = session.get('daily_workouts_count', 0)
    weekly_plans = session.get('weekly_plans_count', 0)
    
    tier_limits = SUBSCRIPTION_TIERS[subscription_tier]
    
    return jsonify({
        'subscription_tier': subscription_tier,
        'daily_workouts': {
            'used': daily_workouts,
            'limit': tier_limits['daily_workouts']
        },
        'weekly_plans': {
            'used': weekly_plans,
            'limit': tier_limits['weekly_plans']
        }
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logging.error(f"Internal error: {str(error)}")
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)