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
        "fields": "name,formatted_address,formatted_phone_number",
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

            data.append({
                "Name": name,
                "Address": address,
                "Phone Number": phone_number
            })

    return data

def save_to_existing_file(data, output_format):
    filename = f"output.{output_format}"

    if os.path.exists(filename):
        existing_data = getattr(pd, f"read_{output_format}")(filename)
        combined_data = pd.concat([existing_data, pd.DataFrame(data)], ignore_index=True)
        getattr(combined_data, f"to_{output_format}")(filename, index=False)
    else:
        pd.DataFrame(data).to_excel(filename, index=False)


def main():
    query = input("Enter the query you want to search: ")
    api_key = "YOUR GOOGLE MAPS API KEY"

    place_ids = get_place_ids(api_key, query)

    if place_ids:
        data = fetch_details_async(api_key, place_ids)

        output_format = input("Choose the output format (Excel, CSV, JSON): ").lower()

        save_to_existing_file(data, output_format)

    else:
        print("No data to export.")

if __name__ == "__main__":
    main()
