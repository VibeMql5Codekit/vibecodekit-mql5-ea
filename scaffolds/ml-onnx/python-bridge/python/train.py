#!/usr/bin/env python3
"""train.py — Train a simple ML model for MQL5 EA signal prediction.

Usage: python train.py --data features.csv --output model.pt
"""
import argparse
import sys
from pathlib import Path


def load_data(data_path: Path):
    """Load CSV features: columns = [open, high, low, close, volume, ..., label]."""
    import numpy as np
    data = np.genfromtxt(data_path, delimiter=",", skip_header=1)
    X = data[:, :-1]
    y = data[:, -1]
    return X, y


def train_model(X, y, epochs: int = 100):
    """Train a simple PyTorch model."""
    import torch
    import torch.nn as nn

    X_t = torch.FloatTensor(X)
    y_t = torch.FloatTensor(y).unsqueeze(1)

    model = nn.Sequential(
        nn.Linear(X.shape[1], 64),
        nn.ReLU(),
        nn.Linear(64, 32),
        nn.ReLU(),
        nn.Linear(32, 1),
        nn.Sigmoid(),
    )

    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.BCELoss()

    for epoch in range(epochs):
        optimizer.zero_grad()
        output = model(X_t)
        loss = criterion(output, y_t)
        loss.backward()
        optimizer.step()
        if (epoch + 1) % 20 == 0:
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {loss.item():.4f}")

    return model


def main() -> int:
    parser = argparse.ArgumentParser(description="Train ML model")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("model.pt"))
    parser.add_argument("--epochs", type=int, default=100)
    args = parser.parse_args()

    if not args.data.exists():
        print(f"Error: {args.data} not found")
        return 1

    X, y = load_data(args.data)
    print(f"Data: {X.shape[0]} samples, {X.shape[1]} features")
    model = train_model(X, y, args.epochs)

    import torch
    torch.save(model, args.output)
    print(f"Model saved: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
