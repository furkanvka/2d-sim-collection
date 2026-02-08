import pygame
import argparse
import os
import math
from datetime import datetime

from ml.environment import CarEnvironment
from ml.dqn_agent import DQNAgent
from gui.training_ui import TrainingUI
from gui.renderer import Renderer


class Trainer:
    """Main training class supporting both GUI and headless modes."""
    
    def __init__(self, map_path, num_cars=1, use_gui=True, training_speed=1):
        """
        Initialize trainer.
        
        Args:
            map_path (str): Path to map image
            num_cars (int): Number of cars to train simultaneously
            use_gui (bool): Whether to use GUI
            training_speed (int): Training speed multiplier (GUI only)
        """
        self.map_path = map_path
        self.num_cars = num_cars
        self.use_gui = use_gui
        self.training_speed = training_speed
        
        # Create environment
        self.env = CarEnvironment(map_path, num_cars=num_cars)
        
        # Create agent
        state_size = self.env.get_state_size()
        action_size = self.env.get_action_size()
        self.agent = DQNAgent(state_size, action_size, hidden_sizes=[128, 64])
        
        # GUI components
        self.renderer = None
        self.training_ui = None
        self.screen = None
        
        if use_gui:
            pygame.init()
            self.width = 1000
            self.height = 800
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("RL Car Training")
            
            self.renderer = Renderer(map_path, self.width, self.height, fps=60)
            self.training_ui = TrainingUI(self.screen, self.width, self.height)
            self.training_ui.training_speed = training_speed
        
        # Training state
        self.is_training = False
        self.total_episodes = 0
        self.save_dir = "models"
        os.makedirs(self.save_dir, exist_ok=True)
        
    def train(self, num_episodes=1000):
        """
        Train the agent.
        
        Args:
            num_episodes (int): Number of episodes to train
        """
        print(f"Starting training for {num_episodes} episodes...")
        print(f"Mode: {'GUI' if self.use_gui else 'Headless'}")
        print(f"Number of cars: {self.num_cars}")
        
        for episode in range(num_episodes):
            self.total_episodes = episode + 1
            
            # Reset environment for all cars
            states = self.env.reset()
            episode_rewards = [0.0] * self.num_cars
            dones = [False] * self.num_cars
            steps = 0
            
            while not all(dones):
                steps += 1
                
                # Handle GUI events
                if self.use_gui:
                    if not self._handle_events():
                        return  # User closed window
                    
                    # Wait if paused
                    while not self.training_ui.is_training and self.use_gui:
                        if not self._handle_events():
                            return
                        pygame.time.wait(100)
                
                # Step each car
                for car_idx in range(self.num_cars):
                    if dones[car_idx]:
                        continue
                    
                    # Select action
                    action = self.agent.act(states[car_idx])
                    
                    # Take step
                    next_state, reward, done, info = self.env.step(car_idx, action)
                    
                    # Store experience and learn
                    self.agent.step(states[car_idx], action, reward, next_state, done)
                    
                    # Update state and reward
                    states[car_idx] = next_state
                    episode_rewards[car_idx] += reward
                    dones[car_idx] = done
                
                # Render if using GUI
                if self.use_gui and steps % self.training_speed == 0:
                    self._render()
            
            # Episode finished
            avg_reward = sum(episode_rewards) / self.num_cars
            self.agent.update_epsilon()
            
            # Update UI
            if self.use_gui:
                self.training_ui.update_stats(
                    episode=self.total_episodes,
                    reward=avg_reward,
                    epsilon=self.agent.epsilon,
                    loss=0.0  # Loss is tracked internally
                )
            
            # Print progress
            if (episode + 1) % 10 == 0:
                print(f"Episode {episode + 1}/{num_episodes} | "
                      f"Avg Reward: {avg_reward:.2f} | "
                      f"Epsilon: {self.agent.epsilon:.3f}")
            
            # Save best model
            if (episode + 1) % 50 == 0:
                self.save_model(f"checkpoint_ep{episode + 1}.pth")
        
        print("Training completed!")
        self.save_model("final_model.pth")
    
    def _handle_events(self):
        """
        Handle pygame events.
        
        Returns:
            bool: False if should quit, True otherwise
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                button = self.training_ui.handle_click(event.pos)
                
                if button == 'start_pause':
                    self.training_ui.toggle_training()
                    if not self.training_ui.is_training:
                        print("Training paused")
                    else:
                        print("Training resumed")
                
                elif button == 'stop':
                    print("Training stopped by user")
                    return False
                
                elif button == 'save':
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"manual_save_{timestamp}.pth"
                    self.save_model(filename)
                    print(f"Model saved: {filename}")
                
                elif button == 'load':
                    # Try to load the most recent model
                    models = [f for f in os.listdir(self.save_dir) if f.endswith('.pth')]
                    if models:
                        latest_model = max(models, key=lambda x: os.path.getctime(os.path.join(self.save_dir, x)))
                        self.load_model(latest_model)
                        print(f"Model loaded: {latest_model}")
                    else:
                        print("No models found to load")
            
            if event.type == pygame.KEYDOWN:
                # Speed control with number keys
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                    self.training_speed = event.key - pygame.K_0
                    self.training_ui.training_speed = self.training_speed
                    print(f"Training speed: {self.training_speed}x")
        
        return True
    
    def _render(self):
        """Render the training visualization."""
        # Draw map
        self.renderer.draw_world()
        
        # Draw all cars
        for car in self.env.get_all_cars():
            self.renderer.draw_car(car)
            self.renderer.draw_sensors(car)
        
        # Draw UI
        self.training_ui.draw()
        
        pygame.display.flip()
        self.renderer.clock.tick(60)
    
    def save_model(self, filename):
        """Save model to file."""
        filepath = os.path.join(self.save_dir, filename)
        self.agent.save(filepath)
    
    def load_model(self, filename):
        """Load model from file."""
        filepath = os.path.join(self.save_dir, filename)
        if os.path.exists(filepath):
            self.agent.load(filepath)
        else:
            print(f"Model file not found: {filepath}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Train RL agent for self-driving car')
    parser.add_argument('--gui', action='store_true', help='Use GUI mode (default: headless)')
    parser.add_argument('--no-gui', dest='gui', action='store_false', help='Use headless mode')
    parser.add_argument('--cars', type=int, default=1, help='Number of cars to train simultaneously')
    parser.add_argument('--episodes', type=int, default=500, help='Number of training episodes')
    parser.add_argument('--speed', type=int, default=1, help='Training speed multiplier (GUI only)')
    parser.add_argument('--map', type=str, default='map.png', help='Path to map image')
    parser.set_defaults(gui=True)
    
    args = parser.parse_args()
    
    # Create trainer
    trainer = Trainer(
        map_path=args.map,
        num_cars=args.cars,
        use_gui=args.gui,
        training_speed=args.speed
    )
    
    # Start training UI if using GUI
    if args.gui:
        trainer.training_ui.toggle_training()  # Auto-start training
    else:
        trainer.is_training = True
    
    # Train
    try:
        trainer.train(num_episodes=args.episodes)
    except KeyboardInterrupt:
        print("\nTraining interrupted by user")
    finally:
        if args.gui:
            pygame.quit()


if __name__ == "__main__":
    main()
