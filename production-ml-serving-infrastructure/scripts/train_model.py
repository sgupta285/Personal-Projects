from app.ml.train import train_model

if __name__ == "__main__":
    metadata = train_model()
    print("trained", metadata["model_version"])
