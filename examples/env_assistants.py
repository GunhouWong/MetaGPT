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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([GenerateSql, ExecuteSql])


class AssignEnvSqlDataAssistant(Role):
    async def run(self, context: str):
        return '使用SQL数据助手查询数据'


class EnvChartAssistant(Role):
    name: str = '周图镖'
    profile: str = "环境质量图表生成助手"


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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([AssignFinalAnswer])
        self.set_actions([FinalAnswer])


class FinalAnswer(Action):
    PROMPT_TEMPLATE: str = """Context: 
{context}

请根据 Context 回答 Human 的问题:
    """

    async def run(self, context):
        prompt = self.PROMPT_TEMPLATE.format(context=context)

        rsp = await self._aask(prompt)
        return rsp


class AssignKnowledgeAssistant(Action):

    async def run(self, context: str):
        return '使用环境质量知识助手回答问题'


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
                        '2. 用户问的是某个特定的河流，监测站，统计，图表等信息，请选择 AssignEnvBusinessAssistant\n'
                        '3. Context 中包含了 Human 问题的答案，请选择 AssignFinalAnswer')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self._set_react_mode(RoleReactMode.REACT, 3)
        self._watch([AssignQuestionToTaskManager, GenerateEnvKnowledgeAnswer, GenerateEnvBusinessDataAnswer])
        self.set_actions([AssignKnowledgeAssistant, AssignEnvBusinessAssistant, AssignFinalAnswer])


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
    # '二氧化碳是什么？'
    # '什么是碳监测？'
    # '近一日的茅洲河水温变化折线图？'
    logger.info(idea)

    team = Team()
    team.hire(
        [
            TaskStarter(),
            TaskManager(),
            EnvKnowledgeAssistant(),
            EnvBusinessDataAssistant(),
            FinalAnswerSpeaker(),
        ]
    )

    team.invest(investment=3)
    team.run_project(idea)
    his = await team.run(n_round=10)
    print(his)


if __name__ == "__main__":
    fire.Fire(main)

