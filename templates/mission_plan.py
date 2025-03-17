# 这个是方案的模板，意思多个submission排列构成方案。
import os.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DeLLMa.DeLLMa import *

from templates.submision import *

class mission_plan():
    def __init__(self):
        self.id_str = "none"
        self.target_str = "none"
        self.force_arrange = [] 
        self.submission_list = []
        self.DeLLMa = DeLLMa()
    
    def set_users_goal(self, G:str):
        # 这个是用来对某个任务设定目标的。明确:论文里的users goal G和这里代码里的target str，道理上就是一回事儿。
        self.target_str = G
        print("mission_plan: set users goal to: \n", G)
    
    def set_config_mission_plan(self,**kargs):
        self.DeLLMa.set_config_assist(**kargs)

    def compatibility_check(self, submission_list):
        # 这个是检测整个任务序列是否合法，别有各种冲突。至于检测规则可以后面慢慢加。
        return True
    
    def ready_check(self):
        # 这个是检测整个任务序列是否已经具备状态，比如覆盖了所有时间所有装备，凑够了所有指标。
        return True
    
    def decide_next_submission(self):
        # 如果是之前已经决策决策到一半的，那就是需要把已有的submission_list转化成一些Prompt，用于输入进去
        planned_prompt, planned_unit_type = self.get_planned_prompt()
        self.DeLLMa.text_transfer.get_planned_str(planned_prompt)
        self.DeLLMa.get_planned_unit_type(planned_unit_type)

        # 这个是决定下一个要执行的任务。
        next_mission_json = self.DeLLMa.one_round(user_goal=self.target_str)

        # 设定好下一步的，然后得给出决策还没决策圆的地方
        next_submission = submission(next_mission_json=next_mission_json,submission_list=self.submission_list)
        # 做一个容错，如果和前面一个完全一样，那就不append了。
        if len(self.submission_list)>0:
            if next_submission.check_equal(self.submission_list[-1]):
                # 估计得重新写一个判断等于函数
                print("mission_plan: 发现下一个决策和上一个决策完全一样，不进行append操作。")
                # raise Exception("任务生成的有问题，这个就不应该放进去。")
            else:
                self.submission_list.append(next_submission)
        else:
            self.submission_list.append(next_submission)
        self.DeLLMa.output_docx.set_submission(self.submission_list)
        self.DeLLMa.output_docx.save_file()

        print("mission_plan: finish one decision, next submission was determined, En Taro XXH.")

        return next_submission
    
    def decide_void_submission(self):
        # 搞一个空的子任务用于发回去，用于表示当前是空的
        next_submission = submission()
        next_submission.id_str = "未定义子任务"
        next_submission.target_str = "无"
        next_submission.type_str = "无"
        next_submission.force_arrange = "无"

        self.submission_list.append(next_submission)
        return next_submission
    
    def decide_default_submission(self,force_arrange,num,submission_list,**kargs):
        # 这个是为了配合那边接口那里而搞出来的，默认子任务得琢磨一下还。不同的兵种得要不一样的。
        # 不要缝合太多的功能，这个就是单纯的生成默认说法。
        print("mission_plan: decide_default_submission unfinished yet")
        next_mission_json = {}
        

        if force_arrange == "坦克和自行迫榴炮":
            # 那默认任务就是向北进攻。
            next_mission_json["任务类型"] = "陆地进攻"
            pass
        elif force_arrange ==  "装甲车等其他地面力量":
            # 那默认任务本来应该是过去汇合，姑且也先用向北进攻好了。
            next_mission_json["任务类型"] = "陆地进攻"
            pass
        elif force_arrange == "无人机和巡飞弹":
            # 那默认任务就是去侦查。
            next_mission_json["任务类型"] = "空中侦察"
            pass 

        next_mission_json["参加单位"] = force_arrange
        next_mission_json["出击方向"] = "中间"

        defualt_submission = submission(next_mission_json=next_mission_json,submission_list=submission_list)
        return defualt_submission


    def describe_last_submission(self,index = -1 ):
        # 返回一段描述下一个子任务的话，用于发过去显示在前端。
        
        # 先取出一个子任务出来看看成色
        submission_single = self.submission_list[index]

        # 然后生成一段对话。
        str_single = "在第" + str(submission_single.time_arrange[0]) + "帧到第" +str(submission_single.time_arrange[1]) + "帧期间，方案智能生成分系统为" + submission_single.force_arrange + "分配了任务，命令其" + submission_single.type_str+"，具体出击方向为" + submission_single.config_json["出击方向"] +"，解算得到预定任务范围"+ str(submission_single.space_arrange)+"。"

        return str_single

    
    def get_planned_prompt(self):
        # 如果是之前已经决策决策到一半的，那就是需要把已有的submission_list转化成一些Prompt，用于输入进去
        geshu = len(self.submission_list)
        if geshu ==0:
            # 无事发生。
            planned_prompt = ""
            planned_unit_type = unit_type
        else:
            planned_prompt = "在之前的决策过程中，我们已经确定了"+str(geshu)+"个子任务，做出了部分的作战决策，如下所示: \n "
            for i in range(geshu):
                planned_prompt += self.DeLLMa.text_transfer.get_str_from_json2(self.submission_list[i].config_json) + "\n"
            waiting_prompt, planned_unit_type = self.get_waiting_prompt()
            planned_prompt += waiting_prompt
            planned_prompt += "注意,需要尽量给我方所有单位都分配上合适的任务,不要留下闲置的单位。"
        
        # 然后来一段根据时间的情况来推测敌方动向的Prompt，以及我方战术提示的。这部分对标的其实是条令条例。
        time =self.check_time()
        planned_prompt += "根据当前时间"+str(time)+"帧，推测敌方动向如下: \n"
        if time < 1002:
            planned_prompt += "敌方从起始点出发，尚在向可能的预定阵地进行机动，我方需做出侦察，以根据情况选择合适作战方向。"
        elif time < 3002:
            planned_prompt += "敌方已经到达预定阵地，正在等待我方进攻，我方需做好进攻准备，进行火力试探。"
        else:
            planned_prompt += "敌方可能已经发现我方行动意图，并相应调整了布署，此时我方应该集结兵力，互相配合，尝试取得突破。"

            
        return planned_prompt, planned_unit_type

    def get_waiting_prompt(self):
        # 查出还需要决策的单位和时间。确切地说应该是所有所有单位，在多少帧之前进行了决策。
        # print("unfinishd yet, get_waiting_prompt")
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
        
        if len(unit_type) <= len(force_arranged_list):
            # 那就是都安排全了，可以安排下一个时间节点的了。
            force_prompt += "所有单位都已经安排完毕，可以安排下一个时间节点的作战任务了。"
            planned_unit_type = unit_type
        else:
            planned_unit_type = []
            for unit_type_single in unit_type:
                if unit_type_single not in force_arranged_list:
                    if unit_type_single == "坦克和自行迫榴炮":
                        force_prompt += "尚未为坦克和自行迫榴炮榴炮安排作战任务，应该充分发挥其火力优势，安排其掩护我方地面力量，打击敌方防线。\n"
                        planned_unit_type.append(unit_type_single)
                    elif unit_type_single == "无人机和巡飞弹":
                        force_prompt += "尚未为无人机和巡飞弹安排作战任务，应该充分发挥其机动和侦察优势，根据态势预测安排其前出侦察。\n"
                        planned_unit_type.append(unit_type_single)
                    elif unit_type_single == "装甲车等其他地面力量":
                        force_prompt += "尚未为装甲车等其他地面力量安排作战任务，应该发挥其电子干扰、运输步兵的优势，为其他单位提供有效支援。\n"
                        planned_unit_type.append(unit_type_single) # 复制代码很是丑陋，但是不管了，无所谓了呵呵。
        waiting_prompt = force_prompt + "你作为决策者，接下来需要在考虑敌方可能应对的同时做出决策。"
        
        if len(planned_unit_type) == 0:
            planned_unit_type = unit_type
            print("按说不应该运行到这里，看看哪儿出问题了。")
        return waiting_prompt, planned_unit_type

    def check_time(self):
        # 从submission_list里面找到时间最大的那个，然后返回这个时间。
        # 原来的简单逻辑有问题，因为正常情况下会有好几个子任务是最后同一个时间结束。
        # 干脆再来一轮check同样的个数好了，反正总共也没几个子任务，计算开销不大
        time_arranged_max = 0
        time_arranged_max2 = 0 
        for submission in self.submission_list:
            time_arranged = submission.time_arrange[1]
            if time_arranged > time_arranged_max:
                time_arranged_max = time_arranged
                time_arranged_max2 = submission.time_arrange[0]
        
        # 然后来一个检测有几个子任务是这个时间段的。
        # num_repeat = 3 # 这个设定为一个可调的阈值好了，其实是取决于有几个兵种。
        num_repeat = len(unit_type)
        num_repeat_here = 0 
        for submission in self.submission_list:
            if submission.time_arrange[1] == time_arranged_max:
                # 那就计数加一
                num_repeat_here += 1
        if num_repeat_here >= num_repeat:
            # 那就说明都安排好了，可以安排下一个时间节点了。
            pass
        else:
            # 那就说明这个时间点还没安排好，需要继续安排。
            time_arranged_max = time_arranged_max2

        return time_arranged_max