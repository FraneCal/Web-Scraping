import os
import requests
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor
import time

def get_place_ids(api_key, query):
    """
    Retrieve place IDs using the Google Places Text Search API with pagination.

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

    place_ids = []
    while True:
        response = requests.get(base_url, params=params)
        results = response.json().get("results", [])
        place_ids.extend([result["place_id"] for result in results])

        next_page_token = response.json().get("next_page_token")
        if not next_page_token:
            break

        # Update the parameters to include the next_page_token
        params["pagetoken"] = next_page_token

        # Wait for a short period before making the next request
        time.sleep(2)

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
        "fields": "name,formatted_address,formatted_phone_number,user_ratings_total,rating,reviews,website,geometry,photos,place_id",
        "key": api_key,
    }

    response = requests.get(base_url, params=params)
    place_details = response.json().get("result", {})

    return place_details

def fetch_details_async(api_key, place_ids, keyword, location):
    """
    Fetch detailed information about multiple places asynchronously.

    Parameters:
    - api_key (str): Your Google Maps API key.
    - place_ids (list): List of place IDs.
    - keyword (str): The keyword entered by the user.
    - location (str): The location entered by the user.

    Returns:
    - list: List of dictionaries containing detailed information about each place.
    """
    data = []

    keyword = keyword.title()
    location = location.title()

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_place_details, api_key, place_id) for place_id in place_ids]

        for future in futures:
            place_details = future.result()
            name = place_details.get("name", "N/A")
            address = place_details.get("formatted_address", "N/A")
            website = place_details.get("website", "N/A")
            phone_number = place_details.get("formatted_phone_number", "N/A")
            rating = place_details.get("rating", "N/A")
            user_ratings_total = place_details.get("user_ratings_total", "N/A")
            latitude = place_details.get("geometry", {}).get("location", {}).get("lat", "N/A")
            longitude = place_details.get("geometry", {}).get("location", {}).get("lng", "N/A")
            # place_id = place_details.get("place_id", "N/A")
            # email = place_details.get("email", "N/A")
            # instagram = place_details.get("instagram", "N/A")
            # twitter = place_details.get("twitter", "N/A")
            # linkedin = place_details.get("linkedin", "N/A")
            # youtube = place_details.get("youtube", "N/A")
            # business_hours = place_details.get("opening_hours", {}).get("weekday_text", "N/A")
            # business_page_link = f"https://www.google.com/maps/place/?q=place_id:{place_id}"

            # Use user-entered keyword and location
            keyword = keyword.title()
            location = location.title()

            data.append({
                "Name": name,
                "Address": address,
                "Phone Number": phone_number,
                "Website": website,
                "Number of Reviews": user_ratings_total,
                "Total rating": rating,
                "Latitude": latitude,
                "Longitude": longitude,
                # "Place ID": place_id,
                # "Email": email,
                # "Instagram": instagram,
                # "Twitter": twitter,
                # "LinkedIn": linkedin,
                # "YouTube": youtube,
                # "Business Hours": business_hours,
                # "Business Page Link": business_page_link,
                # "Keyword": keyword,
                # "Location": location,
            })

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
    
    # Replace comma with underscore in the filename
    query_filename = query_filename.replace(',', '_')
    
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

        # Extract keyword and location from the query
        keyword, _, location = query.partition(",")
        keyword = keyword.strip()
        location = location.strip()

        api_key = "YOUR GOOGLE MAPS API KEY"
        place_ids = get_place_ids(api_key, query)

        if place_ids:
            data = fetch_details_async(api_key, place_ids, keyword, location)

            output_format = input("Choose the output format (CSV, JSON, XLSX): ").lower()

            save_to_existing_file(data, query, output_format)

        else:
            print("No data to export.")

if __name__ == "__main__":
    main()




# import os
# import requests
# import pandas as pd
# import json
# from concurrent.futures import ThreadPoolExecutor


# def get_facebook_page_link(api_key, query):
#     base_url = "https://graph.facebook.com/v14.0"
#     access_token = "YOUR FACEBOOK GRAPH API KEY"

#     search_url = f"{base_url}/search"
#     search_params = {
#         "q": query,
#         "type": "page",
#         "access_token": access_token,
#     }

#     print(f"Facebook Graph API Request: {search_url}?{search_params}")

#     response = requests.get(search_url, params=search_params)
#     result_data = response.json().get("data", [])

#     print(f"Facebook Graph API Response: {response.json()}")

#     if result_data:
#         first_result = result_data[0]
#         page_link = first_result.get("link")

#         if page_link:
#             return page_link
#         else:
#             print(f"Error: Facebook Page link not found in the result for query: {query}")
#     else:
#         print(f"Error: No data found in the Facebook Graph API response for query: {query}")

#     return None

# def get_place_ids(api_key, query):
#     """
#     Retrieve place IDs using the Google Places Text Search API.

#     Parameters:
#     - api_key (str): Your Google Maps API key.
#     - query (str): The query string for the place search.

#     Returns:
#     - list: List of place IDs.
#     """
#     base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
#     params = {
#         "query": query,
#         "key": api_key,
#     }

#     response = requests.get(base_url, params=params)
#     results = response.json().get("results", [])

#     place_ids = [result["place_id"] for result in results]
#     return place_ids

# def get_place_details(api_key, place_id):
#     """
#     Retrieve detailed information about a place using the Google Places Details API.

#     Parameters:
#     - api_key (str): Your Google Maps API key.
#     - place_id (str): The unique identifier for the place.

