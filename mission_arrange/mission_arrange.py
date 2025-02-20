# 在这里面实现模块2，输入态势、意图和先验知识，输出多个方案，每个方案里面是子任务序列。
import os.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from templates.mission_plan import mission_plan
from text_transfer.stage_prompt import StagePrompt
from text_transfer.text_transfer import *
import pickle 
import dill 
import time

class mission_arrange:
    def __init__(self, status="none", intent="none", prior_knowledge="none",communicator="none"):
        self.status = status
        self.intent = intent
        self.prior_knowledge = prior_knowledge
        self.input_prompt = StagePrompt()
        self.index = 1
        self.plan_list = [] # 这个还是得存的嘛。
        self.communicator = communicator # 把交互那个的引用传进来，在适当的时候print一些东西到前端，反正异步的。
        self.text_transfer = text_transfer()

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
        if self.index == 0:
            num_saved = 1
        else:
            num_saved = 0
        
        jieguo_location = r"auto_test\jieguo_DeLLMa" + str(self.index) + r".pkl"
        
        one_plan.set_config_mission_plan(num_saved=num_saved, jieguo_location =jieguo_location) # 设定一些不从0开始计算的机制。

        # 好，先把DeLLMa润起来看Prompt好了，冲就完事儿了。
        # 要是后面要搞人机交互的话，就是在每一次decide前加一些读取命令、操作submissionlist的东西。
        # next_submission = one_plan.decide_next_submission()
      
        time_now = 0 
        while(time_now<5000):
            # 然后继续，这次主要解决的是在已经生成了一部分的基础上，继续生成。主要需要改的是context部分。
            time_now = one_plan.check_time()
        # for i in range(3):
            # 最理想的其实应该是检测submission的时间来决定是不是结束，以及更新那些东西。
            next_submission = one_plan.decide_next_submission()
            next_report_str = one_plan.describe_last_submission()
            
            if not(self.communicator == "none"):
                self.communicator.send_response(self.text_transfer.response_wrap(next_report_str)) # 这个直接传到前端去，并且保持兼容性。
            # 这个别每一步存。由于兼容性问题，存的时候要把docx那部分删了，所以每一步都存的话会影响docx的输出。
            # 但是在调试的时候可以开了它，这样就容易给出结果。
            # self.save_one_plan(one_plan,"jieguo"+str(self.index))
        
        self.save_one_plan(one_plan,"jieguo"+str(self.index))
        self.plan_list.append(one_plan)
        return one_plan
    
    def main_loop(self, plan_num = 3):
        # 在这里实现模块2的主循环，不断生成方案，直到满足数量为止。
        # plan_num = plan_num
        start_time = time.time()
        for index in range(plan_num):
            # index = index + 1 # 跳过第一个，因为第一个已经生成出来了。
            users_goal = self.input_prompt.get_stage_prompt_plan(index)
            jieguo = self.get_one_plan(users_goal=users_goal, index=index)
            self.plan_list.append(jieguo)
        pass
        end_time = time.time()
        print("mission_arrange.main_loop,本轮"+str(plan_num)+"个方案，生成方案耗时：", end_time - start_time, "秒")
        return self.plan_list
    
    def main_loop_debug(self, plan_num = 3):
        # 这个是用来调试的.
        # name0 = "jieguo0"
        # plan0 = self.load_one_plan(name0)
        # for index in range(plan_num):
        #     # 直接重复几次，复制几个就好了嘛
        #     self.plan_list.append(plan0)
        
        for i in range(plan_num):
            time.sleep(1.14514) # 这里延时倒是也没问题，但是还不够，里面也还得延时。
            name_i = "jieguo" + str(i)
            plan_i = self.load_one_plan(name_i)
            plan_i = self.add_ECM_submmission(plan_i)
            # 这里得来一个发送方案生成过程到前端的东西，展示就拿这个展示了可能。
            self.report_one_plan(plan_i)
            self.plan_list.append(plan_i)

        return self.plan_list
    
    def report_one_plan(self,plan_input:mission_plan):
        # 这个就是发送方案生成过程到前端的东西。
        geshu = len(plan_input.submission_list)
        for i in range(geshu):
            # 这里也是需要延迟的，不然方案一下全出来还是有点吓人的
            time.sleep(1.14514*2)
            index = i 
            next_report_str = plan_input.describe_last_submission(index)
            if not(self.communicator == "none"):
                self.communicator.send_response(self.text_transfer.response_wrap(next_report_str)) # 这个直接传到前端去，并且保持兼容性。
            # self.save_one_plan(plan_input,"jieguo"+str(self.index)) # 本来就是读取出来的，这里就不要存了。

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
            plan.DeLLMa.model_communication = "为了保存整个对象，model_communication功能先关了。"
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
    
    def add_ECM_submmission(self,plan:mission_plan):
        # 增加ECM子任务。这个直接放这里好了，看看成色。
        plan_new = copy.deepcopy(plan)
        submission_list_new = [] 
        for submission_single in plan.submission_list:
            submission_list_new.append(submission_single)
            if(submission_single.force_arrange == "装甲车等其他地面力量"):
                # 那就是追加分配电磁干扰任务
                submission_single_new = self.submission_single_to_ECM(submission_single,index=len(submission_list_new))
                submission_list_new.append(submission_single_new)
        plan_new.submission_list = submission_list_new
        return plan_new

    def submission_single_to_ECM(self,submission_single,index=0):
        # 修改生成电子战方案。原则上不应该放这里的，不过不管了下次一定。
        submission_single_new = copy.deepcopy(submission_single)
        model_selected, submodel_selected = self.text_transfer.generate_ECM_model()

        submission_single_new.id_str = "电子对抗" + str(index)
        submission_single_new.type_str = model_selected
        submission_single_new.force_arrange = "电子干扰车"
        submission_single_new.target_str = submodel_selected
        
        return submission_single_new

if __name__ == "__main__":
    # 在这里实现模块2的测试代码，可以调用get_one_plan函数生成方案，并输出方案内容。
    flag = 1
    if flag == 0:
        plan_num = 3
        shishi = mission_arrange()
        shishi.main_loop(plan_num = plan_num)
        print("方案智能生成分系统，已完成一轮方案生成，本轮包含"+str(plan_num)+"个方案。")
    elif flag == 1:
        shishi = mission_arrange()
        # 加载进来看看成色。
        shishi.main_loop_debug(plan_num=3)
    # shishi = mission_arrange()
    # # input_prompt = StagePrompt()
    # # index = 1
    # # jieguo1 = shishi.get_one_plan(input_prompt.get_stage_prompt_plan(index))
    # # shishi.save_one_plan(jieguo1,"jieguo1")
    # # jieguo2 = shishi.load_one_plan("jieguo1")
    # shishi.main_loop(plan_num = 3)
    # print("完事儿了一(?)次，看看成色。")