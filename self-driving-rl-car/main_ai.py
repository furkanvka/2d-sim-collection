import pygame
import argparse
import os
import math

from ml.environment import CarEnvironment
from ml.dqn_agent import DQNAgent
from gui.renderer import Renderer


def main():
    """Run trained AI agent."""
    parser = argparse.ArgumentParser(description='Run trained RL agent')
    parser.add_argument('--model', type=str, default='models/final_model.pth', help='Path to model file')
    parser.add_argument('--map', type=str, default='map.png', help='Path to map image')
    
    args = parser.parse_args()
    
    # Check if model exists
    if not os.path.exists(args.model):
        print(f"Error: Model file not found: {args.model}")
        print("Please train a model first using main_train.py")
        return
    
    # Initialize pygame
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    
    # Create renderer
    renderer = Renderer(args.map, WIDTH, HEIGHT, fps=60)
    
    # Create environment with single car
    env = CarEnvironment(args.map, num_cars=1)
    
    # Create agent and load model
    state_size = env.get_state_size()
    action_size = env.get_action_size()
    agent = DQNAgent(state_size, action_size, hidden_sizes=[128, 64])
    
    print(f"Loading model: {args.model}")
    agent.load(args.model)
    agent.epsilon = 0.0  # No exploration, only exploitation
    
    print("AI agent loaded successfully!")
    print("Press R to reset, ESC to quit")
    
    # Reset environment
    state = env.reset(car_idx=0)
    car = env.get_car(0)
    
    clock = pygame.time.Clock()
    running = True
    total_reward = 0.0
    steps = 0
    
    while running:
        clock.tick(60)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    # Reset
                    state = env.reset(car_idx=0)
                    total_reward = 0.0
                    steps = 0
                    print("Environment reset")
        
        # Get action from agent
        action = agent.act(state, epsilon=0.0)
        
        # Take step
        next_state, reward, done, info = env.step(0, action)
        total_reward += reward
        steps += 1
        
        # Update state
        state = next_state
        
        # Reset if done
        if done:
            print(f"Episode finished! Steps: {steps}, Total Reward: {total_reward:.2f}")
            state = env.reset(car_idx=0)
            total_reward = 0.0
            steps = 0
        
        # Render
        renderer.render(car, draw_sensors=True)
        
        # Display stats
        font = pygame.font.Font(None, 24)
        stats_text = [
            f"Steps: {steps}",
            f"Reward: {total_reward:.2f}",
            f"Speed: {car.speed:.2f}",
        ]
        
        for i, text in enumerate(stats_text):
            text_surf = font.render(text, True, (255, 255, 255))
            # Draw background for text
            bg_rect = text_surf.get_rect(topleft=(10, 10 + i * 30))
            bg_rect.inflate_ip(10, 5)
            pygame.draw.rect(renderer.screen, (0, 0, 0, 180), bg_rect)
            renderer.screen.blit(text_surf, (10, 10 + i * 30))
        
        pygame.display.flip()
    
    pygame.quit()
    print("AI demo ended")


if __name__ == "__main__":
    main()
