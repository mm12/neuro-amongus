import torch
import torch.autograd as autograd


class Model(torch.nn.Module):
    def __init__(self):
        super(Model, self).__init__()
        # INPUTS (66)
        # tasks: 10x 2 positiondatas = 10x 2x 3 floats = 60
        # sabotage: 2 positiondatas = 1x 2x 3 floats = 6

        # OUTPUTS (2)
        # velocity: 2 floats = 2

        self.fc1 = torch.nn.Linear(4, 64)

        self.fc2 = torch.nn.Linear(64, 4)

    def forward(self, x):
        # input is batch x 10 x 4 so we need to flatten it
        x = x[:, -1, :]

        x = torch.relu(self.fc1(x))

        x = torch.sigmoid(self.fc2(x))

        return x


class LSTMModel(torch.nn.Module):
    def __init__(self):
        super(LSTMModel, self).__init__()
        # INPUTS (66)
        # tasks: 10x 2 positiondatas = 10x 2x 3 floats = 60
        # sabotage: 2 positiondatas = 1x 2x 3 floats = 6

        # OUTPUTS (2)
        # velocity: 2 floats = 2

        self.hidden_dim = 64
        self.layers = 2

        self.fc1 = torch.nn.Linear(36, self.hidden_dim)

        self.lstm = torch.nn.LSTM(self.hidden_dim, self.hidden_dim, self.layers)

        self.fc2 = torch.nn.Linear(self.hidden_dim, 4)

    def forward(self, x):
        hidden = self.init_hidden(x.shape[1], x.device)

        x = torch.relu(self.fc1(x))

        x, hidden = self.lstm(x, hidden)

        x = x[:, -1, :]

        x = torch.sigmoid(self.fc2(x))

        return x

        # x, (ht, ct) = self.lstm(x, hidden)

        # output = self.fc2(ht[-1])

        # return output

    def init_hidden(self, batch_size, device):
        return (autograd.Variable(torch.randn(self.layers, batch_size, self.hidden_dim, device=device)),
                autograd.Variable(torch.randn(self.layers, batch_size, self.hidden_dim, device=device)))
