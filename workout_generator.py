import json
import random
from typing import List, Dict, Any
import logging

class WorkoutGenerator:
    """Handles workout generation logic based on user preferences."""
    
    def __init__(self):
        """Initialize the workout generator with exercise data."""
        self.exercises = self._load_exercises()
        self.equipment_mapping = {
            'bodyweight': [],
            'dumbbells': ['dumbbell'],
            'kettlebells': ['kettlebell'],
            'resistance_bands': ['resistance_band'],
            'pull_up_bar': ['pull_up_bar'],
            'bench': ['bench'],
            'barbell': ['barbell'],
            'medicine_ball': ['medicine_ball']
        }
    
    def _load_exercises(self) -> List[Dict[str, Any]]:
        """Load exercise data from JSON file."""
        try:
            with open('exercises.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error("exercises.json not found")
            return []
        except json.JSONDecodeError:
            logging.error("Invalid JSON in exercises.json")
            return []
    
    def _calculate_exercise_duration(self, exercise: Dict[str, Any]) -> int:
        """Calculate total duration for an exercise in seconds."""
        duration_per_rep = exercise.get('duration_per_rep_seconds', 3)
        reps_per_set = exercise.get('reps_per_set', 10)
        sets = exercise.get('sets', 3)
        rest_between_sets = exercise.get('rest_between_sets_seconds', 60)
        
        # Total time = (duration per rep * reps per set * sets) + (rest between sets * (sets - 1))
        exercise_time = (duration_per_rep * reps_per_set * sets)
        rest_time = rest_between_sets * (sets - 1)
        
        return exercise_time + rest_time
    
    def _filter_exercises_by_equipment(self, available_equipment: List[str]) -> List[Dict[str, Any]]:
        """Filter exercises based on available equipment."""
        # Convert user equipment selection to equipment needed format
        user_equipment = set()
        for eq in available_equipment:
            if eq in self.equipment_mapping:
                user_equipment.update(self.equipment_mapping[eq])
        
        # Always include bodyweight exercises
        if 'bodyweight' in available_equipment:
            user_equipment.add('')  # Empty string for bodyweight
        
        filtered_exercises = []
        for exercise in self.exercises:
            equipment_needed = set(exercise.get('equipment_needed', []))
            
            # If exercise needs no equipment (bodyweight) or all needed equipment is available
            if not equipment_needed or equipment_needed.issubset(user_equipment):
                filtered_exercises.append(exercise)
        
        return filtered_exercises
    
    def _create_balanced_workout(self, exercises: List[Dict[str, Any]], target_duration_minutes: int) -> Dict[str, Any]:
        """Create a balanced workout plan within the target duration."""
        target_duration_seconds = target_duration_minutes * 60
        selected_exercises = []
        total_duration = 0
        
        # Group exercises by muscle group for balanced selection
        muscle_groups = {}
        for exercise in exercises:
            muscle_group = exercise.get('muscle_group', 'other')
            if muscle_group not in muscle_groups:
                muscle_groups[muscle_group] = []
            muscle_groups[muscle_group].append(exercise)
        
        # Ensure we have a variety of exercise types
        exercise_types = {}
        for exercise in exercises:
            exercise_type = exercise.get('type', 'other')
            if exercise_type not in exercise_types:
                exercise_types[exercise_type] = []
            exercise_types[exercise_type].append(exercise)
        
        # Start with a warm-up exercise if available
        warmup_exercises = [ex for ex in exercises if ex.get('type') == 'cardio' or 'warm' in ex.get('name', '').lower()]
        if warmup_exercises and total_duration < target_duration_seconds:
            warmup = random.choice(warmup_exercises)
            warmup_duration = self._calculate_exercise_duration(warmup)
            if total_duration + warmup_duration <= target_duration_seconds:
                selected_exercises.append(warmup)
                total_duration += warmup_duration
        
        # Add main exercises, rotating through muscle groups
        muscle_group_keys = list(muscle_groups.keys())
        current_group_index = 0
        attempts = 0
        max_attempts = len(exercises) * 2  # Prevent infinite loops
        
        while total_duration < target_duration_seconds * 0.9 and attempts < max_attempts:
            attempts += 1
            
            # Try to select from current muscle group
            if muscle_group_keys:
                current_group = muscle_group_keys[current_group_index % len(muscle_group_keys)]
                available_exercises = [ex for ex in muscle_groups[current_group] 
                                     if ex not in selected_exercises]
                
                if available_exercises:
                    exercise = random.choice(available_exercises)
                    exercise_duration = self._calculate_exercise_duration(exercise)
                    
                    # Check if adding this exercise would exceed target duration
                    if total_duration + exercise_duration <= target_duration_seconds:
                        selected_exercises.append(exercise)
                        total_duration += exercise_duration
                        current_group_index += 1
                    else:
                        # Try to find a shorter exercise
                        shorter_exercises = [ex for ex in available_exercises 
                                           if self._calculate_exercise_duration(ex) <= target_duration_seconds - total_duration]
                        if shorter_exercises:
                            exercise = min(shorter_exercises, key=self._calculate_exercise_duration)
                            exercise_duration = self._calculate_exercise_duration(exercise)
                            selected_exercises.append(exercise)
                            total_duration += exercise_duration
                        break
                else:
                    current_group_index += 1
            else:
                break
        
        # Add cool-down if there's time and space
        if total_duration < target_duration_seconds * 0.95:
            cooldown_exercises = [ex for ex in exercises if ex.get('type') == 'flexibility' or 'stretch' in ex.get('name', '').lower()]
            if cooldown_exercises:
                cooldown = random.choice(cooldown_exercises)
                cooldown_duration = self._calculate_exercise_duration(cooldown)
                if total_duration + cooldown_duration <= target_duration_seconds:
                    selected_exercises.append(cooldown)
                    total_duration += cooldown_duration
        
        return {
            'exercises': selected_exercises,
            'total_duration_minutes': round(total_duration / 60, 1),
            'target_duration_minutes': target_duration_minutes,
            'exercise_count': len(selected_exercises)
        }
    
    def generate_workout(self, equipment: List[str], duration_minutes: int) -> Dict[str, Any]:
        """Generate a complete workout plan."""
        # Filter exercises by available equipment
        available_exercises = self._filter_exercises_by_equipment(equipment)
        
        if not available_exercises:
            return {
                'exercises': [],
                'total_duration_minutes': 0,
                'target_duration_minutes': duration_minutes,
                'exercise_count': 0,
                'error': 'No exercises available for selected equipment'
            }
        
        # Create balanced workout
        workout_plan = self._create_balanced_workout(available_exercises, duration_minutes)
        
        return workout_plan
