import numpy as np
import math
from simulation.car import Car
from simulation.world import CollisionMap


class CarEnvironment:
    """
    Environment wrapper for training self-driving cars with reinforcement learning.
    Supports multiple cars training in parallel.
    """
    
    # Define discrete actions
    # [throttle, steering]
    ACTIONS = [
        (0.5, 0.0),    # 0: Forward
        (0.5, -0.5),   # 1: Forward-Left
        (0.5, 0.5),    # 2: Forward-Right
        (0.0, -0.5),   # 3: Left (no throttle)
        (0.0, 0.5),    # 4: Right (no throttle)
    ]
    
    def __init__(self, map_path, num_cars=1, start_positions=None):
        """
        Initialize environment.
        
        Args:
            map_path (str): Path to map image
            num_cars (int): Number of cars to train simultaneously
            start_positions (list): List of (angle, x, y) tuples for starting positions
        """
        self.collision_map = CollisionMap(map_path)
        self.num_cars = num_cars
        
        # Default starting positions
        if start_positions is None:
            start_positions = [(math.pi / 2, 120, 120)] * num_cars
        
        self.start_positions = start_positions
        
        # Create cars
        self.cars = []
        for i in range(num_cars):
            angle, x, y = start_positions[i % len(start_positions)]
            car = Car(self.collision_map, angle, x, y)
            self.cars.append(car)
        
        # Track episode statistics
        self.episode_steps = [0] * num_cars
        self.episode_distances = [0.0] * num_cars
        self.prev_positions = [(car.x, car.y) for car in self.cars]
        
    def reset(self, car_idx=None):
        """
        Reset environment for a specific car or all cars.
        
        Args:
            car_idx (int): Index of car to reset (None = reset all)
            
        Returns:
            np.array or list: Initial state(s)
        """
        if car_idx is None:
            # Reset all cars
            states = []
            for i, car in enumerate(self.cars):
                angle, x, y = self.start_positions[i % len(self.start_positions)]
                car.reset(angle, x, y)
                self.episode_steps[i] = 0
                self.episode_distances[i] = 0.0
                self.prev_positions[i] = (car.x, car.y)
                states.append(self._get_state(i))
            return states
        else:
            # Reset specific car
            angle, x, y = self.start_positions[car_idx % len(self.start_positions)]
            self.cars[car_idx].reset(angle, x, y)
            self.episode_steps[car_idx] = 0
            self.episode_distances[car_idx] = 0.0
            self.prev_positions[car_idx] = (self.cars[car_idx].x, self.cars[car_idx].y)
            return self._get_state(car_idx)
    
    def step(self, car_idx, action_idx):
        """
        Execute one step in the environment for a specific car.
        
        Args:
            car_idx (int): Index of car
            action_idx (int): Action index
            
        Returns:
            tuple: (next_state, reward, done, info)
        """
        car = self.cars[car_idx]
        
        # Get action
        throttle, steer = self.ACTIONS[action_idx]
        
        # Store previous position
        prev_x, prev_y = car.x, car.y
        prev_speed = car.speed
        
        # Execute action
        success = car.step(throttle, steer)
        
        # Calculate distance traveled
        distance = math.sqrt((car.x - prev_x)**2 + (car.y - prev_y)**2)
        self.episode_distances[car_idx] += distance
        self.episode_steps[car_idx] += 1
        
        # Get new state
        next_state = self._get_state(car_idx)
        
        # Calculate reward
        reward, done = self._calculate_reward(car_idx, success, distance, car.speed)
        
        # Info dictionary
        info = {
            'distance': self.episode_distances[car_idx],
            'steps': self.episode_steps[car_idx],
            'speed': car.speed
        }
        
        return next_state, reward, done, info
    
    def _get_state(self, car_idx):
        """
        Get normalized state representation for a car.
        
        Args:
            car_idx (int): Index of car
            
        Returns:
            np.array: State vector [sensor1, sensor2, ..., sensor5, speed, sin(angle), cos(angle)]
        """
        car = self.cars[car_idx]
        
        # Get sensor readings (5 sensors)
        sensors = car.sensors()
        
        # Normalize sensors (0-200 range -> 0-1)
        normalized_sensors = [s / 200.0 for s in sensors]
        
        # Normalize speed (0-5 range -> 0-1)
        normalized_speed = car.speed / car.max_speed
        
        # Angle as sin/cos (already in -1 to 1 range)
        angle_sin = math.sin(car.angle)
        angle_cos = math.cos(car.angle)
        
        # State vector: [5 sensors, speed, sin(angle), cos(angle)]
        state = np.array(normalized_sensors + [normalized_speed, angle_sin, angle_cos], dtype=np.float32)
        
        return state
    
    def _calculate_reward(self, car_idx, success, distance, speed):
        """
        Calculate reward for the current step.
        
        Args:
            car_idx (int): Index of car
            success (bool): Whether the car successfully moved
            distance (float): Distance traveled this step
            speed (float): Current speed
            
        Returns:
            tuple: (reward, done)
        """
        done = False
        
        # Collision penalty
        if not success:
            reward = -10.0
            done = True
            return reward, done
        
        # Base reward for staying alive
        reward = 0.1
        
        # Reward for distance traveled
        reward += distance * 2.0
        
        # Reward for maintaining speed
        reward += speed * 0.5
        
        # Check if sensors indicate good positioning (not too close to walls)
        sensors = self.cars[car_idx].sensors()
        min_sensor = min(sensors)
        
        # Bonus for staying away from walls
        if min_sensor > 50:
            reward += 0.5
        elif min_sensor < 20:
            reward -= 0.3  # Penalty for being too close to walls
        
        # Episode timeout (prevent infinite episodes)
        if self.episode_steps[car_idx] > 1000:
            done = True
        
        return reward, done
    
    def get_state_size(self):
        """Get the size of the state space."""
        return 8  # 5 sensors + speed + sin(angle) + cos(angle)
    
    def get_action_size(self):
        """Get the size of the action space."""
        return len(self.ACTIONS)
    
    def get_car(self, car_idx):
        """Get a specific car."""
        return self.cars[car_idx]
    
    def get_all_cars(self):
        """Get all cars."""
        return self.cars
