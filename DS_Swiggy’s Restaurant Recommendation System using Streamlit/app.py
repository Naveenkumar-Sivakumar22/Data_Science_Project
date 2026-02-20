import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, HTML, clear_output
import ipywidgets as widgets
from typing import List, Dict, Any, Tuple, Optional

# --- 1. Data Loading & Column Check ---
def load_data(file_path: str = "cleaned_data.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path)

        # Debugging: Print columns to help you see what is actually in your file
        print(f"Loaded columns: {df.columns.tolist()}")

        # Numeric conversions (handle missing columns gracefully)
        cols_to_fix = ['rating', 'price_level', 'reviews', 'latitude', 'longitude']
        for col in cols_to_fix:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except FileNotFoundError:
        print(f"Error: '{file_path}' not found.")
        return pd.DataFrame()

# --- 2. Filtering Logic ---
def filter_restaurants(df, city, cuisine, min_rating, max_price):
    filtered_df = df.copy()

    if city and city != "All":
        filtered_df = filtered_df[filtered_df['city'].str.contains(city, case=False, na=False)]

    if cuisine and cuisine != "All":
        filtered_df = filtered_df[filtered_df['cuisine'].str.contains(cuisine, case=False, na=False)]

    if 'rating' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['rating'] >= min_rating]

    if 'price_level' in filtered_df.columns:
        filtered_df = filtered_df[(filtered_df['price_level'] <= max_price) | (filtered_df['price_level'].isna())]

    return filtered_df

# --- 3. Robust Recommendation Logic (FIXES KEYERROR) ---
def recommend_restaurants(df, top_n=10):
    if df.empty:
        return df

    sort_cols = []
    asc_flags = []

    # Only sort by columns that actually exist in your CSV
    if 'rating' in df.columns:
        sort_cols.append('rating')
        asc_flags.append(False)

    if 'reviews' in df.columns:
        sort_cols.append('reviews')
        asc_flags.append(False)

    if sort_cols:
        return df.sort_values(by=sort_cols, ascending=asc_flags).head(top_n)
    return df.head(top_n)

# --- 4. UI Rendering Function ---
def update_dashboard(change=None):
    clear_output(wait=True)
    display(ui) # Keep the controls visible

    filtered = filter_restaurants(df, city_drop.value, cuisine_drop.value, rating_slider.value, price_slider.value)
    recs = recommend_restaurants(filtered, n_slider.value)

    print(f"\nFound {len(filtered)} restaurants matching your criteria")
    print("-" * 30)

    if recs.empty:
        print("No restaurants found. Try loosening your filters.")
    else:
        # Display Recommendations as HTML cards
        for _, row in recs.iterrows():
            # Handle potentially missing price/review data in the display
            p_val = row.get('price_level', 0)
            price_stars = "$" * int(p_val) if pd.notna(p_val) and p_val > 0 else "N/A"
            rev_count = int(row['reviews']) if 'reviews' in row and pd.notna(row['reviews']) else 0

            html_card = f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 10px; font-family: sans-serif; background-color: #f9f9f9;">
                <h3 style="margin: 0; color: #d32f2f;">{row.get('name', 'Unknown Restaurant')}</h3>
                <p><b>Rating:</b> <span style="color: #fbc02d;">★ {row.get('rating', 'N/A')}</span> ({rev_count} reviews) | <b>Price:</b> {price_stars}</p>
                <p style="margin: 5px 0;"><b>Cuisine:</b> {row.get('cuisine', 'N/A')} | <b>Location:</b> {row.get('city', 'N/A')}</p>
                <p style="font-size: 0.9em; color: #555;">{row.get('address', '')}</p>
            </div>
            """
            display(HTML(html_card))

        # Visualization
        if 'rating' in recs.columns and not recs['rating'].dropna().empty:
            plt.figure(figsize=(8, 3))
            plt.hist(recs['rating'], bins=5, color='skyblue', edgecolor='black')
            plt.title("Rating Distribution of Top Recommendations")
            plt.xlabel("Rating")
            plt.ylabel("Count")
            plt.show()

# --- 5. Main Execution ---
df = load_data()

if not df.empty:
    # Prepare dropdown options safely
    cities = ["All"] + sorted(df['city'].dropna().unique().tolist()) if 'city' in df.columns else ["All"]
    cuisines = ["All"] + sorted(df['cuisine'].dropna().unique().tolist()) if 'cuisine' in df.columns else ["All"]

    # Create Widgets
    city_drop = widgets.Dropdown(options=cities, description='City:')
    cuisine_drop = widgets.Dropdown(options=cuisines, description='Cuisine:')
    rating_slider = widgets.FloatSlider(value=3.5, min=0, max=5.0, step=0.1, description='Min Rating:')
    price_slider = widgets.IntSlider(value=4, min=1, max=4, description='Max Price:')
    n_slider = widgets.IntSlider(value=5, min=1, max=20, description='Top N:')

    # Layout Controls
    ui = widgets.VBox([
        widgets.HBox([city_drop, cuisine_drop]),
        widgets.HBox([rating_slider, price_slider, n_slider])
    ])

    # Set up observers so the dashboard updates automatically
    for w in [city_drop, cuisine_drop, rating_slider, price_slider, n_slider]:
        w.observe(update_dashboard, names='value')

    # Initial display
    update_dashboard()
