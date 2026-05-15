import json
import os
import sys

# Add parent dir to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.retrieval_service import retrieval_service

def evaluate_retrieval():
    dataset_path = os.path.join(os.path.dirname(__file__), "dataset.json")
    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    total_queries = len(dataset)
    successful_retrievals = 0

    print("Running Evaluation...\n")

    for item in dataset:
        query = item["query"]
        expected_keywords = item["expected_keywords"]
        
        print(f"Query: {query}")
        results = retrieval_service.search(query, top_k=3)
        
        found = False
        if results:
            combined_text = " ".join([r["text"].lower() for r in results])
            # Check if at least one expected keyword is in the retrieved text
            for kw in expected_keywords:
                if kw in combined_text:
                    found = True
                    break
        
        if found:
            print("Status: ✅ SUCCESS")
            successful_retrievals += 1
        else:
            print("Status: ❌ FAILED")
            
        print("-" * 40)
        
    accuracy = (successful_retrievals / total_queries) * 100
    print(f"\nEvaluation Complete: {accuracy:.2f}% Accuracy ({successful_retrievals}/{total_queries})")
    
if __name__ == "__main__":
    evaluate_retrieval()
