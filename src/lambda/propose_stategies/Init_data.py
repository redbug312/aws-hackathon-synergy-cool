import json

def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)

def calculate_ac_intensity(data):
    # Default values
    defaults = {
        'time': 12,
        'uv_index': 5,
        'number_of_people': 1,
        'space_size': 50,
        'ceiling_height': 2.5,
        'humidity': 50,
        'temperature': 25,
        'co2_concentration': 400,
        'stress_index': 50,
        'air_quality': 50,
        'building_material': 50,
        'month': 1
    }

    # Use defaults if values are missing or invalid
    for key, default in defaults.items():
        data[key] = data.get(key, default)
        if not isinstance(data[key], (int, float)) or data[key] == '':
            data[key] = default

    # Normalize each parameter to a value between 0 and 1
    time_factor = normalize(data['time'], 0, 24)
    uv_factor = normalize(data['uv_index'], 0, 11)  # UV index range is 0-11
    people_density = normalize(data['number_of_people'] / data['space_size'], 0, 1)  # Assuming max density is 1 person per square meter
    height_factor = normalize(data['ceiling_height'], 0, 3)  # Assuming typical height range is 0 to 3 meters
    humidity_factor = normalize(data['humidity'], 0, 100)
    temperature_factor = normalize(data['temperature'], 15, 40)  # Assuming 15-40°C range
    co2_factor = normalize(data['co2_concentration'], 0, 1000)  # Assuming 0-1000 ppm range
    stress_factor = normalize(data['stress_index'], 0, 100)
    air_quality_factor = normalize(100 - data['air_quality'], 0, 100)  # Inverting air quality for better interpretation
    material_factor = normalize(data['building_material'], 0, 100)

    # Summer months (June, July, August)
    if data['month'] in [6, 7, 8]:
        season_factor = 1
    else:
        season_factor = 0

    # Time factor adjustment for 10 PM to 5 AM (cooler at night)
    if 22 <= data['time'] or data['time'] <= 5:
        time_adjustment_factor = -0.1
    else:
        time_adjustment_factor = 0.1
    
    # Weighted sum of all factors
    intensity = (0.1 * time_factor +
                 0.1 * uv_factor +
                 0.2 * people_density +
                 0.1 * height_factor +
                 0.1 * humidity_factor +
                 0.2 * temperature_factor +
                 0.05 * co2_factor +
                 0.05 * stress_factor +
                 0.05 * air_quality_factor +
                 0.05 * material_factor +
                 0.05 * season_factor +
                 time_adjustment_factor)
    
    # Clamp the value between 0 and 1
    intensity = max(0, min(1, intensity))
    
    return intensity

def init_data_test():
    # Read the input JSON file
    with open('init.json', 'r') as file:
        data = json.load(file)
    
    # Calculate the volume
    volume = data.get('space_size', 50) * data.get('ceiling_height', 2.5)
    
    # Calculate the AC intensity
    ac_intensity = calculate_ac_intensity(data)
    
    # Prepare the output
    output_data = {
        "volume": volume,
        "current_relative_humidity": data.get('humidity', 50),
        "current_temperature": data.get('temperature', 25),
        "target_temperature": data.get('target_temperature', 25),
        "target_time": data.get('target_time', 12),
        "alpha_value": ac_intensity,
        "pressure": data.get('pressure', 101325)
    }
    
    # Write the output JSON file
    with open('input.json', 'w') as file:
        json.dump(output_data, file, indent=4)
    
    # Print the result
    print(f"Calculated AC intensity (alpha value): {ac_intensity:.2f}")

if __name__ == "__main__":
    init_data_test()