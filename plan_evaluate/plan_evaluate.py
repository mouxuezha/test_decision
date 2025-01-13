# 这个是有了一些方案之后，预计用来实现方案评估的模块。毫无疑问，第一件事儿是把方案都读进来
# 或许要考虑做个基类，以后多种评价的玩法就直接从这个基类去继承或者去什么，就好一些。
# 软件工程化完全一坨，现在完全是要个什么功能就加个什么东西出来。不过在git加持下倒是至少不会失控。
import os.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import dill 
# from templates.mission_plan import mission_plan # 模块不用重新导入，它dill加载的时候会自己导入。但是这就意味着路径里得有才对，否则不对。有点变成C++的依赖项那种去了。长此以往必然屎山，得动动脑子想想怎么搞。
# from text_transfer.stage_prompt import StagePrompt

class plan_evaluate:
    def __init__(self):
        # 现阶段还不需要实现太复杂的功能，先能读进来看看成色再说
        self.index = 0
        self.plan_list = [] # 这个还是得存的嘛。
        self.plan_location_list = [] 
        pass

    def load_plans(self,plan_location_list:list):
        # 这个就是读入方案了，plan_location_list里面是各个方案的路径。
        self.plan_location_list = plan_location_list
        for i in range(len(self.plan_location_list)):
            plan_single = self.load_plan(self.plan_location_list[i])
            self.plan_list.append(plan_single)
            # try:
            #     plan_single = self.load_plan(self.plan_location_list[i])
            #     self.plan_list.append(plan_single)
            # except:
            #     print("plan {} load failed".format(i))
        
        print("plan_evaluate: finish load plans.")

    def load_plan(self,plan_location:str):
        # 这个就是读入单个方案了。
        with open(plan_location, 'rb') as f:
            plan = dill.load(f)
        # self.plan_list.append(plan)
        return plan

if __name__ == "__main__":
    plan_location_list = [] 
    plan_location_list.append(r"E:/EnglishMulu/text_decision/auto_test/temp/jieguo0.pkl")
    plan_location_list.append(r"E:/EnglishMulu/text_decision/auto_test/temp/jieguo1.pkl")
    plan_location_list.append(r"E:/EnglishMulu/text_decision/auto_test/temp/jieguo2.pkl")
    shishi_evaluate = plan_evaluate()
    shishi_evaluate.load_plans(plan_location_list)