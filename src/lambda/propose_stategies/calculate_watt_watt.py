import json
import CoolProp.CoolProp as CP
from scipy.constants import minute

DEFAULT_PRESSURE = 101325  # 标准大气压，帕斯卡

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
    required_power = required_energy / (target_time_minutes * minute)  # 瓦特

    # 打印调试信息
    print(f"Current enthalpy: {current_enthalpy:.2f} J/kg")
    print(f"Target enthalpy: {target_enthalpy:.2f} J/kg")
    print(f"Density: {density:.2f} kg/m³")
    print(f"Required energy: {required_energy:.2f} J")
    
    return required_power * multiple_avlue

def calculate_watt():
    input_data = load_from_json("input.json")
    required_power = calculate_cooling_power(input_data)
    output_data = {"required_power": required_power}
    save_to_json(output_data, "min_power.json")

    print(f"Required cooling power: {required_power:.2f} W")

if __name__ == "__main__":
    calculate_watt()


