# my-langgraph

## 启动方式：
1. conda activate langgraph
2. fastapi dev api.py（把后端开起来）
3. streamlit run chatbot.py（把前端开起来）

## Todo
[x] 1. 模型替换为qwen（换成Qwen的模型了，但是不是本地的Qwen模型，也没法指定是哪个版本的Qwen）
[x] 2. 修改步骤为，先出编排结果，确认后再执行
[x] 3. 设计好plan和execute的API格式，然后记录到文档里
[ ] 4. 调整好执行API的流程API，如何识别参数和如何执行
[x] 5. 添加了一个非常直接的cache，如果某个task/query在之前是输入过的，那么就直接返回之前的/chat的结果
[ ] 6. 添加高德地图的API
[ ] 7. 动态配参数
[ ] 8. 添加可视化的部分
[ ] 9. 添加可交互式编排的部分


## 模型改成Qwen的几个注意事项

1. 现在的Qwen是通过`from langchain_community.llms import Tongyi`里面的Tongyi来实现的，然后`model = Tongyi()`;后面得改成通过API调用跑在我们服务器本地的Qwen模型
2. Tongyi返回的result格式和OpenAI不一样，要把所有代码里面的result.content改为result


## 当务之急：
1. 弄出图谱
2. 设计一个需要调用多个API的case（旅行线路）
   1. （使用gpt-3.5的效果很好，改为qwen试一下）我想在xx时间去xx地点旅游，请你帮我查一下机票/酒店，并查询当地天气。
      1. 机票API
      2. 酒店API
      3. 天气预报/当前天气API
   2. （路线规划的case）
3. 做一个能demo的东西：
   1. ~~llm来规划api~~
   2. 然后把规划好得到的api调用路径可视化展示给用户，并进行确认
   3. llm来配参数（省略）
   4. ~~调用api得到结果~~
   5. ~~llm总结所有的api调用结果，然后输出~~
4. 拆分步骤：
   1. 用langgraph做规划
   2. 写代码根据langgraph的编排结果依次执行api并存储结果
   3. 用lm来归纳结果作为输出


## 现有问题：
1.知识图谱不知道如何构建和如何辅助
解决方案：
1.1 看论文，抄他们的
1.2 胡诌几个方案先做着
比如用语义节点连接api
老师说有一些论文里有那种旅游编排的知识图谱？去寻找一下。

2.react格式比较慢/输出很复杂/容易不结束或者选错api
解决方案：
不用react，改为restGPT的格式或者plan and execute，反正改一个方式
同时尝试flash attention来加速这个推理过程

3.配参数难配，只能配1个参数，多个参数效果不好
解决方案：先这样，暂时不管了
要不要试一试关键词识别/实体识别？

4.获得的response太长太抽象，占用很多token和推理时间
解决方案：针对每个response加一个处理函数，这样就可以有效缩短response的内容，不会超出token长度。
（不大好但是也行）

5.“编排”内容太少
设计一个pipeline，在知识图谱+llm编排后，给用户呈现编排结果，让用户进行确认或者再次选择编排顺序。
然后执行整个pipeline。

6.整体代码又臭又长，后期debug等都会比较困难
1.舍弃langchain ctct，用langgraph+streamlit自己搭建


## 技术亮点（待实现）

1. 训练一个分类器，自动识别大致的API调用类别，然后提供一个API选择的方向。
2. cache功能（对于之前发送过的类似的请求，可以直接从我们的cache里面找到执行成功的编排方案）
3. 自动添加API功能（可以用户自己添加）
4. self-reflection功能（可以反思/总结自己的编排结果，然后给出改进意见）
5. 可视化功能（可以把编排结果可视化展示给用户，用户可以进行编辑，也可以完全从头规定执行顺序）