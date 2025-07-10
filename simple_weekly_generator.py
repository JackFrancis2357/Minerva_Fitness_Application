"""
Simple weekly workout generator as a fallback when OpenAI is unavailable.
"""

import random
from typing import List, Dict, Any


def generate_simple_weekly_plan(equipment: List[str], daily_duration: int, weekly_goal: str) -> Dict[str, Any]:
    """Generate a simple weekly workout plan without OpenAI."""
    
    # Equipment-based exercise templates
    exercise_templates = {
        'bodyweight': [
            {"name": "Push-ups", "sets": 3, "reps": "10-15", "rest_seconds": 60, "muscle_group": "chest"},
            {"name": "Squats", "sets": 3, "reps": "15-20", "rest_seconds": 60, "muscle_group": "legs"},
            {"name": "Planks", "sets": 3, "reps": "30-45 sec", "rest_seconds": 45, "muscle_group": "core"},
            {"name": "Lunges", "sets": 3, "reps": "10 each leg", "rest_seconds": 60, "muscle_group": "legs"},
            {"name": "Mountain climbers", "sets": 3, "reps": "20 sec", "rest_seconds": 40, "muscle_group": "cardio"},
            {"name": "Burpees", "sets": 3, "reps": "8-10", "rest_seconds": 90, "muscle_group": "full body"},
            {"name": "Jumping jacks", "sets": 3, "reps": "30 sec", "rest_seconds": 30, "muscle_group": "cardio"}
        ],
        'dumbbells': [
            {"name": "Dumbbell bench press", "sets": 3, "reps": "10-12", "rest_seconds": 90, "muscle_group": "chest"},
            {"name": "Dumbbell rows", "sets": 3, "reps": "10-12", "rest_seconds": 90, "muscle_group": "back"},
            {"name": "Dumbbell squats", "sets": 3, "reps": "12-15", "rest_seconds": 90, "muscle_group": "legs"},
            {"name": "Dumbbell shoulder press", "sets": 3, "reps": "10-12", "rest_seconds": 75, "muscle_group": "shoulders"},
            {"name": "Dumbbell bicep curls", "sets": 3, "reps": "12-15", "rest_seconds": 60, "muscle_group": "arms"}
        ],
        'kettlebells': [
            {"name": "Kettlebell swings", "sets": 3, "reps": "15-20", "rest_seconds": 90, "muscle_group": "full body"},
            {"name": "Kettlebell goblet squats", "sets": 3, "reps": "12-15", "rest_seconds": 90, "muscle_group": "legs"},
            {"name": "Kettlebell Turkish get-ups", "sets": 2, "reps": "5 each side", "rest_seconds": 120, "muscle_group": "full body"}
        ],
        'pull_up_bar': [
            {"name": "Pull-ups", "sets": 3, "reps": "5-10", "rest_seconds": 120, "muscle_group": "back"},
            {"name": "Chin-ups", "sets": 3, "reps": "5-8", "rest_seconds": 120, "muscle_group": "back"}
        ]
    }
    
    # Get available exercises based on equipment
    available_exercises = []
    for eq in equipment:
        if eq in exercise_templates:
            available_exercises.extend(exercise_templates[eq])
    
    # Always include bodyweight exercises
    if 'bodyweight' in equipment or not available_exercises:
        available_exercises.extend(exercise_templates['bodyweight'])
    
    # Define weekly structure based on goal
    if 'strength' in weekly_goal.lower() or 'muscle' in weekly_goal.lower():
        weekly_structure = {
            'monday': {'focus': 'Upper Body Strength', 'type': 'strength'},
            'tuesday': {'focus': 'Lower Body Strength', 'type': 'strength'},
            'wednesday': {'focus': 'Cardio & Core', 'type': 'cardio'},
            'thursday': {'focus': 'Upper Body Power', 'type': 'strength'},
            'friday': {'focus': 'Full Body', 'type': 'full_body'},
            'saturday': {'focus': 'Active Recovery', 'type': 'recovery'},
            'sunday': {'focus': 'Rest', 'type': 'rest'}
        }
    elif 'cardio' in weekly_goal.lower() or 'endurance' in weekly_goal.lower():
        weekly_structure = {
            'monday': {'focus': 'HIIT Cardio', 'type': 'cardio'},
            'tuesday': {'focus': 'Strength Training', 'type': 'strength'},
            'wednesday': {'focus': 'Steady State Cardio', 'type': 'cardio'},
            'thursday': {'focus': 'Upper Body', 'type': 'strength'},
            'friday': {'focus': 'Circuit Training', 'type': 'full_body'},
            'saturday': {'focus': 'Low Intensity Cardio', 'type': 'recovery'},
            'sunday': {'focus': 'Rest', 'type': 'rest'}
        }
    else:  # General fitness
        weekly_structure = {
            'monday': {'focus': 'Upper Body', 'type': 'strength'},
            'tuesday': {'focus': 'Lower Body', 'type': 'strength'},
            'wednesday': {'focus': 'Cardio', 'type': 'cardio'},
            'thursday': {'focus': 'Full Body', 'type': 'full_body'},
            'friday': {'focus': 'Core & Flexibility', 'type': 'core'},
            'saturday': {'focus': 'Active Recovery', 'type': 'recovery'},
            'sunday': {'focus': 'Rest', 'type': 'rest'}
        }
    
    # Generate daily workouts
    daily_workouts = {}
    
    for day, info in weekly_structure.items():
        if info['type'] == 'rest':
            daily_workouts[day] = {
                "focus": "Rest and Recovery",
                "description": "Complete rest day for muscle recovery",
                "rest_day": True,
                "exercises": [],
                "duration_minutes": 0,
                "recovery_activities": ["light stretching", "walk", "meditation"]
            }
        else:
            # Select exercises for this day
            day_exercises = []
            target_exercises = min(6, max(3, daily_duration // 8))  # Rough estimate
            
            # Filter exercises by type and muscle group
            if info['type'] == 'cardio':
                filtered = [ex for ex in available_exercises if 'cardio' in ex['muscle_group'] or 'full body' in ex['muscle_group']]
            elif info['type'] == 'strength':
                filtered = [ex for ex in available_exercises if ex['muscle_group'] not in ['cardio']]
            else:
                filtered = available_exercises
            
            # Select random exercises
            selected = random.sample(filtered, min(target_exercises, len(filtered)))
            
            for exercise in selected:
                day_exercises.append({
                    "name": exercise["name"],
                    "sets": exercise["sets"],
                    "reps": exercise["reps"],
                    "rest_seconds": exercise["rest_seconds"],
                    "instructions": "Focus on proper form and controlled movement",
                    "muscle_group": exercise["muscle_group"]
                })
            
            daily_workouts[day] = {
                "focus": info['focus'],
                "description": f"Focus on {info['focus'].lower()} exercises",
                "rest_day": False,
                "exercises": day_exercises,
                "duration_minutes": daily_duration,
                "warmup": "5-10 minutes of light movement and dynamic stretching",
                "cooldown": "5-10 minutes of static stretching and deep breathing"
            }
    
    return {
        "weekly_goal": weekly_goal,
        "total_weekly_duration": daily_duration * 6,
        "plan_description": f"A balanced weekly plan focused on {weekly_goal.lower()}. This is a simplified plan generated when AI assistance is unavailable.",
        "daily_workouts": daily_workouts,
        "weekly_tips": [
            "Focus on proper form over speed or weight",
            "Stay hydrated throughout your workouts",
            "Listen to your body and rest when needed",
            "Progress gradually by increasing intensity weekly"
        ],
        "fallback_used": True
    }