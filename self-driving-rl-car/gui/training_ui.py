import pygame
import math
from collections import deque


class TrainingUI:
    """
    Training UI with controls, statistics, and real-time graphs.
    """
    
    def __init__(self, screen, width=1000, height=800):
        """
        Initialize training UI.
        
        Args:
            screen: Pygame screen surface
            width (int): Screen width
            height (int): Screen height
        """
        self.screen = screen
        self.width = width
        self.height = height
        
        # Fonts
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        
        # UI Layout
        self.panel_width = 250
        self.panel_x = width - self.panel_width
        self.graph_height = 150
        
        # Training state
        self.is_training = False
        self.training_speed = 1
        
        # Statistics
        self.episode_rewards = deque(maxlen=500)
        self.episode_losses = deque(maxlen=500)
        self.current_episode = 0
        self.current_reward = 0.0
        self.best_reward = float('-inf')
        self.avg_reward = 0.0
        self.epsilon = 1.0
        self.loss = 0.0
        
        # Buttons
        self.buttons = self._create_buttons()
        
    def _create_buttons(self):
        """Create UI buttons."""
        buttons = {}
        
        panel_x = self.panel_x
        button_width = self.panel_width - 20
        button_height = 35
        x_offset = 10
        y_start = 10
        y_spacing = 45
        
        # Start/Pause button
        buttons['start_pause'] = {
            'rect': pygame.Rect(panel_x + x_offset, y_start, button_width, button_height),
            'text': 'Start Training',
            'color': (50, 200, 50),
            'hover_color': (70, 220, 70)
        }
        
        # Stop button
        buttons['stop'] = {
            'rect': pygame.Rect(panel_x + x_offset, y_start + y_spacing, button_width, button_height),
            'text': 'Stop Training',
            'color': (200, 50, 50),
            'hover_color': (220, 70, 70)
        }
        
        # Save button
        buttons['save'] = {
            'rect': pygame.Rect(panel_x + x_offset, y_start + y_spacing * 2, button_width, button_height),
            'text': 'Save Model',
            'color': (50, 50, 200),
            'hover_color': (70, 70, 220)
        }
        
        # Load button
        buttons['load'] = {
            'rect': pygame.Rect(panel_x + x_offset, y_start + y_spacing * 3, button_width, button_height),
            'text': 'Load Model',
            'color': (200, 150, 50),
            'hover_color': (220, 170, 70)
        }
        
        return buttons
    
    def handle_click(self, pos):
        """
        Handle mouse click on UI elements.
        
        Args:
            pos (tuple): Mouse position (x, y)
            
        Returns:
            str: Button name if clicked, None otherwise
        """
        for button_name, button in self.buttons.items():
            if button['rect'].collidepoint(pos):
                return button_name
        return None
    
    def toggle_training(self):
        """Toggle training state."""
        self.is_training = not self.is_training
        if self.is_training:
            self.buttons['start_pause']['text'] = 'Pause Training'
            self.buttons['start_pause']['color'] = (200, 150, 50)
        else:
            self.buttons['start_pause']['text'] = 'Resume Training'
            self.buttons['start_pause']['color'] = (50, 200, 50)
    
    def stop_training(self):
        """Stop training."""
        self.is_training = False
        self.buttons['start_pause']['text'] = 'Start Training'
        self.buttons['start_pause']['color'] = (50, 200, 50)
    
    def update_stats(self, episode, reward, epsilon, loss=None):
        """
        Update training statistics.
        
        Args:
            episode (int): Current episode number
            reward (float): Episode reward
            epsilon (float): Current epsilon value
            loss (float): Training loss
        """
        self.current_episode = episode
        self.current_reward = reward
        self.epsilon = epsilon
        
        if loss is not None:
            self.loss = loss
            self.episode_losses.append(loss)
        
        self.episode_rewards.append(reward)
        
        # Update best reward
        if reward > self.best_reward:
            self.best_reward = reward
        
        # Calculate average reward (last 100 episodes)
        if len(self.episode_rewards) > 0:
            recent_rewards = list(self.episode_rewards)[-100:]
            self.avg_reward = sum(recent_rewards) / len(recent_rewards)
    
    def draw(self, cars=None, draw_sensors=True):
        """
        Draw the training UI.
        
        Args:
            cars (list): List of cars to visualize
            draw_sensors (bool): Whether to draw sensor rays
        """
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw control panel background
        panel_rect = pygame.Rect(self.panel_x, 0, self.panel_width, self.height)
        pygame.draw.rect(self.screen, (40, 40, 40), panel_rect)
        pygame.draw.line(self.screen, (80, 80, 80), (self.panel_x, 0), (self.panel_x, self.height), 2)
        
        # Draw buttons
        for button_name, button in self.buttons.items():
            color = button['hover_color'] if button['rect'].collidepoint(mouse_pos) else button['color']
            pygame.draw.rect(self.screen, color, button['rect'], border_radius=5)
            pygame.draw.rect(self.screen, (255, 255, 255), button['rect'], 2, border_radius=5)
            
            text_surf = self.font_small.render(button['text'], True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=button['rect'].center)
            self.screen.blit(text_surf, text_rect)
        
        # Draw statistics
        stats_y = 200
        stats_x = self.panel_x + 10
        line_height = 25
        
        stats = [
            f"Episode: {self.current_episode}",
            f"Reward: {self.current_reward:.2f}",
            f"Avg (100): {self.avg_reward:.2f}",
            f"Best: {self.best_reward:.2f}",
            f"Epsilon: {self.epsilon:.3f}",
            f"Loss: {self.loss:.4f}",
            f"Speed: {self.training_speed}x",
        ]
        
        # Draw stats title
        title_surf = self.font_medium.render("Statistics", True, (255, 255, 100))
        self.screen.blit(title_surf, (stats_x, stats_y - 30))
        
        for i, stat in enumerate(stats):
            text_surf = self.font_small.render(stat, True, (255, 255, 255))
            self.screen.blit(text_surf, (stats_x, stats_y + i * line_height))
        
        # Draw reward graph
        self._draw_graph(
            data=list(self.episode_rewards),
            x=10,
            y=self.height - self.graph_height - 10,
            width=self.panel_x - 20,
            height=self.graph_height,
            title="Episode Rewards",
            color=(100, 200, 100)
        )
        
        # Draw training status indicator
        if self.is_training:
            status_text = "TRAINING"
            status_color = (50, 255, 50)
        else:
            status_text = "PAUSED"
            status_color = (255, 150, 50)
        
        status_surf = self.font_large.render(status_text, True, status_color)
        status_rect = status_surf.get_rect(center=(self.panel_x + self.panel_width // 2, self.height - 30))
        self.screen.blit(status_surf, status_rect)
    
    def _draw_graph(self, data, x, y, width, height, title, color):
        """
        Draw a line graph.
        
        Args:
            data (list): Data points to plot
            x, y (int): Graph position
            width, height (int): Graph dimensions
            title (str): Graph title
            color (tuple): Line color (R, G, B)
        """
        # Draw background
        graph_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (30, 30, 30), graph_rect)
        pygame.draw.rect(self.screen, (80, 80, 80), graph_rect, 2)
        
        # Draw title
        title_surf = self.font_small.render(title, True, (255, 255, 255))
        self.screen.blit(title_surf, (x + 5, y + 5))
        
        if len(data) < 2:
            return
        
        # Calculate scaling
        max_val = max(data) if max(data) > 0 else 1
        min_val = min(data) if min(data) < 0 else 0
        value_range = max_val - min_val if max_val != min_val else 1
        
        # Draw data points
        points = []
        for i, value in enumerate(data):
            px = x + (i / max(len(data) - 1, 1)) * width
            py = y + height - ((value - min_val) / value_range) * (height - 30)
            points.append((px, py))
        
        # Draw line
        if len(points) > 1:
            pygame.draw.lines(self.screen, color, False, points, 2)
        
        # Draw moving average (last 50 points)
        if len(data) >= 10:
            avg_points = []
            window = 10
            for i in range(window, len(data)):
                avg_val = sum(data[i-window:i]) / window
                px = x + (i / max(len(data) - 1, 1)) * width
                py = y + height - ((avg_val - min_val) / value_range) * (height - 30)
                avg_points.append((px, py))
            
            if len(avg_points) > 1:
                pygame.draw.lines(self.screen, (255, 255, 100), False, avg_points, 2)
        
        # Draw axis labels
        max_text = self.font_small.render(f"{max_val:.1f}", True, (200, 200, 200))
        min_text = self.font_small.render(f"{min_val:.1f}", True, (200, 200, 200))
        self.screen.blit(max_text, (x + width - 50, y + 25))
        self.screen.blit(min_text, (x + width - 50, y + height - 20))
