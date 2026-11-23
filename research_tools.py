import requests

def search_openalex(topic):

    print(f"\nSearching OpenAlex for: {topic}")

    url = "https://api.openalex.org/works"

    params = {
        "search": topic,
        "per-page": 5
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        print("HTTP Status:", response.status_code)

        if response.status_code != 200:
            print("API Error:", response.text[:500])
            return []

        data = response.json()

        papers = data.get("results", [])

        for i, paper in enumerate(papers, start=1):

            title = paper.get("title", "No title")
            year = paper.get("publication_year", "Unknown")
            doi = paper.get("doi", "No DOI")

            authors = []

            for author in paper.get("authorships", []):
                name = author.get("author", {}).get("display_name")
                if name:
                    authors.append(name)

            print(f"\nPaper {i}")
            print("-" * 50)
            print("Title:", title)
            print("Year:", year)
            print("Authors:", ", ".join(authors[:5]))
            print("DOI:", doi)

        return papers

    except requests.exceptions.Timeout:
        print("Error: OpenAlex request timed out.")

    except requests.exceptions.RequestException as e:
        print("Request error:", e)

    except Exception as e:
        print("Unexpected error:", e)

    return []
if __name__ == "__main__":
    search_openalex("Machine Learning")