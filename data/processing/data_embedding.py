import pandas as pd
from sentence_transformers import SentenceTransformer

df = pd.read_parquet("data/ready/michelin.parquet")

# model
model = SentenceTransformer("multi-qa-mpnet-base-dot-v1")

# Generate address embeddings
df["embedding"] = df["Address"].apply(
    lambda x: model.encode(x).astype("float16").tolist()
)

df.to_parquet(
    "data/ready/michelin_embedding.parquet",
    index=False,
    compression="brotli",
    compression_level=11,
)
