import torch
import torch.nn as nn
import numpy as np

import torch
import torch.nn as nn
import pytorch_lightning as pl
from torch.utils.data import DataLoader
import torch.optim.lr_scheduler as lr_scheduler


class CausalConv1d(torch.nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, dilation=1):
        super(CausalConv1d, self).__init__()
        self.padding = (kernel_size - 1) * dilation
        self.conv1d = torch.nn.Conv1d(
            in_channels,
            out_channels,
            kernel_size,
            padding=self.padding,
            dilation=dilation,
        )

    def forward(self, x):
        x = self.conv1d(x)
        x = x[:, :, : -self.padding]
        return x


class TCNResidualBlock(torch.nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, dilation):
        super(TCNResidualBlock, self).__init__()
        self.causal_conv1 = CausalConv1d(
            in_channels, out_channels, kernel_size, dilation
        )
        self.causal_conv2 = CausalConv1d(
            out_channels, out_channels, kernel_size, dilation
        )
        self.relu = torch.nn.ReLU()
        if in_channels != out_channels:
            self.skip = torch.nn.Conv1d(in_channels, out_channels, 1)
        else:
            self.skip = None

    def forward(self, x):
        residual = x
        x = self.relu(self.causal_conv1(x))
        x = self.relu(self.causal_conv2(x))

        if self.skip is not None:
            residual = self.skip(residual)

        return self.relu(x + residual)


class Model(torch.nn.Module):
    def __init__(self, configs):
        super(Model, self).__init__()
        input_size = configs.dec_in
        self.pred_len = configs.pred_len
        if (
            configs.task_name == "long_term_forecast"
            or configs.task_name == "short_term_forecast"
        ):
            output_size = configs.c_out
        elif configs.task_name == "classification":
            raise ValueError("Classification not supported for TCN")
        else:
            raise ValueError("task_name should be forecast or classification")
        num_channels = [32, 32, 32, 32]
        kernel_size = 5
        dropout = configs.dropout
        self.tcn_layers = torch.nn.ModuleList()
        self.num_levels = len(num_channels)
        self.task_name = configs.task_name
        self.seq_len = configs.seq_len
        for i in range(self.num_levels):
            in_channels = input_size if i == 0 else num_channels[i - 1]
            out_channels = num_channels[i]
            self.tcn_layers.append(
                TCNResidualBlock(in_channels, out_channels, kernel_size, dilation=1)
            )
            self.fc = torch.nn.Linear(num_channels[-1], output_size)
            self.dropout = torch.nn.Dropout(dropout)

    def forecast(self, x):
        x = x.transpose(1, 2)
        for layer in self.tcn_layers:
            x = layer(x)
        # Instead of taking the last element, take the last 'pred_len' elements
        x = x[:, :, -self.pred_len :]
        x = self.dropout(x)
        # Reshape for the fully connected layer
        batch_size, channels, steps = x.shape
        x = x.view(batch_size, -1)
        x = self.fc(x)
        # Reshape back to (batch_size, pred_len, output_size)
        x = x.view(batch_size, self.pred_len, -1)
        return x

    def forward(self, x_enc):
        # print("Shape of input to TCN", x_enc.shape)
        if (
            self.task_name == "long_term_forecast"
            or self.task_name == "short_term_forecast"
        ):
            return self.forecast(x_enc)
        elif self.task_name == "classification":
            return self.classification(x_enc)
        else:
            raise ValueError("task_name should be forecast or classification")
