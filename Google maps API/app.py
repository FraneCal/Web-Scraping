from flask import Flask, render_template, request, send_file, redirect, url_for, session, make_response
import os
import requests
import pandas as pd
import secrets
import tempfile
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
secret_key = secrets.token_hex(16)
app.secret_key = secret_key

def get_place_ids(api_key, query):
    """Fetches place IDs using the Google Places Text Search API."""
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
    """Fetches detailed information for a given place using the Google Places Details API."""
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
    """Fetches place details asynchronously using ThreadPoolExecutor."""
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
    """Saves data to a file, handling file naming conflicts."""
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
    """Handles the main index route, including form submissions."""
    if request.method == 'POST':
        query = request.form['query']
        output_format = request.form['output_format'].lower()

        api_key = "YOUR GOOGLE MAPS API KEY"

        place_ids = get_place_ids(api_key, query)

        if place_ids:
            data = fetch_details_async(api_key, place_ids)
            save_to_existing_file(data, query, output_format)

            session['data'] = data
            session['query'] = query
            session['output_format'] = output_format
            success_message = "Search was successful!"
            return render_template('index.html', data=data, success_message=success_message)
        else:
            return render_template('index.html', message="No data to export.")

    # Clear session on page load
    session.clear()
    return render_template('index.html')


@app.route('/download')
def download():
    """Handles file download, ensuring the file exists and setting appropriate headers."""
    query = session.get('query')
    output_format = session.get('output_format')

    if query and output_format:
        filename = f"{query}_{output_format.lower()}"
        
        # Use a temporary directory
        folder_path = tempfile.mkdtemp()

        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f"{filename}.{output_format.lower()}")

        print(f"File Path: {file_path}")

        if os.path.exists(file_path):
            # Create a Flask response with the file
            response = make_response(send_file(file_path, as_attachment=True))

            # Set the Content-Disposition and Content-Type headers
            response.headers["Content-Disposition"] = f"attachment; filename={filename}.{output_format.lower()}"
            response.headers["Content-Type"] = "application/octet-stream"

            return response
        else:
            print("File not found!")

    # Redirect only if the file doesn't exist
    return redirect(url_for('index'))

@app.route('/delete_results')
def delete_results():
    """Handles clearing session data on a request to delete results."""
    # Clear session
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
