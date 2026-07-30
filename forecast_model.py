import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torch.utils.data import DataLoader, Dataset

class TimeSeriesDataset(Dataset):
    def __init__(self, data, input_len, output_len):
        self.data = torch.tensor(data, dtype=torch.float32)
        self.input_len = input_len
        self.output_len = output_len
        
    def __len__(self):
        return self.data.size(dim=1) - self.input_len - self.output_len + 1

    def __getitem__(self, idx):
        x = self.data[:-1, idx:idx + self.input_len]
        y = self.data[-1:, idx + self.input_len:idx + self.input_len + self.output_len]
        return x, y

