import os
import requests
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor

def get_place_ids(api_key, query):
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": api_key,
    }

    response = requests.get(base_url, params=params)
    results = response.json().get("results", [])

    place_ids = [result["place_id"] for result in results]
    return place_ids

def get_place_details(api_key, place_id):
    base_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,formatted_phone_number,user_ratings_total,rating,reviews",
        "key": api_key,
    }

    response = requests.get(base_url, params=params)
    place_details = response.json().get("result", {})

    return place_details

def fetch_details_async(api_key, place_ids):
    data = []

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_place_details, api_key, place_id) for place_id in place_ids]

        for future in futures:
            place_details = future.result()
            name = place_details.get("name", "N/A")
            address = place_details.get("formatted_address", "N/A")
            phone_number = place_details.get("formatted_phone_number", "N/A")
            user_ratings_total = place_details.get("user_ratings_total", "N/A")
            rating = place_details.get("rating", "N/A")

            data.append({
                "Name": name,
                "Address": address,
                "Phone Number": phone_number,
                "Number of Reviews": user_ratings_total,
                "Total rating": rating,
            })

    for info in data:
        print(info)

    return data

def save_to_existing_file(data, query, output_format):
    index = 1
    while True:
        filename = f"{query}_{output_format}{f'({index})' if index > 1 else ''}"
        full_filename = f"{filename}.{output_format}"

        if not os.path.exists(full_filename):
            break
        index += 1

    if os.path.exists(full_filename):
        existing_data = pd.read_json(full_filename) if output_format == 'json' else pd.read_csv(full_filename)
        combined_data = pd.concat([existing_data, pd.DataFrame(data)], ignore_index=True)
        if output_format == 'json':
            combined_data.to_json(full_filename, orient='records', lines=True)
        else:
            combined_data.to_csv(full_filename, index=False)
    else:
        pd.DataFrame(data).to_json(full_filename, orient='records', lines=True) if output_format == 'json' else pd.DataFrame(data).to_csv(full_filename, index=False)

def main():
    query = input("Enter the query you want to search: ")
    api_key = "YOUR GOOGLE MAPS API KEY"

    place_ids = get_place_ids(api_key, query)

    if place_ids:
        data = fetch_details_async(api_key, place_ids)

        output_format = input("Choose the output format (CSV, JSON): ").lower()

        save_to_existing_file(data, query, output_format)

    else:
        print("No data to export.")

if __name__ == "__main__":
    main()
