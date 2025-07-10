from datetime import datetime, timedelta
from app import db
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint


# User model for authentication
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)
    subscription_tier = db.Column(db.String, default='free')  # free, premium, pro
    subscription_end_date = db.Column(db.DateTime, nullable=True)
    stripe_customer_id = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Usage tracking for limits
    daily_workouts_count = db.Column(db.Integer, default=0)
    weekly_plans_count = db.Column(db.Integer, default=0)
    last_usage_reset = db.Column(db.DateTime, default=datetime.now)
    
    def is_premium(self):
        return self.subscription_tier in ['premium', 'pro']
    
    def is_pro(self):
        return self.subscription_tier == 'pro'
    
    def is_subscription_active(self):
        if self.subscription_end_date:
            return datetime.now() < self.subscription_end_date
        return False
    
    def reset_daily_limits_if_needed(self):
        """Reset daily usage counters if it's a new day"""
        if self.last_usage_reset.date() < datetime.now().date():
            self.daily_workouts_count = 0
            self.weekly_plans_count = 0
            self.last_usage_reset = datetime.now()
            db.session.commit()


# OAuth storage for Replit authentication
class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = db.relationship(User)

    __table_args__ = (UniqueConstraint(
        'user_id',
        'browser_session_key', 
        'provider',
        name='uq_user_browser_session_key_provider',
    ),)


# Workout plans storage for premium users
class WorkoutPlan(db.Model):
    __tablename__ = 'workout_plans'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    plan_type = db.Column(db.String(50), nullable=False)  # single, weekly
    equipment = db.Column(db.Text)  # JSON string
    duration = db.Column(db.Integer)
    weekly_goal = db.Column(db.String(200))
    plan_data = db.Column(db.Text)  # JSON string of workout data
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_favorite = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='workout_plans')


# Progress tracking for premium users
class WorkoutProgress(db.Model):
    __tablename__ = 'workout_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    workout_plan_id = db.Column(db.Integer, db.ForeignKey('workout_plans.id'), nullable=True)
    date = db.Column(db.Date, nullable=False)
    exercises_completed = db.Column(db.Integer, default=0)
    total_exercises = db.Column(db.Integer, default=0)
    duration_minutes = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
    difficulty_rating = db.Column(db.Integer)  # 1-5 scale
    
    user = db.relationship('User', backref='progress_entries')
    workout_plan = db.relationship('WorkoutPlan', backref='progress_entries')


# Nutrition plans for pro users
class NutritionPlan(db.Model):
    __tablename__ = 'nutrition_plans'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    goal = db.Column(db.String(100))  # weight_loss, muscle_gain, maintenance
    daily_calories = db.Column(db.Integer)
    macros = db.Column(db.Text)  # JSON string of macro targets
    meal_plan = db.Column(db.Text)  # JSON string of meal plans
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship('User', backref='nutrition_plans')


# Custom exercises for premium users
class CustomExercise(db.Model):
    __tablename__ = 'custom_exercises'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    muscle_group = db.Column(db.String(100))
    equipment_needed = db.Column(db.Text)  # JSON string
    difficulty_level = db.Column(db.Integer)  # 1-5 scale
    instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship('User', backref='custom_exercises')


# Subscription payments tracking
class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    stripe_payment_intent_id = db.Column(db.String, nullable=False)
    amount = db.Column(db.Integer)  # Amount in cents
    currency = db.Column(db.String, default='usd')
    subscription_tier = db.Column(db.String, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String, default='pending')
    
    user = db.relationship('User', backref='payments')