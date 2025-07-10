import json
import os
from typing import Dict, List, Any

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
    timeout=10.0  # Much shorter timeout - 10 seconds max
)


def generate_weekly_workout_plan(equipment: List[str], daily_duration: int, weekly_goal: str, exercises: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a weekly workout plan using GPT-4o based on user preferences and available exercises."""
    
    # Prepare equipment list for the prompt
    equipment_str = ", ".join(equipment) if equipment else "bodyweight only"
    
    # Prepare exercise database summary for context (limit to reduce prompt size)
    exercise_summary = []
    for exercise in exercises[:15]:  # Reduce to prevent timeout
        exercise_summary.append({
            "name": exercise.get("name", ""),
            "type": exercise.get("type", ""),
            "muscle_group": exercise.get("muscle_group", ""),
            "equipment_needed": exercise.get("equipment_needed", [])
        })
    
    prompt = f"""Create a comprehensive 7-day weekly workout plan with COMPLETE daily workout details:

REQUIREMENTS:
- Available Equipment: {equipment_str}
- Daily Workout Duration: {daily_duration} minutes per session
- Weekly Goal: {weekly_goal}
- Use exercises from the provided database when possible

AVAILABLE EXERCISES:
{json.dumps(exercise_summary, indent=2)}

WEEKLY PLAN STRUCTURE:
Create a JSON response with exactly this structure:
{{
    "weekly_goal": "{weekly_goal}",
    "total_weekly_duration": (total minutes),
    "plan_description": "Brief overview of the weekly plan approach",
    "daily_workouts": {{
        "monday": {{
            "focus": "primary muscle group or workout type",
            "description": "brief description of the day's workout",
            "rest_day": false,
            "exercises": [
                {{
                    "name": "Exercise name from database or similar",
                    "sets": 3,
                    "reps": "10-12",
                    "rest_seconds": 60,
                    "instructions": "Brief form instructions",
                    "muscle_group": "target muscle"
                }}
            ],
            "duration_minutes": {daily_duration},
            "warmup": "5-minute warm-up description",
            "cooldown": "5-minute cool-down description"
        }},
        "tuesday": {{
            "focus": "different muscle group",
            "description": "brief description", 
            "rest_day": false,
            "exercises": [
                {{
                    "name": "Exercise name",
                    "sets": 3,
                    "reps": "8-10", 
                    "rest_seconds": 90,
                    "instructions": "Brief form instructions",
                    "muscle_group": "target muscle"
                }}
            ],
            "duration_minutes": {daily_duration},
            "warmup": "warm-up description",
            "cooldown": "cool-down description"
        }},
        "wednesday": {{ ... }},
        "thursday": {{ ... }},
        "friday": {{ ... }},
        "saturday": {{ ... }},
        "sunday": {{
            "focus": "Rest and Recovery",
            "description": "Complete rest day for muscle recovery",
            "rest_day": true,
            "exercises": [],
            "duration_minutes": 0,
            "recovery_activities": ["light stretching", "walk", "meditation"]
        }}
    }},
    "weekly_tips": [
        "tip 1 about progression",
        "tip 2 about nutrition", 
        "tip 3 about recovery"
    ]
}}

GUIDELINES:
- Include 1-2 rest days per week
- Each workout day should have 4-8 exercises that fit the duration
- Vary muscle groups and workout types across the week
- Use exercises from the provided database when possible, or create similar ones
- Include specific sets, reps, and rest periods for each exercise
- Provide warm-up and cool-down for each workout day
- Consider the weekly goal when planning intensity and focus
- Keep daily sessions within the specified duration
- Provide practical, actionable advice
- Focus on progressive overload and recovery balance
"""

    try:
        # Try with shorter prompt first to reduce timeout risk
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional fitness trainer creating personalized weekly workout plans. "
                    + "Always respond with valid JSON matching the exact structure requested. "
                    + "Focus on balanced, safe, and effective workout programming."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=2500,
            temperature=0.7
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Validate the response structure
        required_keys = ["weekly_goal", "total_weekly_duration", "plan_description", "daily_workouts", "weekly_tips"]
        if not all(key in result for key in required_keys):
            raise ValueError("Invalid response structure from GPT-4o")
        
        return result
        
    except Exception as e:
        # Log the specific error for debugging
        import logging
        logging.error(f"OpenAI API error: {str(e)}")
        
        # Fallback response if OpenAI fails
        return {
            "weekly_goal": weekly_goal,
            "total_weekly_duration": daily_duration * 6,  # 6 workout days
            "plan_description": f"A balanced weekly plan focused on {weekly_goal.lower()} using {equipment_str}.",
            "daily_workouts": {
                "monday": {
                    "focus": "Upper Body", 
                    "description": "Focus on chest, shoulders, and arms", 
                    "rest_day": False,
                    "exercises": [
                        {"name": "Push-ups", "sets": 3, "reps": "10-15", "rest_seconds": 60, "instructions": "Keep body straight", "muscle_group": "chest"},
                        {"name": "Shoulder raises", "sets": 3, "reps": "12-15", "rest_seconds": 45, "instructions": "Control the movement", "muscle_group": "shoulders"}
                    ],
                    "duration_minutes": daily_duration,
                    "warmup": "5 minutes of arm circles and light movement",
                    "cooldown": "5 minutes of upper body stretching"
                },
                "tuesday": {
                    "focus": "Lower Body", 
                    "description": "Focus on legs and glutes", 
                    "rest_day": False,
                    "exercises": [
                        {"name": "Squats", "sets": 3, "reps": "12-15", "rest_seconds": 90, "instructions": "Keep knees aligned", "muscle_group": "legs"},
                        {"name": "Lunges", "sets": 3, "reps": "10 each leg", "rest_seconds": 60, "instructions": "Step forward and down", "muscle_group": "legs"}
                    ],
                    "duration_minutes": daily_duration,
                    "warmup": "5 minutes of leg swings and marching",
                    "cooldown": "5 minutes of leg stretching"
                },
                "wednesday": {
                    "focus": "Cardio", 
                    "description": "Cardiovascular endurance training", 
                    "rest_day": False,
                    "exercises": [
                        {"name": "Jumping jacks", "sets": 3, "reps": "30 seconds", "rest_seconds": 30, "instructions": "Keep rhythm steady", "muscle_group": "full body"},
                        {"name": "Mountain climbers", "sets": 3, "reps": "20 seconds", "rest_seconds": 40, "instructions": "Fast alternating legs", "muscle_group": "core"}
                    ],
                    "duration_minutes": daily_duration,
                    "warmup": "5 minutes of light jogging in place",
                    "cooldown": "5 minutes of walking and deep breathing"
                },
                "thursday": {
                    "focus": "Upper Body", 
                    "description": "Focus on back and biceps", 
                    "rest_day": False,
                    "exercises": [
                        {"name": "Pull-ups or rows", "sets": 3, "reps": "8-12", "rest_seconds": 90, "instructions": "Pull with control", "muscle_group": "back"},
                        {"name": "Planks", "sets": 3, "reps": "30 seconds", "rest_seconds": 60, "instructions": "Keep body straight", "muscle_group": "core"}
                    ],
                    "duration_minutes": daily_duration,
                    "warmup": "5 minutes of arm and back movement",
                    "cooldown": "5 minutes of upper body stretching"
                },
                "friday": {
                    "focus": "Full Body", 
                    "description": "Complete body workout", 
                    "rest_day": False,
                    "exercises": [
                        {"name": "Burpees", "sets": 3, "reps": "8-10", "rest_seconds": 90, "instructions": "Full body movement", "muscle_group": "full body"},
                        {"name": "Plank to push-up", "sets": 3, "reps": "5-8", "rest_seconds": 60, "instructions": "Smooth transition", "muscle_group": "full body"}
                    ],
                    "duration_minutes": daily_duration,
                    "warmup": "5 minutes of full body movement",
                    "cooldown": "5 minutes of full body stretching"
                },
                "saturday": {
                    "focus": "Active Recovery", 
                    "description": "Light movement and stretching", 
                    "rest_day": False,
                    "exercises": [
                        {"name": "Gentle yoga flow", "sets": 1, "reps": "15 minutes", "rest_seconds": 0, "instructions": "Focus on breathing", "muscle_group": "flexibility"},
                        {"name": "Walking", "sets": 1, "reps": "15 minutes", "rest_seconds": 0, "instructions": "Light pace", "muscle_group": "cardio"}
                    ],
                    "duration_minutes": daily_duration,
                    "warmup": "Light movement and breathing",
                    "cooldown": "Relaxation and stretching"
                },
                "sunday": {
                    "focus": "Rest and Recovery", 
                    "description": "Complete rest day for muscle recovery", 
                    "rest_day": True,
                    "exercises": [],
                    "duration_minutes": 0,
                    "recovery_activities": ["light stretching", "walk", "meditation"]
                }
            },
            "weekly_tips": [
                "Gradually increase intensity each week",
                "Stay hydrated and maintain proper nutrition",
                "Ensure adequate sleep for muscle recovery"
            ],
            "error": f"OpenAI generation failed: {str(e)}"
        }


def get_workout_goal_suggestions() -> List[str]:
    """Return a list of common workout goal suggestions for the UI."""
    return [
        "Build muscle and strength",
        "Lose weight and burn fat", 
        "Improve cardiovascular fitness",
        "Increase flexibility and mobility",
        "Build endurance and stamina",
        "Tone and sculpt body",
        "Improve athletic performance",
        "General fitness and health",
        "Stress relief and mental wellness",
        "Rehabilitation and injury recovery"
    ]