import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim
from collections import deque, namedtuple
import random

from ml.neural_network import QNetwork


class ReplayBuffer:
    """Experience Replay Buffer for storing and sampling transitions."""
    
    def __init__(self, buffer_size, batch_size, seed=42):
        """
        Initialize replay buffer.
        
        Args:
            buffer_size (int): Maximum size of buffer
            batch_size (int): Size of training batch
            seed (int): Random seed
        """
        self.memory = deque(maxlen=buffer_size)
        self.batch_size = batch_size
        self.experience = namedtuple("Experience", 
                                     field_names=["state", "action", "reward", "next_state", "done"])
        random.seed(seed)
        
    def add(self, state, action, reward, next_state, done):
        """Add a new experience to memory."""
        e = self.experience(state, action, reward, next_state, done)
        self.memory.append(e)
        
    def sample(self):
        """Randomly sample a batch of experiences from memory."""
        experiences = random.sample(self.memory, k=self.batch_size)
        
        states = torch.from_numpy(np.vstack([e.state for e in experiences if e is not None])).float()
        actions = torch.from_numpy(np.vstack([e.action for e in experiences if e is not None])).long()
        rewards = torch.from_numpy(np.vstack([e.reward for e in experiences if e is not None])).float()
        next_states = torch.from_numpy(np.vstack([e.next_state for e in experiences if e is not None])).float()
        dones = torch.from_numpy(np.vstack([e.done for e in experiences if e is not None]).astype(np.uint8)).float()
        
        return (states, actions, rewards, next_states, dones)
    
    def __len__(self):
        """Return the current size of internal memory."""
        return len(self.memory)


class DQNAgent:
    """Deep Q-Network Agent for reinforcement learning."""
    
    def __init__(self, state_size, action_size, hidden_sizes=[64, 64], 
                 buffer_size=100000, batch_size=64, gamma=0.99, 
                 tau=0.001, lr=0.0005, update_every=4, seed=42):
        """
        Initialize DQN Agent.
        
        Args:
            state_size (int): Dimension of state space
            action_size (int): Dimension of action space
            hidden_sizes (list): Hidden layer sizes for Q-network
            buffer_size (int): Replay buffer size
            batch_size (int): Minibatch size
            gamma (float): Discount factor
            tau (float): Soft update parameter for target network
            lr (float): Learning rate
            update_every (int): How often to update the network
            seed (int): Random seed
        """
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        self.tau = tau
        self.batch_size = batch_size
        self.update_every = update_every
        self.seed = random.seed(seed)
        
        # Q-Network
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.qnetwork_local = QNetwork(state_size, action_size, hidden_sizes, seed).to(self.device)
        self.qnetwork_target = QNetwork(state_size, action_size, hidden_sizes, seed).to(self.device)
        self.optimizer = optim.Adam(self.qnetwork_local.parameters(), lr=lr)
        
        # Replay memory
        self.memory = ReplayBuffer(buffer_size, batch_size, seed)
        
        # Initialize time step (for updating every UPDATE_EVERY steps)
        self.t_step = 0
        
        # Epsilon for epsilon-greedy action selection
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        
    def step(self, state, action, reward, next_state, done):
        """
        Save experience in replay memory and learn if enough samples are available.
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode is done
        """
        # Save experience in replay memory
        self.memory.add(state, action, reward, next_state, done)
        
        # Learn every UPDATE_EVERY time steps
        self.t_step = (self.t_step + 1) % self.update_every
        if self.t_step == 0:
            # If enough samples are available in memory, get random subset and learn
            if len(self.memory) > self.batch_size:
                experiences = self.memory.sample()
                self.learn(experiences)
                
    def act(self, state, epsilon=None):
        """
        Returns action for given state using epsilon-greedy policy.
        
        Args:
            state: Current state
            epsilon: Epsilon value for exploration (if None, uses self.epsilon)
            
        Returns:
            int: Selected action
        """
        if epsilon is None:
            epsilon = self.epsilon
            
        state = torch.from_numpy(state).float().unsqueeze(0).to(self.device)
        
        self.qnetwork_local.eval()
        with torch.no_grad():
            action_values = self.qnetwork_local(state)
        self.qnetwork_local.train()
        
        # Epsilon-greedy action selection
        if random.random() > epsilon:
            return np.argmax(action_values.cpu().data.numpy())
        else:
            return random.choice(np.arange(self.action_size))
            
    def learn(self, experiences):
        """
        Update value parameters using given batch of experience tuples.
        
        Args:
            experiences (Tuple[torch.Tensor]): Tuple of (s, a, r, s', done) tuples
        """
        states, actions, rewards, next_states, dones = experiences
        
        # Move to device
        states = states.to(self.device)
        actions = actions.to(self.device)
        rewards = rewards.to(self.device)
        next_states = next_states.to(self.device)
        dones = dones.to(self.device)
        
        # Get max predicted Q values (for next states) from target model
        Q_targets_next = self.qnetwork_target(next_states).detach().max(1)[0].unsqueeze(1)
        
        # Compute Q targets for current states
        Q_targets = rewards + (self.gamma * Q_targets_next * (1 - dones))
        
        # Get expected Q values from local model
        Q_expected = self.qnetwork_local(states).gather(1, actions)
        
        # Compute loss
        loss = F.mse_loss(Q_expected, Q_targets)
        
        # Minimize the loss
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Update target network
        self.soft_update(self.qnetwork_local, self.qnetwork_target)
        
        return loss.item()
        
    def soft_update(self, local_model, target_model):
        """
        Soft update model parameters.
        θ_target = τ*θ_local + (1 - τ)*θ_target
        
        Args:
            local_model: PyTorch model (weights will be copied from)
            target_model: PyTorch model (weights will be copied to)
        """
        for target_param, local_param in zip(target_model.parameters(), local_model.parameters()):
            target_param.data.copy_(self.tau * local_param.data + (1.0 - self.tau) * target_param.data)
            
    def update_epsilon(self):
        """Decay epsilon for epsilon-greedy exploration."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
    def save(self, filepath):
        """Save model weights."""
        torch.save({
            'qnetwork_local_state_dict': self.qnetwork_local.state_dict(),
            'qnetwork_target_state_dict': self.qnetwork_target.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon
        }, filepath)
        
    def load(self, filepath):
        """Load model weights."""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.qnetwork_local.load_state_dict(checkpoint['qnetwork_local_state_dict'])
        self.qnetwork_target.load_state_dict(checkpoint['qnetwork_target_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
