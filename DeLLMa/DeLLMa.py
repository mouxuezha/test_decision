# 这个就用来复现论文里那个DeLMMa了，原则上所有和大模型交互的东西都放在这里面。

import os.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json

from typing import Optional, Dict, List, Tuple, Callable
from text_transfer.text_transfer import *
from templates.submision import submission, submission_type_list
from model_communication.model_comm_langchain import ModelCommLangchain

class DeLLMa():
    # 算了，和大模型互动的也闭环在这里面好了。

    def __init__(self):
        self.text_transfer= text_transfer()
        self.utility_prompt = self.text_transfer.prepare_utility_prompt(human_intent = "none")
        self.belief2score = belief2score
        self.model_communication = ModelCommLangchain(model_name="qianfan",Comm_type="DeLLMa",role="none")
        self.config_assist = {} # 这个用来实现一些边缘的功能

    def set_utility_prompt(self, utility_prompt: str):
        self.utility_prompt = utility_prompt
        pass 
    
    def get_action_choice(self):
        # 这个原则上得从库里面读取，现在嘛先不管了。
        
        # 得是任务类型加上一些参数，才是action 

        # 参加单位：
        # unit_type = ["坦克和自行迫榴炮", "无人机和巡飞弹", "所有地面装备"]
        unit_type = ["坦克和自行迫榴炮", "所有地面装备"]

        # 出击方向
        direction_list = ["偏东", "偏西"]

        #子任务类型：
        submission_type_list1 = submission_type_list

        # 然后来个巨大的循环
        action_choice = [] 
        for unit_type in unit_type:
            for direction in direction_list:
                for submission_type in submission_type_list1:
                    action_str = "类型：" + submission_type + "，参加单位：" + unit_type + "，出击方向：" + direction
                    flag_pass = self.check_action_choice(unit_type,submission_type)
                    if flag_pass:
                        action_choice.append(action_str)
        return action_choice
    
    def check_action_choice(self,unit_type,submission_type):
        # 把那种一眼顶针的过滤掉。这个是高度定制化的，子任务要是变了，这个得好好看好好学。
        flag_pass = True
        if unit_type == "无人机和巡飞弹" and "陆地" in submission_type :
            flag_pass = False
        if not(unit_type == "无人机和巡飞弹") and "空中" in submission_type :
            flag_pass = False
        if not(unit_type == "所有地面装备") and "干扰" in submission_type :
            flag_pass = False
        if submission_type == "none":
            flag_pass = False

        return flag_pass 

    def get_state_candidates(self):
        # 这个是给出可能出现的state组合。也是先生成然后再筛选。
        state_enmueration_dict = self.text_transfer.state_enmueration_dict 
        index_state = 0 
        state_json = {} 
        state_value_list = [] 
        state_name_list = []
        for state_name in state_enmueration_dict.keys():
            state_value_single = state_enmueration_dict[state_name]
            state_value_list.append(state_value_single)
            state_name_list.append(state_name)
        
        # 然后再开始循环，恐怕是比较阳间的
        for i in range(len(state_value_list[0])**len(state_value_list)):
            state_candidate_single = {} 
            
            for j in range(len(state_name_list)):
                index_tmp = (i // (len(state_value_list[0])**(j))) % (len(state_value_list[0]))
                state_candidate_single[state_name_list[j]] = state_value_list[j][index_tmp]
            flag_check = self.check_state_candidate(state_candidate_single)
            if flag_check:
                name = "状态" + str(index_state)
                state_json[name] = state_candidate_single
                index_state += 1

        return state_json

    def check_state_candidate(self,state_candidate_single):
        # 先check掉一些不对的。
        flag_check = True
        if state_candidate_single["敌方经度"] != self.text_transfer.state_enmueration_dict["敌方经度"][1]:
            flag_check = False
        if not("北" in state_candidate_single["敌方纬度"]):
            flag_check = False
        if not("南" in state_candidate_single["我方纬度"]):
            flag_check = False
        if state_candidate_single["我方聚集程度"] != self.text_transfer.state_enmueration_dict["我方聚集程度"][2]:
            flag_check = False
        if state_candidate_single["敌方聚集程度"] != self.text_transfer.state_enmueration_dict["敌方聚集程度"][1]:
            flag_check = False
        return flag_check


    def check_state_candidates(self):
        # 这个是筛选state，把不要的的筛掉。
        pass

    def state_enumeration_and_forecasting(self,G:str):
        # G是对应里面的用户目标。具体有几个备选的state恐怕得看是什么任务。
        
        # 先定一下需要哪些维度，以及各个维度需要离散成什么。
        context = self.text_transfer.prepare_context()
        context += "这个过程中你需要做的第一步，是生成一个信度分布，描述敌我双方战场态势的可能状态。"

        state_discription = self.text_transfer.state_discription_dict
        state_str = self.text_transfer.prepare_state_prompt(state_discription)
        belief_list_str = self.text_transfer.prepare_belief_prompt()

        state_enumeration_prompt = context + state_str
        state_enumeration_prompt += "\n 每个键都应该映射到一个有3个键的JSON对象，每个键都是一个描述状态变量的字符串。这些键应该包含状态变量最可能的三个取值，每个键应该映射到你对它的信度，以自然语言表示。如果这些变量是连续变量，你应该将它们离散成三种值。"

        state_enumeration_prompt += "你仅应该从以下列表中挑选信度的描述，" + belief_list_str + "例如，若其中一个状态变量是“敌方经度”，然后三个最可能的取值是“靠中间”、“偏西”、“偏东”，那么你的回复应该是如下格式：\n        {\n            \"敌方经度\" : {\n                \"靠中间\" : \"很可能\",\n                \"偏西\" : \"有点可能\",\n                \"偏东\" : \"不太可能\"\n            },\n        }"

        # 好，然后和大模型交互一圈，看看情况。这里其实应该已经算是forecasting了，
        # print(state_enumeration_prompt)
        # response_str = self.model_communication.communicate_with_model(state_enumeration_prompt)
        response_str = text_DeLLMa_state
        if self.config_assist["num_round"]>1:
            # 那说明是第二次跑到这里，最开始是用于测试“下一个任务行不行”的
            response_str = self.model_communication.communicate_with_model(state_enumeration_prompt)

        # print(response_str)

        # 然后处理成JSON再返回吧
        state_forecasting_json = self.text_transfer.get_json_from_str(response_str)
        
        return state_forecasting_json
    
    def U_func_elicitation(self,state_forecasting_json):
        # 这个是最关键的评分了，评估出效用函数。
        dellma_prompt,state_action_pair_list = self.prepare_dellma_prompt(state_forecasting_json)
        # print(dellma_prompt)

        # 好，弄好之后和大模型互动一波，看看出来的东西是什么样。
        # response_str = self.model_communication.communicate_with_model(dellma_prompt)
        response_str = text_DeLLMa_utility
        if self.config_assist["num_round"]>1:
            # 那说明是第二次跑到这里，最开始是用于测试“下一个任务行不行”的
            response_str = self.model_communication.communicate_with_model(dellma_prompt)

        print(response_str)

        # 道理上到这里应该是转成JSON，然后根据如果侦测到什么态势，就改出相应的东西来？

        U_func_json = self.text_transfer.get_json_from_str(response_str)
        return U_func_json,state_action_pair_list
    
    def maximize_Utility(self, theta_j:str, a_i:str,U_theta_a_list:list):
        # 这个是最大化效用函数的，选出一个特定的Action来最大化效用，至此就决定出哪个好了。
        a_star = 1145
        return a_star
    
    def get_next_mission(self, U_func_json,state_action_pair_list):
        # 这个就是给出下一步要执行什么样的子任务了。

        selected_str = U_func_json["decision"]

        index_selected = int(self.text_transfer.cut_from_str(selected_str,'状态-动作对',"114514",model="infinite"))

        selected_state_action_pair = state_action_pair_list[index_selected]

        next_mission_str = selected_state_action_pair["action"]

        next_mission_json = {} 
        # action_str = "类型：" + submission_type + "，参加单位：" + unit_type + "，出击方向：" + direction
        next_mission_json["类型"] = self.text_transfer.cut_from_str(next_mission_str,"类型：","，参加单位：",model="normal")
        next_mission_json["参加单位"] = self.text_transfer.cut_from_str(next_mission_str,"，参加单位：","，出击方向：",model="normal")
        next_mission_json["出击方向"] = self.text_transfer.cut_from_str(next_mission_str,"，出击方向：","1919810",model="infinite")

        return next_mission_json

    def prepare_dellma_prompt(self,state_forecasting_json) -> str | List[str]:
        context = self.text_transfer.prepare_context()  # how the context is prepared 因为是每一部分可以单独和大模型发，不依赖于大模型那里的历史记录，所以这里要补全一个context
        action_choice = self.get_action_choice()
        actions = self.text_transfer.prepare_actions(action_choice)  # how the actions are enumerated
        state_str = self.text_transfer.get_str_from_json(state_forecasting_json)

        state_candidates = self.get_state_candidates()

        state_action_pair_str, state_action_pair_list= self.text_transfer.prepare_state_action_prompt(action_choice, state_candidates)  # how the state-action pair is enumerated
        preference = self.text_transfer.prepare_preference_prompt(state_action_pair_list)  # how the preference is elicited

        DeLLMa_prmpt = context + "\n\n" + self.utility_prompt + "\n\n" + actions + "\n\n" + state_str + "\n\n 可能的状态动作对为：\n" + state_action_pair_str+ "\n" + preference

        return DeLLMa_prmpt,state_action_pair_list

    def one_round(self):
        if "num_round" in self.config_assist:
            self.config_assist["num_round"] += 1
        else:
            self.config_assist["num_round"]  = 0 

        # 别再叠床架屋了，这里直接给他冲了。这个要返回的是，下一个子任务是是什么。先别管多步的，先把一步的做了再说。

        state_forecasting_json = self.state_enumeration_and_forecasting(G="避免正面冲击敌防线")
        U_func_json,state_action_pair_list = self.U_func_elicitation(state_forecasting_json)

        # 然后是把它提提出来，决定好下一个任务是什么。
        next_mission_json = self.get_next_mission(U_func_json,state_action_pair_list)
        
        return next_mission_json