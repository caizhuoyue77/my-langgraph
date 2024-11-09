# load model
from FlagEmbedding import FlagModel
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid
import json

# Load the embedding model
model = FlagModel("/Users/caizhuoyue/Documents/code/bge-small-en-v1.5-tuned", use_fp16=True)

# Initialize the Qdrant client
client = QdrantClient(url="http://localhost:6333")

COLLECTION_NAME = 'test_embedding_bge_small_v1.5_tuned'

import uuid

def generate_uuid_from_string(input_string):
    # 使用 SHA-1 哈希生成 UUID
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, input_string))

# Calculate embedding
def encode_query(query):
    return model.encode([query])[0]

# Save to Qdrant
def save_to_qdrant(query, payload):

    vector = encode_query(query)
    query_id = generate_uuid_from_string(query)
    print(vector.tolist())
    print(payload)
    
    points = [PointStruct(vector = vector, payload = payload, id = query_id)]
    
    operation_info = client.upsert(
        collection_name=COLLECTION_NAME,
        wait=True,
        points=points
    )
    

# Query Qdrant
def query_qdrant(query, top_k):
    vector = encode_query(query)
    result = client.search(collection_name=COLLECTION_NAME, query_vector=vector, limit=top_k)
    return result

# client.create_collection(
#     collection_name=COLLECTION_NAME,
#     vectors_config=VectorParams(size=384, distance=Distance.DOT),
# )

if __name__ == '__main__':
    # Load JSON file
    # with open('/Users/caizhuoyue/Desktop/my-langgraph/data/retrieval/G1/unique_1k_apis.json', 'r') as f:
    #     data = json.load(f)

    # idx = 0
    # Process each item in the JSON list
    # for item in data:
    #     save_to_qdrant(str(item), item)
    #     print(f'{idx} saved')
    #     idx += 1

    # print("Data has been saved to Qdrant.")
    result = query_qdrant('I am in Shanghai travelling alone, do I need an umbrella if I leave in 30 minutes?', 10)
    print(result)