import os
import requests
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor

def get_place_ids(api_key, query):
    """
    Retrieve place IDs using the Google Places Text Search API.

    Parameters:
    - api_key (str): Your Google Maps API key.
    - query (str): The query string for the place search.

    Returns:
    - list: List of place IDs.
    """
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
    """
    Retrieve detailed information about a place using the Google Places Details API.

    Parameters:
    - api_key (str): Your Google Maps API key.
    - place_id (str): The unique identifier for the place.

    Returns:
    - dict: Detailed information about the place.
    """
    base_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,formatted_phone_number,user_ratings_total,rating,reviews,website",
        "key": api_key,
    }

    response = requests.get(base_url, params=params)
    place_details = response.json().get("result", {})

    return place_details

def fetch_details_async(api_key, place_ids):
    """
    Fetch detailed information about multiple places asynchronously.

    Parameters:
    - api_key (str): Your Google Maps API key.
    - place_ids (list): List of place IDs.

    Returns:
    - list: List of dictionaries containing detailed information about each place.
    """
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
            website = place_details.get("website", "N/A")

            data.append({
                "Name": name,
                "Address": address,
                "Phone Number": phone_number,
                "Website": website,
                "Number of Reviews": user_ratings_total,
                "Total rating": rating,
            })

    for info in data:
        #print(info)
        pass

    return data

def save_to_existing_file(data, query, output_format):
    """
    Save data to a new or existing file in JSON or CSV format.

    Parameters:
    - data (list): List of dictionaries containing place information.
    - query (str): The original query used for the place search.
    - output_format (str): The desired output format (CSV or JSON).
    """
    index = 1
    query_filename = "_".join(query.split())
    while True:
        filename = f"{query_filename}{f'({index})' if index > 1 else ''}"
        full_filename = f"{filename}.{output_format}"

        if not os.path.exists(full_filename):
            break
        index += 1

    if output_format == 'xlsx':
        with pd.ExcelWriter(full_filename, engine='openpyxl') as writer:
            df = pd.DataFrame(data)
            df.to_excel(writer, index=False)
    else:
        with open(full_filename, 'w', encoding='utf-8') as file:
            if output_format == 'json':
                json.dump(data, file, ensure_ascii=False, indent=2)
            elif output_format == 'csv':
                df = pd.DataFrame(data)
                df.to_csv(file, index=False)

    print(f"Successfully saved to {full_filename}")  # Print success message


def main():
    """
    Main function to execute the Google Maps scraping process.

    Takes user input for the query, fetches place details, and saves the data to a file.
    """
    while True:
        query = input("Enter the query you want to search (enter 'q' to quit): ")
        if query.lower() == 'q':
            break

        api_key = "YOUR GOOGLE MAPS API KEY"
        place_ids = get_place_ids(api_key, query)

        if place_ids:
            data = fetch_details_async(api_key, place_ids)

            output_format = input("Choose the output format (CSV, JSON, XLSX): ").lower()

            save_to_existing_file(data, query, output_format)
            #print("Successfully saved")  # Print success message

        else:
            print("No data to export.")

if __name__ == "__main__":
    main()
