import json
import numpy as np
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value, LpStatus

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
    if LpStatus[prob.status] != 'Optimal' or sum(value(zi) * x_values[i] for i, zi in enumerate(z)) < min_value:
        # 如果没有找到最优解，或者解的总和小于 min_value，将所有 z 设置为 1
        return [1] * n
    
    # 提取结果
    optimized_z = [value(zi) for zi in z]
    return optimized_z

def vincent_algorithm_test():
    input_data = load_from_json("aircondition_array.json")
    min_value_data = load_from_json("min_power.json")
    
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

    save_to_json(output_data, "output.json")

    print("Optimized percentages:")
    for key, value in optimized_percentages.items():
        print(f"{key}: {value:.2f}")
    print(f"Total y value: {total_y:.2f}")
    print(f"Total zx value: {total_zx:.2f}")

if __name__ == "__main__":
    vincent_algorithm_test()


