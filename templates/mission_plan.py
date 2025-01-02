# 这个是方案的模板，意思多个submission排列构成方案。
import os.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DeLLMa.DeLLMa import *

class mission_plan():
    def __init__(self):
        self.id_str = "none"
        self.target_str = "none"
        self.force_arrange = [] 
        self.submission_list = []
        self.DeLLMa = DeLLMa()

    def compatibility_check(self, submission_list):
        # 这个是检测整个任务序列是否合法，别有各种冲突。至于检测规则可以后面慢慢加。
        return True
    
    def ready_check(self):
        # 这个是检测整个任务序列是否已经具备状态，比如覆盖了所有时间所有装备，凑够了所有指标。
        return True
    
    def decide_next_submission(self):
        # 如果是之前已经决策决策到一半的，那就是需要把已有的submission_list转化成一些Prompt，用于输入进去
        planned_prompt = self.get_planned_prompt()
        self.DeLLMa.text_transfer.get_planned_str(planned_prompt)
        # 这个是决定下一个要执行的任务。
        next_mission_json = self.DeLLMa.one_round()
        

        # 设定好下一步的，然后得给出决策还没决策圆的地方
        next_submission = submission(next_mission_json=next_mission_json,submission_list=self.submission_list)
        self.submission_list.append(next_submission)

        return next_submission
    
    def get_planned_prompt(self):
        # 如果是之前已经决策决策到一半的，那就是需要把已有的submission_list转化成一些Prompt，用于输入进去
        geshu = len(self.submission_list)
        if geshu ==0:
            # 无事发生。
            planned_prompt = ""
        else:
            planned_prompt = "在之前的决策过程中，我们已经确定了"+str(geshu)+"个子任务，做出了部分的作战决策，如下所示: \n "
            for i in range(geshu):
                planned_prompt += self.DeLLMa.text_transfer.get_str_from_json2(self.submission_list[i].config_json) + "\n"
            waiting_prompt = self.get_waiting_prompt()
            planned_prompt += waiting_prompt
        return planned_prompt

    def get_waiting_prompt(self):
        # 查出还需要决策的单位和时间。确切地说应该是所有所有单位，在多少帧之前进行了决策。
        print("unfinishd yet, get_waiting_prompt")
        time_arranged = self.submission_list[-1].time_arrange[1]
        force_arranged = self.submission_list[-1].force_arrange
        
        # 这里好好地搞一下，仅计算时间最新的，时间最新的里面的单位情况。
        time_arranged_max = 0
        for submission in self.submission_list:
            time_arranged = submission.time_arrange[1] 
            if time_arranged > time_arranged_max:
                time_arranged_max = time_arranged

        # 最大时间出来之后，再来看装备情况。
        force_arranged_list = [] 
        for submission in self.submission_list:
            time_arranged = submission.time_arrange[1]
            if time_arranged == time_arranged_max:
                force_arranged_list.append(submission.force_arrange)

        # 然后是根据不同的安排情况来看，到底是还有哪些东西没有安排。
        force_prompt = "在"+str(time_arranged_max)+"帧之前，"
        for unit_type_single in unit_type:
            if unit_type_single not in force_arranged_list:
                if unit_type_single == "坦克和自行迫榴炮":
                    force_prompt += "尚未为坦克和自行迫榴炮榴炮安排作战任务，应该充分发挥其火力优势，安排其掩护我方地面力量，打击敌方防线。\n"
                elif unit_type_single == "无人机和巡飞弹":
                    force_prompt += "尚未为无人机和巡飞弹，应该充分发挥其机动和侦察优势，根据态势预测安排其前出侦察。\n"
                elif unit_type_single == "装甲车等其他地面力量":
                    force_prompt += "尚未为装甲车安排作战任务，应该发挥其电子干扰、运输步兵的优势，为其他单位提供有效支援。\n"
        waiting_prompt = "在"+str(time_arranged_max)+"帧之前的决策业已完成，你作为决策者，接下来需要在考虑敌方可能应对的同时做出决策。"
        return waiting_prompt

