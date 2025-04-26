from transformers import AutoTokenizer, AutoModel
import torch

model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Export to ONNX
dummy_input = tokenizer("hello world", return_tensors="pt")
torch.onnx.export(model, (dummy_input["input_ids"],), "model.onnx")
