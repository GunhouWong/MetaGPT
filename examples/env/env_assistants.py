import ast
import json
import re
from datetime import datetime

import fire

from metagpt.actions import Action
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.roles.role import RoleReactMode
from metagpt.team import Team


class GenerateEnvKnowledgeAnswer(Action):
    PROMPT_TEMPLATE: str = """Context: 
{context}

请根据 Context 回答 Human 的问题，Context 中不存在的信息请回答不知道:"""

    async def run(self, context):
        prompt = self.PROMPT_TEMPLATE.format(context=context)

        rsp = await self._aask(prompt)
        return ('针对 Human 的回答如下：\n'
                f'###\n{rsp}\n###')


class SearchEnvKnowledge(Action):

    async def run(self, context):

        return ("## 检索问题\n"
                f"{context[0].content}\n"
                "## 检索结果\n"
                "什么是碳监测?\n"
                "碳监测通过综合观测、结合数值模拟、统计分析等手段，获取温室气体排放强度、环境中浓度、生态系统碳汇等碳源汇状况及其变化趋势信息，为应对气候变化研究和管理提供服务支撑。主要监测对象为《京都议定书》和《多哈修正案》中规定控制的7种人为活动排放的温室气体，包括二氧化碳 (COz)、甲烷(CH+)、氧化亚氮(NzO)氢氟化碳(HFCs)、全氟化碳(PFCs) 、六氟化硫 (SFc) 和三氟化氮 (NFs) 。"
                )


class EnvKnowledgeAssistant(Role):
    name: str = '黄智识'
    profile: str = "环境质量知识助手"
    goal: str = '回答用户的一些环保相关的知识'
    constraints: str = '可以先使用 SearchEnvKnowledge 对知识进行检索，然后通过 GenerateEnvKnowledgeAnswer 生成回答'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._set_react_mode(RoleReactMode.REACT, 2)
        self._watch([AssignKnowledgeAssistant])
        self.set_actions([SearchEnvKnowledge, GenerateEnvKnowledgeAnswer])


class GenerateEnvBusinessDataAnswer(Action):
    PROMPT_TEMPLATE: str = """
    Context: {context}
    请根据 Context 回答 Human 的问题:
    """

    async def run(self, context):
        prompt = self.PROMPT_TEMPLATE.format(context=context)

        rsp = await self._aask(prompt)

        return rsp


class GenerateSql(Action):
    async def run(self, context):
        return (f'根据用户问题：{context[0].content}\n'
                "生成的数据查询SQL：\n"
                "```sql\n"
                "select water_temperature, datetime from t_water where id = '23' order by datetime desc limit 24\n"
                "```")


class ExecuteSql(Action):
    async def run(self, context):
        # todo 倒序遍历
        sql_content = next((c.content for c in context if '```sql' in c.content), None)
        if sql_content:
            pattern = r'```sql(.*?)```'
            sql_content = re.findall(pattern, sql_content, re.DOTALL)

        if not sql_content:
            return "不存在 SQL，无法执行。"

        return ("根据SQL查询到的数据如下：\n"
                """water_temperature,datetime
12.3,2024-06-04 00:00:00
13.7,2024-06-04 01:00:00
14.2,2024-06-04 02:00:00
15.5,2024-06-04 03:00:00
16.8,2024-06-04 04:00:00
17.2,2024-06-04 05:00:00
18.6,2024-06-04 06:00:00
19.1,2024-06-04 07:00:00
20.4,2024-06-04 08:00:00
21.8,2024-06-04 09:00:00
22.3,2024-06-04 10:00:00
23.7,2024-06-04 11:00:00
24.2,2024-06-04 12:00:00
25.4,2024-06-04 13:00:00
24.8,2024-06-04 14:00:00
23.5,2024-06-04 15:00:00
22.1,2024-06-04 16:00:00
21.6,2024-06-04 17:00:00
20.3,2024-06-04 18:00:00
19.9,2024-06-04 19:00:00
18.5,2024-06-04 20:00:00
17.0,2024-06-04 21:00:00
16.5,2024-06-04 22:00:00
15.2,2024-06-04 23:00:00""")


