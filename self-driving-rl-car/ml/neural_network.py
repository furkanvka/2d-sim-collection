import torch
import torch.nn as nn
import torch.nn.functional as F


class QNetwork(nn.Module):
    """
    Q-Network for Deep Q-Learning.
    Maps state to Q-values for each action.
    """
    
    def __init__(self, state_size, action_size, hidden_sizes=[64, 64], seed=42):
        """
        Initialize Q-Network.
        
        Args:
            state_size (int): Dimension of state space
            action_size (int): Dimension of action space
            hidden_sizes (list): List of hidden layer sizes
            seed (int): Random seed
        """
        super(QNetwork, self).__init__()
        torch.manual_seed(seed)
        
        self.state_size = state_size
        self.action_size = action_size
        
        # Build network layers
        layers = []
        input_size = state_size
        
        for hidden_size in hidden_sizes:
            layers.append(nn.Linear(input_size, hidden_size))
            layers.append(nn.ReLU())
            input_size = hidden_size
        
        # Output layer
        layers.append(nn.Linear(input_size, action_size))
        
        self.network = nn.Sequential(*layers)
        
    def forward(self, state):
        """
        Forward pass through the network.
        
        Args:
            state (torch.Tensor): State tensor
            
        Returns:
            torch.Tensor: Q-values for each action
        """
        return self.network(state)
