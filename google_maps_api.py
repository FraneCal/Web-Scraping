import requests

def get_place_id(api_key, query):
    base_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": query,
        "inputtype": "textquery",
        "fields": "place_id",
        "key": api_key,
    }

    response = requests.get(base_url, params=params)
    results = response.json().get("candidates", [])

    place_ids = [result["place_id"] for result in results]
    return place_ids

def get_place_details(api_key, place_id):
    base_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,formatted_phone_number,review",
        "key": api_key,
    }

    response = requests.get(base_url, params=params)
    place_details = response.json().get("result", {})

    return place_details

def main():
    api_key = "ENTER YOUR GOOGLE MAPS API KEY"
    query = "Bauhaus Zagreb"

    place_ids = get_place_id(api_key, query)

    for place_id in place_ids:
        place_details = get_place_details(api_key, place_id)

        name = place_details.get("name", "N/A")
        address = place_details.get("formatted_address", "N/A")
        phone_number = place_details.get("formatted_phone_number", "N/A")
        reviews_count = len(place_details.get("reviews", []))

        print(f"Name: {name}")
        print(f"Address: {address}")
        print(f"Phone Number: {phone_number}")
        print(f"Number of Reviews: {reviews_count}")
        print("---")

if __name__ == "__main__":
    main()
