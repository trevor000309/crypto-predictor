import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torch.utils.data import DataLoader, Dataset
from database import Database
import pandas as pd

class TimeSeriesDataset(Dataset):
    def __init__(self, data, input_len, output_len):
        self.data = torch.tensor(data, dtype=torch.float32)
        self.input_len = input_len
        self.output_len = output_len
        
    def __len__(self):
        return self.data.size(dim=0) - self.input_len - self.output_len + 1

    def __getitem__(self, idx):
        x = self.data[idx:idx + self.input_len, :-1]
        y = self.data[idx + self.input_len:idx + self.input_len + self.output_len, -1].long()
        return x, y

class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_len, dropout = 0.2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout)
        self.dropout = nn.Dropout(dropout)
        self.output_len = output_len
        self.fc = nn.Linear(hidden_size, output_len * 3)  # 3 classes for each output step

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.dropout(out)
        out = self.fc(out[:, -1, :])  # Take the last time step
        return out.view(-1, self.output_len, 3)  # Reshape to (batch_size, output_len, 3)

INPUT_LEN = 60
OUTPUT_LEN = 5

db = Database()

for symbol in ['BTCUSDT']:
    df = pd.read_sql(
        "SELECT * FROM feature_data WHERE symbol = ? ORDER BY open_time ASC",
        db.conn,
        params = (symbol,)
    )

data = df.drop(columns=["symbol", "open_time"])
data["label"] += 1 

split = int(len(data) * 0.8)

train_data = data.iloc[:split].copy()
val_data = data.iloc[split:].copy()

train_mean = train_data[train_data.columns[:-1]].mean()
train_std = train_data[train_data.columns[:-1]].std()

train_data[train_data.columns[:-1]] = (train_data[train_data.columns[:-1]] - train_mean) / (train_std + 1e-8)
val_data[val_data.columns[:-1]] = (val_data[val_data.columns[:-1]] - train_mean) / (train_std + 1e-8)

train_dataset = TimeSeriesDataset(train_data.values, INPUT_LEN, OUTPUT_LEN)
val_dataset = TimeSeriesDataset(val_data.values, INPUT_LEN, OUTPUT_LEN)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)

model = LSTMModel(input_size=7, hidden_size=64, num_layers=2, output_len=OUTPUT_LEN)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)

def train_epoch(model, loader, optimizer, criterion):
    model.train()
    total_loss = 0.0
    for x, y in loader:
        optimizer.zero_grad()
        pred = model(x)
        loss = criterion(pred.reshape(-1, 3), y.reshape(-1))
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        total_loss += loss.item() * x.size(0)
    return total_loss / len(loader.dataset)

def eval_epoch(model, loader, criterion):
    model.eval()
    total_loss = 0.0
    with torch.no_grad():
        for x, y in loader:
            pred = model(x)
            loss = criterion(pred.reshape(-1, 3), y.reshape(-1))
            total_loss += loss.item() * x.size(0)
    return total_loss / len(loader.dataset)

for epoch in range(1, 31):
    train_loss = train_epoch(model, train_loader, optimizer, criterion)
    val_loss = eval_epoch(model, val_loader, criterion)
    print(f"Epoch {epoch}/30 : Train Loss = {train_loss:.4f}, Val Loss = {val_loss:.4f}")