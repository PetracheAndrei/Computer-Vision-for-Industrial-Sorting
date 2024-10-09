from ultralytics import YOLO

# Load a model
model = YOLO("generations/gen_5.pt")

# Use the model
model.train(data="config.yaml", epochs=4, batch = 16)  # train the model