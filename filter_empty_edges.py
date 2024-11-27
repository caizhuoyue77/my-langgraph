import pandas as pd

# 输入和输出文件路径
input_file = "data/deepseek_edges.csv"  # 替换为您的文件路径
output_file = "data/deepseek_edges_filtered.csv"  # 输出文件路径

# 读取 CSV 文件
df = pd.read_csv(input_file)

# 过滤掉 dependent_parameters 为 [] 的行
filtered_df = df[df['dependent_parameters'] != '[]']

# 将过滤后的数据保存到新的 CSV 文件
filtered_df.to_csv(output_file, index=False)

print(f"过滤完成，结果已保存到 {output_file}")