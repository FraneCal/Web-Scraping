import tkinter as tk
from tkinter import ttk, messagebox
from concurrent.futures import ThreadPoolExecutor
import os
import requests
import pandas as pd
import json
from pathlib import Path

class GoogleMapsScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Maps Scraper")

        self.create_widgets()

    def create_widgets(self):
        # Query Entry
        self.query_label = ttk.Label(self.root, text="Enter the query:")
        self.query_entry = ttk.Entry(self.root, width=30)
        self.query_label.grid(row=0, column=0, padx=10, pady=10)
        self.query_entry.grid(row=0, column=1, padx=10, pady=10)

        # Output Format Dropdown
        self.format_label = ttk.Label(self.root, text="Choose output format:")
        self.format_var = tk.StringVar()
        self.format_var.set("CSV")
        self.format_dropdown = ttk.Combobox(self.root, textvariable=self.format_var, values=["CSV", "JSON"])
        self.format_label.grid(row=1, column=0, padx=10, pady=10)
        self.format_dropdown.grid(row=1, column=1, padx=10, pady=10)

        # Search Button
        self.search_button = ttk.Button(self.root, text="Search and Save", command=self.search_and_save)
        self.search_button.grid(row=2, column=0, columnspan=2, pady=10)

    def search_and_save(self):
        query = self.query_entry.get()
        output_format = self.format_var.get().lower()

        if not query:
            messagebox.showerror("Error", "Please enter a query.")
            return

        try:
            api_key = "AIzaSyCplLL5nvAccR5vVDKJmQBAsImpbiqPF00"  # Replace with your actual API key

            place_ids = self.get_place_ids(api_key, query)

            if place_ids:
                data = self.fetch_details_async(api_key, place_ids)
                self.save_to_existing_file(data, query, output_format)
                messagebox.showinfo("Success", "Data saved successfully.")
            else:
                messagebox.showinfo("Info", "No data to export.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def get_place_ids(self, api_key, query):
        base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {"query": query, "key": api_key}

        response = requests.get(base_url, params=params)
        results = response.json().get("results", [])

        place_ids = [result["place_id"] for result in results]
        return place_ids

    def get_place_details(self, api_key, place_id):
        base_url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "name,formatted_address,formatted_phone_number",
            "key": api_key,
        }

        response = requests.get(base_url, params=params)
        place_details = response.json().get("result", {})

        return place_details

    def fetch_details_async(self, api_key, place_ids):
        data = []

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.get_place_details, api_key, place_id) for place_id in place_ids]

            for future in futures:
                place_details = future.result()
                name = place_details.get("name", "N/A")
                address = place_details.get("formatted_address", "N/A")
                phone_number = place_details.get("formatted_phone_number", "N/A")

                data.append({"Name": name, "Address": address, "Phone Number": phone_number})

        return data

    def save_to_existing_file(self, data, query, output_format):
        desktop_path = Path.home() / "Desktop"
        index = 1
        while True:
            filename = f"{query}{f'({index})' if index > 1 else ''}"
            full_filename = desktop_path / f"{filename}.{output_format}"

            if not full_filename.exists():
                break
            index += 1

        try:
            with open(full_filename, 'w') as file:
                if output_format == 'json':
                    json.dump(data, file, indent=2)
                elif output_format == 'csv':
                    df = pd.DataFrame(data)
                    df.to_csv(full_filename, index=False)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GoogleMapsScraperApp(root)
    root.mainloop()
