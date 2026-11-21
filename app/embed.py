
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

model = None


def get_model():
    global model

    if model is None:
        print("Loading Sentence Transformer model...")
        model = SentenceTransformer(MODEL_NAME)
        print("Embedding model loaded successfully.")

    return model


def generate_embeddings(texts):
    embedding_model = get_model()

    embeddings = embedding_model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embeddings.tolist()


if __name__ == "__main__":
    sample = ["Article 21 protects life and personal liberty."]
    vectors = generate_embeddings(sample)

    print("Embedding generated successfully")
    print("Vector dimensions:", len(vectors[0]))
