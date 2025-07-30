import requests
import pandas as pd
from datetime import datetime

def get_place_id(pincode, headers):
    response = requests.get(
        "https://api.zeptonow.com/api/v1/maps/place/autocomplete",
        params={'place_name': pincode},
        headers=headers
    )
    if response.status_code == 200:
        json_response = response.json()
        place_candidates = json_response.get("predictions", [])
        if place_candidates:
            return place_candidates[0].get("place_id")
    return None

def get_lat_lng(place_id, headers):
    response = requests.get(
        "https://api.zeptonow.com/api/v1/maps/place/details", 
        params={'place_id': place_id},
        headers=headers
    )
    if response.status_code == 200:
        json_response = response.json()
        result = json_response.get("result", {})
        geometry = result.get("geometry", {})
        location = geometry.get("location", {})
        return location.get("lat"), location.get("lng")
    return None, None

def get_store_id(lat, lng, headers):
    response = requests.get(
        "https://api.zeptonow.com/api/v2/get_page",
        params={'latitude': lat, 'longitude': lng, 'page_type': 'HOME', 'version': 'v2'},
        headers=headers
    )
    if response.status_code == 200:
        json_response = response.json()
        store_serviceable = json_response.get("storeServiceableResponse", {})
        return store_serviceable.get("storeId")
    return None

def get_product_info(lat, lng, store_id, product_id, headers):
    response = requests.get(
        "https://api.zeptonow.com/api/v2/get_page",
        params={
            'latitude': lat,
            'longitude': lng,
            'page_type': 'PDP',
            'version': 'v3',
            'product_variant_id': product_id,
            'store_id': store_id,
            "show_new_eta_banner": "false",
            "page_size": 10,
            "enforce_platform_type": "DESKTOP"
        },
        headers=headers
    )
    if response.status_code == 200:
        json_response = response.json()
        pageLayout = json_response.get("pageLayout", {})
        header = pageLayout.get("header", {})
        widget = header.get("widget", {})
        data = widget.get("data", {})
        productInfo = data.get("productInfo", {})
        storeProduct = productInfo.get("storeProduct", {})
        return {
            'mrp': storeProduct.get("mrp"),
            'out_of_stock': storeProduct.get("outOfStock"),
            'channel': 'Zepto'
        }
    return None

def main(file_path):
    df = pd.read_csv(file_path, header=None, names=["Product ID", "Pincode"])
    product_ids = df["Product ID"].tolist()
    pincodes = df["Pincode"].tolist()

    headers = {
        "Host": "api.zeptonow.com",
        "Accept": "/",
        "content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "platform": "WEB"
    }

    output_data = []

    for pincode, product_id in zip(pincodes, product_ids):
        place_id = get_place_id(pincode, headers)
        if not place_id:
            output_data.append([pincode, product_id, "Failed to get place ID"])
            continue
        
        lat, lng = get_lat_lng(place_id, headers)
        if lat is None or lng is None:
            output_data.append([pincode, product_id, "Failed to get coordinates"])
            continue
        
        store_id = get_store_id(lat, lng, headers)
        if not store_id:
            output_data.append([pincode, product_id, "Failed to get store ID"])
            continue
        
        product_info = get_product_info(lat, lng, store_id, product_id, headers)
        if product_info:
            output_data.append([pincode, product_id, product_info['mrp'], product_info['out_of_stock'], product_info['channel']])
        else:
            output_data.append([pincode, product_id, "Failed to get product info"])
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"Zepto_products_items_{timestamp}.csv"
    output_df = pd.DataFrame(output_data, columns=["Pincode", "Product ID", "MRP", "Out of Stock", "Channel"])
    output_df.to_csv(output_filename, index=False)
    print(f"Output saved to {output_filename}")

if __name__ == "__main__":
    main("Zepto_items.csv")
