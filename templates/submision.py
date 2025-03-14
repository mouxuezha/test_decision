# 这个是子任务的模板，原则上子任务应该实例化一个这个东西
import os.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import random

class submission():
    def __init__(self,**kargs):
        self.id_str = "none"
        self.target_str = "none"
        self.indicator_list = []
        self.type_str = "none"
        self.time_arrange = [0, 0] 
        self.space_arrange = [0,0,0,0] # 左上、右下
        self.spectrum = [[0,1]]
        self.force_arrange = [] 
        self.relation_list = [] 
        self.flag_well_defined = False
        self.config_json = {} 

        if "next_mission_json" in kargs and "submission_list" in kargs:
            self.set_submission(kargs["next_mission_json"],kargs["submission_list"])
    
    def compatibility_check(self, submission2):
        return True
    
    def _init_type(self,type):
        # 根据不同的任务类型，给出各种配置的限制和参考，专门组一个dict好了
        # 后期的话这个应该是要调用知识图谱的。
        type_dict = {} 
        self.type_dict = type_dict
    
    def set_submission(self,next_mission_json,submission_list):
        
        self.config_json = next_mission_json
        
        if "类型" in next_mission_json:
            self.type_str = next_mission_json["类型"]
            self._init_type(self.type_str)
        # if "id" in next_mission_json:
        #     self.id_str = next_mission_json["id"]
        index = len(submission_list)
        self.id_str = self.type_str + str(index)

        if "参加单位" in next_mission_json:
            force_arrange_str = next_mission_json["参加单位"]
            # TODO: 搞个真正的函数来实现force arrang，这样才能和后面的连起来。
            self.force_arrange = self.arrange_force(force_arrange_str)      

        # 先分配单位再来算时间，因为算时间是看着单位算。  
        self.arrange_time(submission_list)

        if "出击方向" in next_mission_json:
            direction = next_mission_json["出击方向"]
            # 算方向得根据时间来算，所以要先分配了时间再来
            self.set_direction(direction,self.type_str)
        
        self.flag_well_defined = self.check_well_define()
    
    def set_direction(self,direction,submission_type):
        # 大模型给出的方向是高度抽象化的，需要转换成具体的坐标。根据任务时间解算坐标可也。


        if submission_type == "陆地进攻" or submission_type == "空中侦察":
            if direction == "偏东":
                theta_rad =  (30+random.randint(0,10)) / 180 * np.pi
                self.space_arrange = [100.164-0.001,13.658-0.007,100.164-0.003,13.658-0.005]
                pos_start = np.array([100.164, 13.658])
            elif direction == "偏西":
                theta_rad = -(30+random.randint(0,10)) / 180 * np.pi
                self.space_arrange = [100.116+0.001,13.643+0.007,100.116+0.003,13.643+0.005]
                pos_start = np.array([100.116, 13.643])
            elif direction == "中间": 
                theta_rad = 0 
                self.space_arrange = [100.137+0.001,13.644+0.007,100.137+0.003,13.644+0.005]
                pos_start = np.array([100.137, 13.644])
            else:
                raise Exception("invalid direction")
        
        # pos_start = np.array([100.15427471282, 13.60603147549])
        pos_end = np.array([100.1247, 13.6615])
        vector_go = pos_end - pos_start
        vector_go_L = np.linalg.norm(vector_go)
        vector_go_n = vector_go / vector_go_L
        bili = (self.time_arrange[0] + self.time_arrange[1])/2 / (5000 + random.randint(0, 1145))   # 做个平均值         
        M_rotate = np.array([[np.cos(theta_rad), -np.sin(theta_rad)], [np.sin(theta_rad), np.cos(theta_rad)]])
        
        L_here = bili*vector_go_L

        dVctor_here = L_here * vector_go_n # 修正向量旋转前
        dVctor_here = M_rotate @ dVctor_here # 修正向量旋转后

        self.space_arrange = [float(pos_start[0]-dVctor_here[0]), float(pos_start[1]+dVctor_here[1]), float(pos_start[0]+dVctor_here[0]), float(pos_start[1]-dVctor_here[1])]

        pass
        
    def arrange_force(self, force_arrange_str):
        # TODO: 搞个真正的函数来实现force arrang，这样才能和后面的连起来。
        # 2025年1月2日20:07:56，现在这样倒是也能和后面连起来，没啥不行的也。
        # print("unfinished yet, submission.arrange_force")
        return force_arrange_str
    
    def arrange_time(self,submission_list):
        # TODO: 整一个阳间的时间分配，要考虑为不同的单位都维护一个“当前任务都分配到啥时候了”，因为很可能不同单位的任务是异步的。
        geshu = len(submission_list) 

        # self.time_arrange=[geshu*1000, (geshu+1)*1000]

        # 好好搞搞。逻辑应该是，找到前面为当前装备的安排的最后一个任务的时间点是多少，然后再往后加一些。
        for submission in submission_list:
            if submission.force_arrange == self.force_arrange:
                if self.time_arrange[0]< submission.time_arrange[1]:
                    self.time_arrange[0] = submission.time_arrange[1]
        self.time_arrange[1] = self.time_arrange[0] + 1000 
        # 这里加多少就是一个任务分配多长的帧数。
        # print("unfinished yet, submission.arrange_time")
    
    def check_well_define(self):
        print("unfinished yet, submission.check_well_define")
        return True
    
    def check_equal(self, next_submission):
        # check一下两个submission是不是一样。
        flag = True
        flag = flag and (self.type_str == next_submission.type_str)
        flag = flag and (self.force_arrange == next_submission.force_arrange)
        flag = flag and (self.time_arrange == next_submission.time_arrange)
        
        # 这几个相等就认为是相等了。
        return flag

# 这个先照着劳动竞赛的去写，看看成色。后期的话这个应该是要调用知识图谱的。
# submission_type_list = ["none","陆地进攻","陆地防御","空中侦察","空中打击","电磁干扰"]
submission_type_list = ["none", "陆地进攻", "空中侦察"] # 来个简化版的不然太多了

# unit_type = ["坦克和自行迫榴炮", "无人机和巡飞弹", "所有地面装备"]
unit_type = ["坦克和自行迫榴炮", "装甲车等其他地面力量", "无人机和巡飞弹"]

# 出击方向
direction_list = ["偏东", "中间", "偏西"]    