import torch.nn as nn


class Model(nn.Module):
    def __init__(self, configs):
        super(Model, self).__init__()

        input_dim = configs.enc_in * configs.seq_len
        self.task_name = configs.task_name
        self.pred_len = configs.pred_len

        if configs.task_name == 'long_term_forecast' or configs.task_name == 'short_term_forecast':
            output_size = configs.c_out
        elif configs.task_name == 'classification':
            output_size = configs.c_out
        else:
            raise ValueError('task_name should be forecast or classification')

        # Adjusted output size to account for prediction length
        adjusted_output_size = output_size * self.pred_len

        # Defining the architecture of the model
        self.layers = nn.Sequential(
            nn.Linear(input_dim, configs.d_model),
            nn.ReLU(),
            nn.Linear(configs.d_model, configs.d_model // 2),
            nn.ReLU(),
            nn.Linear(configs.d_model // 2, adjusted_output_size)
        )

    def forecast(self, x):
        x = x.view(x.size(0), -1)
        out = self.layers(x)
        # Reshape output to (batch_size, pred_len, output_size)
        out = out.view(x.size(0), self.pred_len, -1)
        return out

    def classification(self, x):
        x = x.view(x.size(0), -1)
        out = self.layers(x)
        # For classification, reshape if necessary or handle accordingly
        return out

    def forward(self, x_enc, x_mark_enc, x_dec, x_mark_dec, mask=None):
        if self.task_name == 'long_term_forecast' or self.task_name == 'short_term_forecast':
            return self.forecast(x_enc)
        elif self.task_name == 'classification':
            return self.classification(x_enc)
        else:
            raise ValueError('Task name not recognized')
