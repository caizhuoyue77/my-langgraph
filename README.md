测试脚本从main进去

运行命令：
python main.py --model qwen2.5:7b --method ours --temperature 0.7 --dataset_path "dataset.json" --output_path "output_results.jsonl"

测试10条从G1里面搜到的数据
python main.py --model qwen2.5:7b --method cot --dataset_path "/Users/caizhuoyue/Desktop/my-langgraph/data/instruction/G1_query_sample_10.json" --output_path "vanilla_results_10.jsonl"

python main.py --model qwen2.5:7b --method ours --dataset_path "/Users/caizhuoyue/Desktop/my-langgraph/data/instruction/G3_query.json" --output_path "ours@3_results_10.jsonl"
