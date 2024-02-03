import torch
import torch.nn as nn
import torch.optim as optim

# Dummy data
input_size = 10  # Size of the one-hot encoded vectors
sequence_length = 5  # Length of the sequence
hidden_size = 20  # Size of the hidden state
output_size = 2  # Output size

# Generate random one-hot encoded sequences and corresponding targets
X = torch.randint(
    2, (sequence_length, input_size)
).float()  # Random binary one-hot encoded sequences
y = torch.randint(
    2, (sequence_length, output_size)
).float()  # Random binary target sequences


class SimpleRNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(SimpleRNN, self).__init__()

        self.rnn = nn.RNN(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h_0 = torch.zeros(1, x.size(0), hidden_size)  # Initial hidden state
        out, _ = self.rnn(x, h_0)
        out = self.fc(out[:, -1, :])  # Take the output from the last time step
        return out


# Instantiate the model
model = SimpleRNN(input_size, hidden_size, output_size)

criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

num_epochs = 1000

for epoch in range(num_epochs):
    # Forward pass
    outputs = model(X.unsqueeze(0))  # Add batch dimension

    # Compute the loss
    loss = criterion(outputs, y.unsqueeze(0))

    # Backward pass and optimization
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 100 == 0:
        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}")
