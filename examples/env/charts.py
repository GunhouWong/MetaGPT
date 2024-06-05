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


class GenerateChart(Action):
    async def run(self, context):
        return ("根据用户问题，生成的图表链接如下：\n"
                "https://chart.bovo.com/1222232")


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
        return 'https://chart.bovo.com/1222232'

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
    # constraints: str = ("生成步骤：GenerateSql -> GenerateXXXChartDataApiCodeBySql -> GenerateChartDataApiByCode\n"
    #                     "1. if conversation records no SQL，please select GenerateSql\n"
    #                     "2. if conversation records exist SQL，no api code，必须根据用户需求生成对应的图表API代码\n"
    #                     "3. if conversation records exist api code，please select GenerateChartDataApiByCode to generate Api")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._set_react_mode(RoleReactMode.REACT, 1)
        self._watch([AssignChartDataApiCodeGenerator])
        self.set_actions([GenerateLineChartDataApi, GenerateBarChartDataApi, GeneratePieChartDataApi])


class AssignChartDataApiCodeGenerator(Action):
    async def run(self, context: str):
        return '使用环境质量图表数据接口生成助手回答问题'


class AssignChartAssistant(Action):

    async def run(self, context: str):
        return '使用环境质量图表生成助手回答问题'


class EnvChartAssistant(Role):
    name: str = '周图镖'
    profile: str = "环境质量图表生成助手"
    constraints: str = ("1. 选择 AssignChartDataApiCodeGenerator 进行生成数据 API\n"
                        "3. 如果已经有 API，请选择 GenerateChart 进行生成图表")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self._set_react_mode(RoleReactMode.REACT, 2)
        self._watch([AssignChartAssistant, GenerateLineChartDataApi, GenerateBarChartDataApi, GeneratePieChartDataApi])
        self.set_actions([AssignChartDataApiCodeGenerator, GenerateChart])


class TaskStarter(Role):
    name: str = '黄总'
    profile: str = "任务下派者"
    goal: str = '请选择 AssignChartAssistant'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([AssignChartAssistant])


async def main(idea: str = '近一日的茅洲河水温变化折线图？显示图例'):
    # '近一日的茅洲河水温变化折线图？'
    # '提供近一日的茅洲河水温变化柱状图，x轴的时间格式为：yy-MM-dd HH'
    logger.info(idea)

    team = Team()
    team.hire(
        [
            TaskStarter(),
            EnvChartAssistant(),
            ChartDataApiCodeGenerator(),
        ]
    )

    team.invest(investment=1)
    team.run_project(idea)
    his = await team.run(n_round=2)
    print(his)


if __name__ == "__main__":
    fire.Fire(main)

