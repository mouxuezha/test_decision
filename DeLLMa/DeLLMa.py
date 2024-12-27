# 这个就用来复现论文里那个DeLMMa了，原则上所有和大模型交互的东西都放在这里面。

import os.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Optional, Dict, List, Tuple, Callable
from text_transfer.text_transfer import text_transfer
from templates.submision import submission, submission_type_list
class DeLLMa():
    def __init__(self):
        self.text_transfer= text_transfer()
        self.utility_prompt = self.text_transfer.prepare_utility_prompt()
    
    def set_utility_prompt(self, utility_prompt: str):
        self.utility_prompt = utility_prompt
        pass 
    
    def get_action_choice(self):
        # 这个原则上得从库里面读取，现在嘛先不管了。
        
        # 得是任务类型加上一些参数，才是action 

        # 参加单位：
        unit_type = ["坦克和无人突击车", "自行迫榴炮", "无人机和巡飞弹", "所有地面装备"]

        # 出击方向
        direction = ["偏东", "中路", "偏西"]

        #子任务类型：
        submission_type_list = submission_type_list

        # 然后来个巨大的循环
        action_choice = [] 
        for unit_type in unit_type:
            for direction in direction:
                for submission_type in submission_type_list:
                    action_str = "类型：" + submission_type + "，参加单位：" + unit_type + "，出击方向：" + direction
                    action_choice.append(action_str)
        return action_choice

    def action_generation(self, unit_type:str, direction:str, submission_type:str):
        # 这个是生成action的函数，里面应该包含一些和模型交互的部分。
                    action = submission(unit_type, direction, submission_type)
                    yield action


    def state_enumeration(self,G:str):
        # G是对应里面的用户目标。具体有几个备选的state恐怕得看是什么任务。
        
        # 先定一下需要哪些维度，以及各个维度需要离散成什么。
        # 原来论文里面的这步离散貌似是喂了大模型做的，在咱这个里面，感觉还是直接来比较好。
        state_enmueration_dict = {"敌方经度":["偏西","靠中间","偏东"],
                                  "敌方纬度":["偏北","靠中间","偏南"],
                                  "敌方聚集程度":["分散","一般","集中"],
                                  "我方经度":["偏西","靠中间","偏东"],
                                  "我方纬度":["偏北","靠中间","偏南"],
                                  "我方聚集程度":["分散","一般","集中"]}
        states_list = [] 
        
        return states_list
    
    def state_forecasting(self, theta_j:str, C:str):
        # 这里的C是上下文，原文里的研究报告那些。一定程度上对应以前的the embrace
        # 上下文里应该描述敌方战术，然后让大模型来进行态势的预测。

        pi_thetaj_C = 0.114514 # 这个是概率分布，对应原文里的pi(theta_j|C)
        return pi_thetaj_C
    
    def U_func_elicitation(self, theta_j:str, a_i:str,C:str):
        # 这个是最关键的评分了，评估出效用函数。
        U_func_value = 1145
        return U_func_value
    
    def maximize_Utility(self, theta_j:str, a_i:str,U_theta_a_list:list):
        # 这个是最大化效用函数的，选出一个特定的Action来最大化效用，至此就决定出哪个好了。
        a_star = 1145
        return a_star
    
    def prepare_dellma_prompt(self) -> str | List[str]:
        context = self.text_transfer.prepare_context()  # how the context is prepared
        action_choice = self.get_action_choice()
        actions = self.text_transfer.prepare_actions(action_choice)  # how the actions are enumerated
        state = self.text_transfer.prepare_state_prompt()  # how the state-action pair is enumerated
        preference = self.text_transfer.prepare_preference_prompt()  # how the preference is elicited

        DeLLMa_prmpt = context + "\n\n" + self.utility_prompt + "\n\n" + actions + "\n\n" + state + "\n\n" + preference

        return DeLLMa_prmpt
