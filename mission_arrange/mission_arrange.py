# 在这里面实现模块2，输入态势、意图和先验知识，输出多个方案，每个方案里面是子任务序列。
import os.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from templates.mission_plan import mission_plan

class mission_arrange:
    def __init__(self, status="none", intent="none", prior_knowledge="none"):
        self.status = status
        self.intent = intent
        self.prior_knowledge = prior_knowledge

    def get_one_plan(self,**kargs):
        # 在这里实现模块2的具体逻辑，根据参数生成出一个方案，返回一个方案对象。
        one_plan = mission_plan()

        # 好，先把DeLLMa润起来看Prompt好了，冲就完事儿了。
        one_plan.decide_next_submission()

        return one_plan
    
    def main_loop(self):
        # 在这里实现模块2的主循环，不断生成方案，直到满足数量为止。
        pass

if __name__ == "__main__":
    # 在这里实现模块2的测试代码，可以调用get_one_plan函数生成方案，并输出方案内容。
    shishi = mission_arrange()
    jieguo1 = shishi.get_one_plan()