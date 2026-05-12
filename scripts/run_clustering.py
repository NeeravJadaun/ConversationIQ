from http_utils import API_URL, request


def main() -> None:
    print(f"Running clustering against {API_URL}")
    clusters = request("POST", "/api/clusters/recompute")
    print(f"Clustering complete: {len(clusters)} clusters found")


if __name__ == "__main__":
    main()
