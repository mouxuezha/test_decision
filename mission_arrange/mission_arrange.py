# 在这里面实现模块2，输入态势、意图和先验知识，输出多个方案，每个方案里面是子任务序列。
import os.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from templates.mission_plan import mission_plan
from text_transfer.stage_prompt import StagePrompt
import pickle 
import dill 

class mission_arrange:
    def __init__(self, status="none", intent="none", prior_knowledge="none"):
        self.status = status
        self.intent = intent
        self.prior_knowledge = prior_knowledge
        self.input_prompt = StagePrompt()
        self.index = 1
        self.plan_list = [] # 这个还是得存的嘛。

    def get_one_plan(self,**kargs):
        # 引入用于实现多方案的Prompt。
        if "users_goal" in kargs:
            users_goal = kargs["users_goal"]
        else:
            users_goal = ""
        
        if "index" in kargs:
            self.index = kargs["index"]
        else:
            self.index = 0

        # 在这里实现模块2的具体逻辑，根据参数生成出一个方案，返回一个方案对象。
        one_plan = mission_plan()

        # 然后给它设定进去。
        if len(users_goal)>1:
            # 那就是里面有东西。
            one_plan.set_users_goal(users_goal)

        # 好，先把DeLLMa润起来看Prompt好了，冲就完事儿了。
        # 要是后面要搞人机交互的话，就是在每一次decide前加一些读取命令、操作submissionlist的东西。
        next_submission = one_plan.decide_next_submission()
      
        time_now = 0 
        while(time_now<5000):
            # 然后继续，这次主要解决的是在已经生成了一部分的基础上，继续生成。主要需要改的是context部分。
            time_now = one_plan.check_time()
        # for i in range(3):
            # 最理想的其实应该是检测submission的时间来决定是不是结束，以及更新那些东西。
            next_submission = one_plan.decide_next_submission()
            # 这个别每一步存。由于兼容性问题，存的时候要把docx那部分删了，所以每一步都存的话会影响docx的输出。
            # 但是在调试的时候可以开了它，这样就容易给出结果。
            # self.save_one_plan(one_plan,"jieguo"+str(self.index))
        
        self.save_one_plan(one_plan,"jieguo"+str(self.index))
        self.plan_list.append(one_plan)
        return one_plan
    
    def main_loop(self, plan_num = 3):
        # 在这里实现模块2的主循环，不断生成方案，直到满足数量为止。
        # plan_num = plan_num
        for index in range(plan_num):
            users_goal = self.input_prompt.get_stage_prompt_plan(index)
            jieguo = self.get_one_plan(users_goal=users_goal, index=index)
        pass

    def save_one_plan(self,plan:mission_plan,name:str):
        # 这个就是跑完一次存一下看看成色。
        if ".pkl" in name:
            pass 
        else:
            name = name + ".pkl"
        location_one_plan = "auto_test/" + name 
        # docx那个不能序列化，所以还得想办法改改。
        try:
            plan.DeLLMa.output_docx = "为了保存整个对象，docx功能先关了。"
        except:
            pass

        # 如果有同名文件存在就覆盖。但是现在本来就是覆盖了应该。
        # self.plan_list.append(plan) # 不要搞功能嵌套，这个放到外面去
        with open(location_one_plan, 'wb') as f:
            dill.dump(plan, f)
    
    def load_one_plan(self,name:str):
        # 这个是读取存下来的。
        if ".pkl" in name:
            pass 
        else:
            name = name + ".pkl"

        location_one_plan = "auto_test/" + name
        with open(location_one_plan, 'rb') as f:
            plan = dill.load(f)

        return plan

if __name__ == "__main__":
    # 在这里实现模块2的测试代码，可以调用get_one_plan函数生成方案，并输出方案内容。
    shishi = mission_arrange()
    # input_prompt = StagePrompt()
    # index = 1
    # jieguo1 = shishi.get_one_plan(input_prompt.get_stage_prompt_plan(index))
    # shishi.save_one_plan(jieguo1,"jieguo1")
    # jieguo2 = shishi.load_one_plan("jieguo1")
    shishi.main_loop(plan_num = 2)
    print("完事儿了一(?)次，看看成色。")