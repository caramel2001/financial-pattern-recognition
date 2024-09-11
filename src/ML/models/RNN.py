import torch
import torch.nn as nn


class RNN(nn.Module):
    def __init__(self, args):
        super(RNN, self).__init__()
        self.hidden_dim = args.hidden_dim
        self.num_layers = args.num_layers
        self.task_name = args.task_name
        self.pred_len = args.pred_len  # prediction length

        self.rnn = nn.RNN(
            args.input_dim, args.hidden_dim, args.num_layers, batch_first=True, dropout=args.dropout
        )
        self.fc = nn.Linear(args.hidden_dim, args.output_dim)

    def forward(self, x):
        if self.task_name == 'long_term_forecast' or self.task_name == 'short_term_forecast':
            return self.forecast(x)
        elif self.task_name == 'classification':
            return self.classification(x)
        else:
            raise ValueError('task_name should be forecast or classification')

    def forecast(self, x):
        outputs = []
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim, device=x.device).requires_grad_()

        out, h = self.rnn(x, h0.detach())

        out = out[:, -1, :]
        out = self.fc(out)
        outputs.append(out.unsqueeze(1))

        for _ in range(1, self.pred_len):
            out, h = self.rnn(outputs[-1], h.detach())
            out = self.fc(out[:, -1, :])
            outputs.append(out.unsqueeze(1))

        return torch.cat(outputs, dim=1)

    def classification(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim, device=x.device).requires_grad_()
        out, h0 = self.rnn(x, h0.detach())
        out = out[:, -1, :]
        out = self.fc(out)
        return out
