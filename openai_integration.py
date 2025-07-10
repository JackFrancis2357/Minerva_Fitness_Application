import json
import os
from typing import Dict, List, Any

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def generate_weekly_workout_plan(equipment: List[str], daily_duration: int, weekly_goal: str, exercises: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a weekly workout plan using GPT-4o based on user preferences and available exercises."""
    
    # Prepare equipment list for the prompt
    equipment_str = ", ".join(equipment) if equipment else "bodyweight only"
    
    # Prepare exercise database summary for context
    exercise_summary = []
    for exercise in exercises[:20]:  # Limit to first 20 exercises for context
        exercise_summary.append({
            "name": exercise.get("name", ""),
            "type": exercise.get("type", ""),
            "muscle_group": exercise.get("muscle_group", ""),
            "equipment_needed": exercise.get("equipment_needed", [])
        })
    
    prompt = f"""Create a balanced 7-day weekly workout plan with the following specifications:

REQUIREMENTS:
- Available Equipment: {equipment_str}
- Daily Workout Duration: {daily_duration} minutes per session
- Weekly Goal: {weekly_goal}
- Use exercises from the provided database when possible

AVAILABLE EXERCISES (sample):
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
            "rest_day": false
        }},
        "tuesday": {{ ... }},
        "wednesday": {{ ... }},
        "thursday": {{ ... }},
        "friday": {{ ... }},
        "saturday": {{ ... }},
        "sunday": {{
            "focus": "Rest and Recovery",
            "description": "Complete rest day for muscle recovery",
            "rest_day": true
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
- Vary muscle groups and workout types across the week
- Consider the weekly goal when planning intensity and focus
- Keep daily sessions within the specified duration
- Provide practical, actionable advice
- Focus on progressive overload and recovery balance
"""

    try:
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
            max_tokens=2000
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Validate the response structure
        required_keys = ["weekly_goal", "total_weekly_duration", "plan_description", "daily_workouts", "weekly_tips"]
        if not all(key in result for key in required_keys):
            raise ValueError("Invalid response structure from GPT-4o")
        
        return result
        
    except Exception as e:
        # Fallback response if OpenAI fails
        return {
            "weekly_goal": weekly_goal,
            "total_weekly_duration": daily_duration * 6,  # 6 workout days
            "plan_description": f"A balanced weekly plan focused on {weekly_goal.lower()} using {equipment_str}.",
            "daily_workouts": {
                "monday": {"focus": "Upper Body", "description": "Focus on chest, shoulders, and arms", "rest_day": False},
                "tuesday": {"focus": "Lower Body", "description": "Focus on legs and glutes", "rest_day": False},
                "wednesday": {"focus": "Cardio", "description": "Cardiovascular endurance training", "rest_day": False},
                "thursday": {"focus": "Upper Body", "description": "Focus on back and biceps", "rest_day": False},
                "friday": {"focus": "Full Body", "description": "Complete body workout", "rest_day": False},
                "saturday": {"focus": "Active Recovery", "description": "Light movement and stretching", "rest_day": False},
                "sunday": {"focus": "Rest and Recovery", "description": "Complete rest day for muscle recovery", "rest_day": True}
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