class EnvSqlDataAssistant(Role):
    name: str = '周sq'
    profile: str = "环境质量数据库查询助手"
    goal: str = "根据用户需求生成数据库查询SQL，再执行获得数据"
    constraints: str = ("1. 如果 Context 不存在SQL，选择 GenerateSql 进行生成 SQL\n"
                        "2. 如果 Context 中已经存在可执行 SQL，选择 ExecuteSql")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._set_react_mode(RoleReactMode.REACT, 2)
        self._watch([AssignEnvSqlDataAssistant])
        self.set_actions([GenerateSql, ExecuteSql])


class AssignEnvSqlDataAssistant(Action):
    async def run(self, context: str):
        return '使用SQL数据助手查询数据'


class ChartDataApiBase(Action):
    CHART_OPTIONS: str = ""
    PROMPT_TEMPLATE: str = """# 用户问题
{question}

# 需求
根据用户问题生成数据接口 Python 代码

# SQL
```sql
{sql}
```

# 提供函数
DBUtil.select(sql: str)
说明
        :param sql: SQL
        :return: list[dict]  dict 为每行的每个字段名和对应的值

# 生成数据结构
需要生成的图表为echarts, 其中接口返回的数据结构说明如下：
```ts
{options}
```


# 限制
返回的数据必须符合数据结构要求。
只返回函数体的代码即可，不需要定义函数名。
直接返回数据对象，不需要转换为json字符串。
函数名为 get_chart_data
数据库返回的日期类型为 datetime 对象，必要时需要转换为字符串"""

    def generate_sql(self):
        return "select water_temperature, datetime from t_water where id = '23' order by datetime desc limit 24"

    async def generate_chart_api_code(self, context, sql):
        prompt = self.PROMPT_TEMPLATE.format(question=context[0].content, sql=sql, options=self.CHART_OPTIONS)
        code = await self._aask(prompt)
        return code

    def extract_md_python_code(self, md: str):
        pattern = r'```python(.*?)```'
        code_str = re.findall(pattern, md, re.DOTALL)
        return code_str[0] if len(code_str) > 0 else None

    def extract_function(self, code_str, function_name):
        # 解析代码字符串为抽象语法树
        tree = ast.parse(code_str)

        # 遍历抽象语法树，查找目标函数
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                # 找到目标函数，返回其源代码字符串
                function_code = ast.get_source_segment(code_str, node)
                return function_code

        # 如果未找到目标函数，则返回空字符串或抛出异常等
        return ""

    def run_python_code(self, code):
        class DBUtil:
            @staticmethod
            def select(sql):
                return [
                    {
                        'water_temperature': 12.3,
                        'datetime': datetime.strptime('2024-06-04 00:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 13.7,
                        'datetime': datetime.strptime('2024-06-04 01:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 14.2,
                        'datetime': datetime.strptime('2024-06-04 02:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 15.5,
                        'datetime': datetime.strptime('2024-06-04 03:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 16.8,
                        'datetime': datetime.strptime('2024-06-04 04:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 17.2,
                        'datetime': datetime.strptime('2024-06-04 05:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 18.6,
                        'datetime': datetime.strptime('2024-06-04 06:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 19.1,
                        'datetime': datetime.strptime('2024-06-04 07:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 20.4,
                        'datetime': datetime.strptime('2024-06-04 08:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 21.8,
                        'datetime': datetime.strptime('2024-06-04 09:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 22.3,
                        'datetime': datetime.strptime('2024-06-04 10:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 23.7,
                        'datetime': datetime.strptime('2024-06-04 11:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 24.2,
                        'datetime': datetime.strptime('2024-06-04 12:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 25.4,
                        'datetime': datetime.strptime('2024-06-04 13:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 24.8,
                        'datetime': datetime.strptime('2024-06-04 14:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 23.5,
                        'datetime': datetime.strptime('2024-06-04 15:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 22.1,
                        'datetime': datetime.strptime('2024-06-04 16:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 21.6,
                        'datetime': datetime.strptime('2024-06-04 17:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 20.3,
                        'datetime': datetime.strptime('2024-06-04 18:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 19.9,
                        'datetime': datetime.strptime('2024-06-04 19:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 18.5,
                        'datetime': datetime.strptime('2024-06-04 20:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 17.0,
                        'datetime': datetime.strptime('2024-06-04 21:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 16.5,
                        'datetime': datetime.strptime('2024-06-04 22:00:00', '%Y-%m-%d %H:%M:%S')
                    },
                    {
                        'water_temperature': 15.2,
                        'datetime': datetime.strptime('2024-06-04 23:00:00', '%Y-%m-%d %H:%M:%S')
                    }
                ]
        g = {
            "DBUtil": DBUtil
        }
        exec(code, g)
        return g['result']

    def generate_chart(self, code):
        code = self.extract_md_python_code(code)
        code = self.extract_function(code, 'get_chart_data')
        result = self.run_python_code(code + "\nresult = get_chart_data()")
        print("接口代码：")
        print(code)
        print("代码生成数据")
        print(json.dumps(result, ensure_ascii=False))
        return '根据用户需求生成的图表 API：https://chart.bovo.com/data/1222232'

    async def run(self, context):

        sql = self.generate_sql()
        code = await self.generate_chart_api_code(context, sql)

        return self.generate_chart(code)


class GenerateLineChartDataApi(ChartDataApiBase):
    CHART_OPTIONS: str = """interface LineBarOptions {{
  title: {
    text: string // 标题
  },
  legend: {
    show: boolean  // 是否显示图例
    data: string[] // 图例的数据数组。数组项通常为一个字符串，每一项代表一个系列的 name。
  },
  tooltip: {
    show: boolean // 是否显示提示框
    trigger: 'axis' | 'none' // 'axis' 坐标轴触发，主要在柱状图，折线图等会使用类目轴的图表中使用。 'none' 什么都不触发。
  },
  xAxis: {{ // 直角坐标系 grid 中的 x 轴
    type: 'category' // 'category' 类目轴，适用于离散的类目数据。
    data: string[]  // 类目数据，在类目轴（type: 'category'）中有效。
  }},
  yAxis: {{ // 直角坐标系 grid 中的 y 轴
    type: 'value' // 'value' 数值轴，适用于连续数据。
  }},
  series: [
    {{
      name: string //  系列名称，用于tooltip的显示，legend 的图例筛选
      data: number[]  // 系列中的数据内容数组。数组项通常为具体的数据项。
      type: 'line' // 'line' 折线图
    }}
  ]
}}"""


class GenerateBarChartDataApi(ChartDataApiBase):
    CHART_OPTIONS: str = """interface LineBarOptions {{
      title: {
        text: string // 标题
      },
      legend: {
        show: boolean  // 是否显示图例
        data: string[] // 图例的数据数组。数组项通常为一个字符串，每一项代表一个系列的 name。
      },
      tooltip: {
        show: boolean // 是否显示提示框
        trigger: 'axis' | 'none' // 'axis' 坐标轴触发，主要在柱状图，折线图等会使用类目轴的图表中使用。 'none' 什么都不触发。
      },
      xAxis: {{ // 直角坐标系 grid 中的 x 轴
        type: 'category' // 'category' 类目轴，适用于离散的类目数据。
        data: string[]  // 类目数据，在类目轴（type: 'category'）中有效。
      }},
      yAxis: {{ // 直角坐标系 grid 中的 y 轴
        type: 'value' // 'value' 数值轴，适用于连续数据。
      }},
      series: [
        {{
          name: string //  系列名称，用于tooltip的显示，legend 的图例筛选
          data: number[]  // 系列中的数据内容数组。数组项通常为具体的数据项。
          type: 'bar' // 'bar' 柱状图
        }}
      ]
    }}"""


class GeneratePieChartDataApi(ChartDataApiBase):
    async def run(self, context: str):
        return """根据用户需求生成的接口代码如下：
```js
option = {
  title: {
    text: 'Referer of a Website',
    subtext: 'Fake Data',
    left: 'center'
  },
  tooltip: {
    trigger: 'item'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      name: 'Access From',
      type: 'pie',
      radius: '50%',
      data: [
        { value: 1048, name: 'Search Engine' },
        { value: 735, name: 'Direct' },
        { value: 580, name: 'Email' },
        { value: 484, name: 'Union Ads' },
        { value: 300, name: 'Video Ads' }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
};
```"""


class ChartDataApiCodeGenerator(Role):
    name: str = '张戴马'
    profile: str = "环境质量图表数据接口生成助手"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._set_react_mode(RoleReactMode.REACT, 1)
        self._watch([AssignChartDataApiGenerator])
        self.set_actions([GenerateLineChartDataApi, GenerateBarChartDataApi, GeneratePieChartDataApi])


class GenerateChart(Action):
    PROMPT_TEMPLATE: str = """# Context:
    {context}

# 要求
1. 请根据 Context 内容获取图表的名称，如果不存在，请根据内容生成。
2. 仅需要回答生成的名称，不需要添加其他的信息。"""

    async def run(self, context):
        prompt = self.PROMPT_TEMPLATE.format(context=context)

        rsp = await self._aask(prompt)
        return (f"已根据用户的提问生成图表：chart[{rsp}](1222232)")



class AssignChartDataApiGenerator(Action):
    async def run(self, context: str):
        return '使用环境质量图表数据接口生成助手'


class EnvChartAssistant(Role):
    name: str = '周图镖'
    profile: str = "环境质量图表生成助手"
    constraints: str = ("1. 如果未调用过 环境质量图表数据接口生成助手，选择 AssignChartDataApiCodeGenerator 生成数据 API\n"
                        "2. 如果已经存在图表数据 API，请选择 GenerateChart 进行生成图表")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self._set_react_mode(RoleReactMode.REACT, 2)
        self._watch([AssignChartAssistant, GenerateLineChartDataApi, GenerateBarChartDataApi, GeneratePieChartDataApi])
        self.set_actions([AssignChartDataApiGenerator, GenerateChart])


class QueryEmbeddedEnvBusinessData(Action):

    async def run(self, context: str):
        return """从2023年01月至12月统计结果看（2023年1月至12月），观澜河企坪断面分析项目、项目浓度如下：
(1)pH值,6.6
(2)溶解氧,7.87mg/L
(3)水温,27.0℃
(4)电导率,534.7mg/L
(5)化学需氧量,12.3mg/L
(6)高锰酸盐指数,3.0mg/L
(7)阴离子表面活性剂,0.03mg/L
(8)六价铬,0.002mg/L
(9)总氮,10.84mg/L
(10)氨氮,0.3mg/L
(11)总磷,0.118mg/L
(12)氰化物,0.0015mg/L
(13)氟化物,0.29mg/L
(14)硫化物,0.005mg/L
(15)石油类,0.018mg/L
(16)挥发酚,0.0002mg/L
(17)铜,0.0038mg/L
(18)锌,0.052mg/L
(19)硒,0.0002mg/L
(20)砷,0.0007mg/L
(21)镉,4e-05mg/L
(22)铅,0.00038mg/L
(23)汞,1.4e-05mg/L
(24)生化需氧量,1.3mg/L"""


class EnvBusinessDataAssistant(Role):
    name: str = "张小业"
    profile: str = "环境质量业务数据助手"
    goal: str = "根据用户的需求，先查询业务数据，再根据查询得到的业务数据进行生成问题的答案"
    constraints: str = '如果已经得到用户所需要的答案，请中止运行。'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._set_react_mode(RoleReactMode.REACT, 2)
        self._watch([AssignEnvBusinessAssistant])
        self.set_actions([QueryEmbeddedEnvBusinessData, GenerateEnvBusinessDataAnswer])


class FinalAnswerSpeaker(Role):
    name: str = "张发炎"
    profile: str = "问题回答助手"
    constraints: str = "跟图表相关的回答请选择 ChartFinalAnswer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([AssignFinalAnswer, GenerateChart])
        self.set_actions([FinalAnswer, ChartFinalAnswer])


class ChartFinalAnswer(Action):
    PROMPT_TEMPLATE: str = """假设你是一个图表回答助手，下面的信息已经包含可以回答用户的信息，请根据以下信息尽可能地回答Human的问题。


# 说明
1. 请假设自己可以输出图表。
2. 此标签格式为图表：`chart[描述](id)`，回答时直接带上 Context 中的图表标签，不要修改格式，不要忽略 id。
3. 图表标签会在输出后在前端协助你渲染成图表。

# Context
{context}"""

    async def run(self, context):
        prompt = self.PROMPT_TEMPLATE.format(context=context)

        rsp = await self._aask(prompt)
        return rsp


class FinalAnswer(Action):
    PROMPT_TEMPLATE: str = """Context: 
{context}

请根据 Context 回答 Human 的问题。"""

    async def run(self, context):
        prompt = self.PROMPT_TEMPLATE.format(context=context)

        rsp = await self._aask(prompt)
        return rsp


class AssignKnowledgeAssistant(Action):

    async def run(self, context: str):
        return '使用环境质量知识助手回答问题'


class AssignChartAssistant(Action):

    async def run(self, context: str):
        return '使用环境质量图表生成助手回答问题'


class AssignEnvBusinessAssistant(Action):

    async def run(self, context: str):
        return '使用环境质量业务数据助手回答问题'


class AssignFinalAnswer(Action):

    async def run(self, context):
        return "请回答问题"


class TaskManager(Role):
    name: str = "李工头"
    profile: str = "任务分配者"
    goal: str = '把用户输入的问题分解给对应的角色来处理。'
    constraints: str = ('1. 用户问的是常规的环保类知识，请选择 AssignKnowledgeAssistant\n'
                        '2. 用户问的是某个特定的河流，监测站，统计等信息，请选择 AssignEnvBusinessAssistant\n'
                        '3. 图表类的问题，未生成图表请选择 AssignChartAssistant 生成\n'
                        '4. history 中包含了 Human 问题的答案，请选择 AssignFinalAnswer')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self._set_react_mode(RoleReactMode.REACT, 3)

        self._watch([AssignQuestionToTaskManager, GenerateEnvKnowledgeAnswer,
                     GenerateEnvBusinessDataAnswer, ExecuteSql])

        self.set_actions([AssignKnowledgeAssistant, AssignEnvBusinessAssistant,
                          AssignChartAssistant, AssignFinalAnswer])


class AssignQuestionToTaskManager(Action):
    async def run(self, context):
        return '下达命令给任务管理者'


class TaskStarter(Role):
    name: str = '黄总'
    profile: str = "任务下派者"
    goal: str = '把用户输入的问题提供给任务管理者进行管理。'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([AssignQuestionToTaskManager])


async def main(idea: str = '观澜河企坪断面的水温是多少？'):
    # '观澜河企坪断面的水温是多少？'
    # '什么是碳监测？'
    # '近一日的茅洲河水温变化折线图？'
    # '近一日的茅洲河水温变化折线图？'
    # '提供近一日的茅洲河水温变化柱状图，x轴的时间格式为：yy-MM-dd HH'
    logger.info(idea)

    team = Team()
    team.hire(
        [
            TaskStarter(),
            TaskManager(),
            EnvKnowledgeAssistant(),
            EnvBusinessDataAssistant(),
            EnvSqlDataAssistant(),
            EnvChartAssistant(),
            ChartDataApiCodeGenerator(),
            FinalAnswerSpeaker(),
        ]
    )

    team.invest(investment=3)
    team.run_project(idea)
    his = await team.run(n_round=10)
    print(his)


if __name__ == "__main__":
    fire.Fire(main)

