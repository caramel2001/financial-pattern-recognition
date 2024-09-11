import torch
import torch.nn as nn


class GRU(nn.Module):

    def __init__(self, args):
        super(GRU, self).__init__()

        # Defining the number of layers and the nodes in each layer
        self.num_layers = args.num_layers
        self.hidden_dim = args.hidden_dim
        self.pred_len = args.pred_len
        # GRU layers
        self.gru = nn.GRU(
            args.input_dim, args.hidden_dim, args.num_layers, batch_first=True, dropout=args.dropout
        )

        # Fully connected layer
        self.fc = nn.Linear(args.hidden_dim, args.output_dim * args.pred_len)

    def forecasting(self, x):
        """The forward method takes input tensor x and does forward propagation

        Args:
            x (torch.Tensor): The input tensor of the shape (batch size, sequence length, input_dim)

        Returns:
            torch.Tensor: The output tensor of the shape (batch size, output_dim)

        """
        # Initializing hidden state for first input with zeros
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim, device=x.device).requires_grad_()

        # Forward propagation by passing in the input and hidden state into the model
        out, _ = self.gru(x, h0.detach())

        # Reshaping the outputs in the shape of (batch_size, seq_length, hidden_size)
        # so that it can fit into the fully connected layer
        out = out[:, -1, :]

        # Convert the final state to our desired output shape (batch_size, output_dim)
        out = self.fc(out)
        out = out.view(-1, self.pred_len, 1)
        return out

    def classification(self, x):
        """The forward method takes input tensor x and does forward propagation

        Args:
            x (torch.Tensor): The input tensor of the shape (batch size, sequence length, input_dim)

        Returns:
            torch.Tensor: The output tensor of the shape (batch size, output_dim)

        """
        # Initializing hidden state for first input with zeros
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim, device=x.device).requires_grad_()

        # Forward propagation by passing in the input and hidden state into the model
        out, _ = self.gru(x, h0.detach())

        # Reshaping the outputs in the shape of (batch_size, seq_length, hidden_size)
        # so that it can fit into the fully connected layer
        out = out[:, -1, :]

        # Convert the final state to our desired output shape (batch_size, output_dim)
        out = self.fc(out)
        return out

    def forward(self, x):
        if self.task_name == 'long_term_forecast' or self.task_name == 'short_term_forecast':
            return self.forecast(x)
        elif self.task_name == 'classification':
            return self.classification(x)
        else:
            raise ValueError('Task name not recognized')
