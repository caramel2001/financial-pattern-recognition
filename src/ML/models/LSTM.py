import torch
import torch.nn as nn


class Model(nn.Module):

    def __init__(self, configs):
        super(Model, self).__init__()

        # Defining the number of layers and the nodes in each layer
        self.hidden_dim = configs.d_model
        self.num_layers = configs.e_layers
        self.task_name = configs.task_name
        self.pred_len = configs.pred_len
        if configs.task_name == 'long_term_forecast' or configs.task_name == 'short_term_forecast':
            output_size = configs.c_out
        elif configs.task_name == 'classification':
            output_size = configs.c_out
        else:
            raise ValueError('task_name should be forecast or classification')
        # LSTM layers
        self.lstm = nn.LSTM(
            configs.dec_in, configs.d_model, self.num_layers, batch_first=True, dropout=configs.dropout
        )

        # Fully connected layer
        self.fc = nn.Linear(configs.d_model, output_size * self.pred_len)

    def forecast(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim, device=x.device).requires_grad_()
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim, device=x.device).requires_grad_()

        out, (hn, cn) = self.lstm(x, (h0.detach(), c0.detach()))

        # Convert the final state to our desired output shape
        # Reshape to (batch_size, pred_len, output_size)
        out = self.fc(out[:, -1, :])
        out = out.view(x.size(0), self.pred_len, -1)
        return out

    def classification(self, x):
        # Initializing hidden state for first input with zeros
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim, device=x.device).requires_grad_()

        # Initializing cell state for first input with zeros
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim, device=x.device).requires_grad_()

        # We need to detach as we are doing truncated backpropagation through time (BPTT)
        # If we don't, we'll backprop all the way to the start even after going through another batch
        # Forward propagation by passing in the input, hidden state, and cell state into the model
        out, (hn, cn) = self.lstm(x, (h0.detach(), c0.detach()))

        # Reshaping the outputs in the shape of (batch_size, seq_length, hidden_size)
        # so that it can fit into the fully connected layer
        out = out[:, -1, :]

        # Convert the final state to our desired output shape (batch_size, output_dim)
        out = self.fc(out)
        return out

    def forward(self, x_enc, x_mark_enc, x_dec, x_mark_dec, mask=None):
        if self.task_name == 'long_term_forecast' or self.task_name == 'short_term_forecast':
            return self.forecast(x_enc)
        elif self.task_name == 'classification':
            return self.classification(x_enc)
        else:
            raise ValueError('Task name not recognized')