#     Returns:
#     - dict: Detailed information about the place.
#     """
#     base_url = "https://maps.googleapis.com/maps/api/place/details/json"
#     params = {
#         "place_id": place_id,
#         "fields": "name,formatted_address,formatted_phone_number,user_ratings_total,rating,reviews,website,geometry,photos,place_id",
#         "key": api_key,
#     }

#     response = requests.get(base_url, params=params)
#     place_details = response.json().get("result", {})

#     return place_details

# def fetch_details_async(api_key, place_ids, keyword, location):
#     """
#     Fetch detailed information about multiple places asynchronously.

#     Parameters:
#     - api_key (str): Your Google Maps API key.
#     - place_ids (list): List of place IDs.
#     - keyword (str): The keyword entered by the user.
#     - location (str): The location entered by the user.

#     Returns:
#     - list: List of dictionaries containing detailed information about each place.
#     """
#     data = []

#     keyword = keyword.title()
#     location = location.title()

#     facebook_page_link = get_facebook_page_link(api_key, f"{keyword} {location}")

#     with ThreadPoolExecutor() as executor:
#         futures = [executor.submit(get_place_details, api_key, place_id) for place_id in place_ids]

#         for future in futures:
#             place_details = future.result()
#             name = place_details.get("name", "N/A")
#             address = place_details.get("formatted_address", "N/A")
#             website = place_details.get("website", "N/A")
#             phone_number = place_details.get("formatted_phone_number", "N/A")
#             rating = place_details.get("rating", "N/A")
#             user_ratings_total = place_details.get("user_ratings_total", "N/A")
#             photos = [f"https://maps.googleapis.com/maps/api/place/photo?key={api_key}&photoreference={photo['photo_reference']}&maxwidth=400" for photo in place_details.get("photos", [])]
#             latitude = place_details.get("geometry", {}).get("location", {}).get("lat", "N/A")
#             longitude = place_details.get("geometry", {}).get("location", {}).get("lng", "N/A")
#             place_id = place_details.get("place_id", "N/A")
#             email = place_details.get("email", "N/A")
#             instagram = place_details.get("instagram", "N/A")
#             twitter = place_details.get("twitter", "N/A")
#             linkedin = place_details.get("linkedin", "N/A")
#             youtube = place_details.get("youtube", "N/A")
#             business_hours = place_details.get("opening_hours", {}).get("weekday_text", "N/A")
#             business_page_link = f"https://www.google.com/maps/place/?q=place_id:{place_id}"

#             # Use user-entered keyword and location
#             keyword = keyword.title()
#             location = location.title()

#             data.append({
#                 "Name": name,
#                 "Address": address,
#                 "Phone Number": phone_number,
#                 "Website": website,
#                 "Number of Reviews": user_ratings_total,
#                 "Total rating": rating,
#                 "Photos": photos,
#                 "Latitude": latitude,
#                 "Longitude": longitude,
#                 "Place ID": place_id,
#                 "Email": email,
#                 "Facebook": facebook_page_link,
#                 "Instagram": instagram,
#                 "Twitter": twitter,
#                 "LinkedIn": linkedin,
#                 "YouTube": youtube,
#                 "Business Hours": business_hours,
#                 "Business Page Link": business_page_link,
#                 "Keyword": keyword,
#                 "Location": location,
#             })

#     return data

# def save_to_existing_file(data, query, output_format):
#     """
#     Save data to a new or existing file in JSON or CSV format.

#     Parameters:
#     - data (list): List of dictionaries containing place information.
#     - query (str): The original query used for the place search.
#     - output_format (str): The desired output format (CSV or JSON).
#     """
#     index = 1
#     query_filename = "_".join(query.split())
    
#     # Replace comma with underscore in the filename
#     query_filename = query_filename.replace(',', '_')
    
#     while True:
#         filename = f"{query_filename}{f'({index})' if index > 1 else ''}"
#         full_filename = f"{filename}.{output_format}"

#         if not os.path.exists(full_filename):
#             break
#         index += 1

#     if output_format == 'xlsx':
#         with pd.ExcelWriter(full_filename, engine='openpyxl') as writer:
#             df = pd.DataFrame(data)
#             df.to_excel(writer, index=False)
#     else:
#         with open(full_filename, 'w', encoding='utf-8') as file:
#             if output_format == 'json':
#                 json.dump(data, file, ensure_ascii=False, indent=2)
#             elif output_format == 'csv':
#                 df = pd.DataFrame(data)
#                 df.to_csv(file, index=False)

#     print(f"Successfully saved to {full_filename}")  # Print success message


# def main():
#     """
#     Main function to execute the Google Maps scraping process.

#     Takes user input for the query, fetches place details, and saves the data to a file.
#     """
#     while True:
#         query = input("Enter the query you want to search (enter 'q' to quit): ")
#         if query.lower() == 'q':
#             break

#         # Extract keyword and location from the query
#         keyword, _, location = query.partition(",")
#         keyword = keyword.strip()
#         location = location.strip()

#         api_key = "YOUR GOOGLE MAPS API KEY"
#         place_ids = get_place_ids(api_key, query)

#         if place_ids:
#             data = fetch_details_async(api_key, place_ids, keyword, location)

#             output_format = input("Choose the output format (CSV, JSON, XLSX): ").lower()

#             save_to_existing_file(data, query, output_format)

#         else:
#             print("No data to export.")

# if __name__ == "__main__":
#     main()
