
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embeddings(texts):
    embeddings = model.encode(
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
