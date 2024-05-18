import json
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value, LpStatus
import CoolProp.CoolProp as CP

DEFAULT_PRESSURE = 101325  # 标准大气压，帕斯卡
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
def load_from_json(filename):
    """
    Load data from a JSON file.
    :param filename: str, the name of the JSON file
    :return: dict, the data loaded from the JSON file
    """
    with open(filename, 'r') as f:
        return json.load(f)

def save_to_json(data, filename):
    """
    Save the data to a JSON file.
    :param data: dict, the data to be saved
    :param filename: str, the name of the JSON file
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def calculate_cooling_power(data):
    volume = data["volume"]  # 立方米
    current_relative_humidity = data["current_relative_humidity"]  # 当前相对湿度，百分比
    current_temperature = data["current_temperature"]  # 摄氏度
    target_temperature = data["target_temperature"]  # 摄氏度
    target_time_minutes = data["target_time"]  # 分钟
    alpha_value = data["alpha_value"]
    pressure = data.get("pressure", DEFAULT_PRESSURE)  # 气压，帕斯卡，默认为标准大气压
    
    multiple_avlue = alpha_value / 2 +1

    # 初始化空气的属性
    fluid = 'Air'
    
    # 当前状态
    current_temperature_kelvin = current_temperature + 273.15  # 转换为开尔文
    current_humidity_ratio = CP.HAPropsSI('W', 'T', current_temperature_kelvin, 'P', pressure, 'RH', current_relative_humidity / 100)
    current_enthalpy = CP.HAPropsSI('H', 'T', current_temperature_kelvin, 'P', pressure, 'W', current_humidity_ratio)
    
    # 目标状态
    target_temperature_kelvin = target_temperature + 273.15  # 转换为开尔文
    target_humidity_ratio = CP.HAPropsSI('W', 'T', target_temperature_kelvin, 'P', pressure, 'RH', current_relative_humidity / 100)
    target_enthalpy = CP.HAPropsSI('H', 'T', target_temperature_kelvin, 'P', pressure, 'W', target_humidity_ratio)
    
    # 计算空气的密度
    density = CP.PropsSI('D', 'T', current_temperature_kelvin, 'P', pressure, fluid)

    # 计算所需的能量（焦耳）
    required_energy = volume * density * (current_enthalpy - target_enthalpy)  # 焦耳，冷却过程中能量减少

    # 将能量转换为功率（瓦特）
    required_power = required_energy / (target_time_minutes * 60)  # 瓦特

    # 打印调试信息
    print(f"Current enthalpy: {current_enthalpy:.2f} J/kg")
    print(f"Target enthalpy: {target_enthalpy:.2f} J/kg")
    print(f"Density: {density:.2f} kg/m³")
    print(f"Required energy: {required_energy:.2f} J")
    
    return required_power * multiple_avlue


def calculate_y(z):
    # 当 z <= 0.002 时，y 为 0；当 z > 0.002 时，y 的值为 0.8*z + 0.3 且不能超过 1
    return [0 if zi <= 0.002 else min(0.8 * zi + 0.3, 1) for zi in z]

def optimize_z(x_values, min_value):
    n = len(x_values)
    # 定义问题
    prob = LpProblem("Minimize_Y", LpMinimize)
    
    # 定义变量
    z = [LpVariable(f"z{i}", 0, 1) for i in range(n)]
    
    # 目标函数
    y = calculate_y(z)
    prob += lpSum(y[i] * x_values[i] for i in range(n))
    
    # 约束条件
    prob += lpSum(z[i] * x_values[i] for i in range(n)) == min_value

    # 求解问题
    prob.solve()

    # 检查解的状态
    if LpStatus[prob.status] != 'Optimal' or sum(value(zi) * x_values[i] for i, zi in enumerate(z)) < (min_value -1):
        # 如果没有找到最优解，或者解的总和小于 min_value，将所有 z 设置为 1
        print("sssss")
        print(sum(value(zi) * x_values[i] for i, zi in enumerate(z)))
        return [1] * n
    
    # 提取结果
    optimized_z = [value(zi) for zi in z]
    return optimized_z


def vincent_algorithm_test(data):
    # Calculate the volume
    volume = data.get('space_size', 50) * data.get('ceiling_height', 2.5)
    
    # Calculate the AC intensity
    ac_intensity = calculate_ac_intensity(data)
    
    # Prepare the output
    temp = {
        "volume": volume,
        "current_relative_humidity": data.get('humidity', 50),
        "current_temperature": data.get('temperature', 25),
        "target_temperature": data.get('target_temperature', 25),
        "target_time": data.get('target_time', 12),
        "alpha_value": ac_intensity,
        "pressure": data.get('pressure', 101325)
    }
    
    input_data = temp
    required_power = calculate_cooling_power(input_data)
    output_data = {"required_power": required_power}
    
    input_data = load_from_json("aircondition_array.json")
    min_value_data = output_data
    
    x_values = list(input_data.values())
    min_value = min_value_data['required_power']

    optimized_z = optimize_z(x_values, min_value)
    y_values = calculate_y(optimized_z)
    total_y = sum(y * x for y, x in zip(y_values, x_values))
    total_zx = sum(z * x for z, x in zip(optimized_z, x_values))

    optimized_percentages = {f"z{i+1}": round(optimized_z[i], 2) for i in range(len(optimized_z))}
    output_data = {
        "optimized_percentages": optimized_percentages,
        "total_y": round(total_y, 2),
        "total_zx": round(total_zx, 2)
    }

    print("Optimized percentages:")
    for key, value in optimized_percentages.items():
        print(f"{key}: {value:.2f}")
    print(f"Total y value: {total_y:.2f}")
    print(f"Total zx value: {total_zx:.2f}")
    return output_data

if __name__ == "__main__":
    vincent_algorithm_test()


