from http_utils import API_URL, request


def main() -> None:
    print(f"Generating recommendations against {API_URL}")
    procedures = request("GET", "/api/procedures")
    weak = [op for op in procedures if op["health_score"] < 76][:3]
    for op in weak:
        recommendation = request("POST", "/api/recommendations/generate", {"op_id": op["id"]})
        print(f"{op['id']} {recommendation['priority']}: {recommendation['recommendation_text'][:110]}...")


if __name__ == "__main__":
    main()
