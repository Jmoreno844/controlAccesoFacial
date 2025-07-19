import torch

print(torch.cuda.is_available()) # Check if CUDA is available
print(torch.backends.cudnn.is_available()) # Check if cuDNN is available
print(torch.backends.cudnn.version()) # Get cuDNN version

# If CUDA is available, you can also check the device count and run a test tensor:
if torch.cuda.is_available():
    print(f"Number of GPUs: {torch.cuda.device_count()}")
    device = torch.device("cuda:0") # Use the first GPU
    x = torch.randn(1, 3).to(device) # Example tensor
    print(f"Test tensor on GPU: {x}")