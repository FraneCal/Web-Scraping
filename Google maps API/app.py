from flask import Flask, render_template, request
import os
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        output_format = request.form['output_format'].lower()

        api_key = "YOUR GOOGLE MAPS API KEY"

        place_ids = get_place_ids(api_key, query)

        if place_ids:
            data = fetch_details_async(api_key, place_ids)

            save_to_existing_file(data, query, output_format)

            return render_template('index.html', data=data)
        else:
            return render_template('index.html', message="No data to export.")

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)