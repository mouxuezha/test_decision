# 在这里面实现模块2，输入态势、意图和先验知识，输出多个方案，每个方案里面是子任务序列。

class mission_arrange:
    def __init__(self, status, intent, prior_knowledge):
        self.status = status
        self.intent = intent
        self.prior_knowledge = prior_knowledge

    def get_one_plan(self,**kargs):
        # 在这里实现模块2的具体逻辑。
        pass