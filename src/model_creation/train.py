import torch
import torch.nn as nn
import torch.optim as optim
import os
from torchvision.transforms.v2 import *
from torch.utils.data import DataLoader
from dataset import CycloneDataset
from unet import UNet

# -----------------------------
# 1. Setup and configuration
# -----------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
num_epochs = 100
batch_size = 64
learning_rate = 3e-4
checkpoint_dir = "checkpoints"
os.makedirs(checkpoint_dir, exist_ok=True)

# -----------------------------
# 2. Data and model
# -----------------------------
inputs_tr = Compose([
    ToImage(),
    RandomCrop([128, 128]),
    ToDtype(torch.float32),
    Normalize(mean=[127.5], std=[127.5], inplace=True)
])
targets_tr = Compose([
    ToImage(),
    RandomCrop([128, 128]),
    ToDtype(torch.int64),
    Lambda(lambda t: t.squeeze())
])
train_dataset = CycloneDataset(test=False, inputs_transform=inputs_tr, targets_transform=targets_tr)
test_dataset = CycloneDataset(test=True, inputs_transform=inputs_tr, targets_transform=targets_tr)

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

model = UNet(
    in_channels=1,
    out_channels=3,
    features=[64, 128, 256]
).to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

# -----------------------------
# 3. Auto load last checkpoint (if exists)
# -----------------------------
start_epoch = 1
latest_checkpoint = None

# Find latest checkpoint by epoch number
checkpoints = [f for f in os.listdir(checkpoint_dir) if f.endswith(".pth")]
if checkpoints:
    checkpoints.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))  # assumes name like checkpoint_epoch_10.pth
    latest_checkpoint = os.path.join(checkpoint_dir, checkpoints[-1])

if latest_checkpoint:
    print(f"[INFO] Loading checkpoint: {latest_checkpoint}")
    checkpoint = torch.load(latest_checkpoint, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    start_epoch = checkpoint["epoch"] + 1
    print(f"[INFO] Resumed from epoch {checkpoint['epoch']} with train_loss={checkpoint.get('train_loss', 'N/A'):.4f}")
else:
    print("[INFO] No checkpoint found, starting from scratch.")

# -----------------------------
# 4. Training loop
# -----------------------------
for epoch in range(start_epoch, num_epochs + 1):
    model.train()
    running_loss = 0.0

    for batch_idx, (inputs, targets) in enumerate(train_loader):
        inputs, targets = inputs.to(device), targets.to(device)

        # Forward
        outputs = model(inputs)
        # falltens the channels
        loss = criterion(outputs, targets)

        # Backward
        optimizer.zero_grad()
        loss.backward()

        # Debug info: gradient norms
        total_norm = 0
        for p in model.parameters():
            if p.grad is not None:
                total_norm += p.grad.data.norm(2).item()
        if batch_idx % 10 == 0:
            print(f"[DEBUG] Epoch {epoch}, Batch {batch_idx}: Grad Norm={total_norm:.4f}")

        optimizer.step()
        running_loss += loss.item()

    avg_train_loss = running_loss / len(train_loader)

    # -----------------------------
    # Evaluation on test set
    # -----------------------------
    model.eval()
    test_loss = 0.0
    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            test_loss += loss.item()
    avg_test_loss = test_loss / len(test_loader)

    print(f"Epoch [{epoch}/{num_epochs}] - Train Loss: {avg_train_loss:.4f} | Test Loss: {avg_test_loss:.4f}")

    # -----------------------------
    # Save checkpoints
    # -----------------------------
    if epoch % 10 == 0 or epoch == num_epochs:
        checkpoint_path = os.path.join(checkpoint_dir, f"checkpoint_epoch_{epoch}.pth")
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'train_loss': avg_train_loss,
            'test_loss': avg_test_loss
        }, checkpoint_path)
        print(f"[INFO] Saved checkpoint: {checkpoint_path}")

print("Training complete ✅")
