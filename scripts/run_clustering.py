from http_utils import request


def main() -> None:
    clusters = request("POST", "/api/clusters/recompute")
    print(f"Clustering complete: {len(clusters)} clusters found")


if __name__ == "__main__":
    main()
