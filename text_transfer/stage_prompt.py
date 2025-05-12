# 这个试图实现一个“根据当前的帧数判断是什么阶段”的东西，从而做一个“到一定步数就命令全员A到点里去”这样的。
# TODO: 再做一个输入态势之后计算敌我啥的，然后生成一堆文字来描述态势的功能。
import os.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from text_transfer.text_transfer import *

class StagePrompt:
    def __init__(self, flag_kaiguan=True):
        self.stage_now = "机动"
        # 先初步划分一下，“机动”阶段（前期，调一下阵型，上下车啥的，如有），“交战”阶段（不加什么特效），“夺控”阶段。
        self.flag_kaiguan = flag_kaiguan
        self.player = "red"
        pass

    def set_player(self,player_name = "red"):
        # 这次要分红蓝方了，所以需要一个设定现在是哪一方的东西。
        if (player_name == "red") or (player_name == "blue"):
            # 那就说明队名是合法的，那就可以直接设定。
            self.player = player_name
        else:
            raise Exception("invalid player name in StagePrompt")

    def get_stage_now(self, time_step):
        # 根据当前帧数判断是什么阶段，突出一个怎么快怎么来。
        if time_step < 400:
            self.stage_now = "机动"
        elif time_step <700:
            self.stage_now = "侦察"
        elif time_step < 1500:
            self.stage_now = "交战"
        elif time_step < 2999:
            self.stage_now = "推进"
        else:
            self.stage_now = "默认"
        return self.stage_now
        pass
    
    def get_stage_prompt(self,time_step,player = "red"):
        
        prompt = ""

        if player == "red":
            prompt = self.get_stage_prompt_red(time_step)
        elif player == "blue":
            prompt = self.get_stage_prompt_blue(time_step)
        
        return prompt

    def get_stage_prompt_red(self, time_step):
        # 先确定一下当前的阶段，然后根据阶段生成一些prompt
        if self.flag_kaiguan == False:
            # 关闭状态，直接返回个空的。
            return ""
        self.get_stage_now(time_step)
        prompt = "当前时间步长为" + str(time_step) + "，现在我的作战意图是"
        
        # # 这个是人混的时候加的。
        # prompt = "如无具体命令，则" + prompt
        
        if self.stage_now == "机动":
            prompt = prompt+ "请命令我方全部坦克、无人突击车、步战车和自行迫榴炮搜索前进，向经纬度(100.138, 13.6196)处集结，步兵不下车，无人机和巡飞弹前出至建筑物附近侦察。"
        elif self.stage_now == "交战":
            prompt = prompt+  "请命令我方全部坦克、无人突击车、步战车等地面力量沿地图东侧推进，到(100.175, 13.6446)附近集结，自行迫榴炮占据有利位置(100.167, 13.6472)，无人机和巡飞弹到自行迫榴炮附近巡逻。"
        elif self.stage_now == "推进":
            prompt = prompt+  "请命令除自行迫榴炮以外的地面装备向北突击，向经纬度(100.138, 13.6605)附近展开搜索攻击，两个巡飞弹分别向北向西前出。"
        elif self.stage_now == "侦察":
            prompt = prompt+  "请命令坦克停止前进，步兵下车，全部装备转为隐蔽状态，并命令无人机和巡飞弹移动到东南方向移动以探查敌情"
        elif self.stage_now == "默认":
            prompt = prompt+ "请命令所有地面部队向夺控点推进。"
        return prompt

    def get_stage_prompt_blue(self, time_step): 
        # 红蓝方分开弄了，这里是蓝方的。
        if self.flag_kaiguan == False:
            # 关闭状态，直接返回个空的。
            return ""

        if self.stage_now == "机动":
            prompt = prompt+ "请命令我方全部坦克、步战车搜索前进，向经纬度(100.137, 13.6459)处集结，步兵不下车，无人机和巡飞弹前出至建筑物附近侦察。"
        elif self.stage_now == "交战":
            prompt = prompt+  "请命令我方全部坦克、步战车等地面力量沿地图东侧推进，到(100.148, 13.6538)附近分散布置防御，无人机和巡飞弹前出到东边建筑物附近。"
        elif self.stage_now == "推进":
            prompt = prompt+  "请命令坦克和电子干扰车进行回防，到经纬度(100.13, 13.6452)附近分散部署，派遣一个巡飞弹到电子干扰车附近游走"
        elif self.stage_now == "侦察":
            prompt = prompt+  "请命令坦克停止前进，步兵下车，全部装备转为隐蔽状态，并命令无人机和巡飞弹移动到东南方向移动以探查敌情"
        elif self.stage_now == "默认":
            prompt = prompt+ "请命令所有地面部队向夺控点机动，在夺控点附近分散布防"
        return prompt        

    def get_stage_prompt_plan(self, index):
        # 这个是服务于多方案生成的，根据index提供一些差异化的提示词看看能不能给出一些不一样的方案来。
        plan_prompt = ""
        if index == 0:
            plan_prompt = "请先进行试探，避免正面冲击敌防线，然后再发起进攻。命令我方地面单位沿地图东侧推进，自行迫榴炮占据有利射击位置，无人机和巡飞弹前出至建筑物附近侦察。随着推演进行，基本摸清敌方动向之后地面部队向北突击，进攻对方防线薄弱位置，并在削弱敌方防御之后尝试占领夺控点。"
        elif index == 1:
            plan_prompt = "请尽快完成作战任务，占领夺控点。为达成此目的，可接受一定程度的损失，所以可直接从正面展开进攻。无人机和巡飞弹适当深入敌方设防区域，尽早确定敌方动向。"
        elif index == 2:
            plan_prompt = "请以保存自身实力为主，广泛进行侦察，沿着敌方防线寻找敌方防线的薄弱点进行试探，若无十足把握则不要轻易进攻。命令我方地面单位沿地图西面前出，自行迫榴炮占据有利射击位置，无人机和巡飞弹侦察监控地面部队周围区域，并为炮火提供引导。"
        
        print("get_stage_prompt_plan: unfinished yet.")
        return plan_prompt
    
    def get_jiaocheng_prompt(self,index):
        # 这个是教程的prompt，用来引导用户进行一些操作。
        # 原则上会按顺序输出出去，这个尽量只用于给指挥员人类看。
        
        jiaocheng_prompt_list = [] 
        jiaocheng_prompt_list.append('教程：大模型方案生成工具可根据人类指挥员意图和预置的先验知识，生成特定场景下的作战方案，并驱动推演。以下进行示例。【输入任意字符继续】')
        jiaocheng_prompt_list.append('教程：已加载陆火联合城镇攻防场景。我方为红方，拥有坦克、步兵战车、步兵、自行迫榴炮、无人突击车、巡飞弹、无人机、导弹发射车、电子干扰车等装备，步兵下车后作战。我方自行迫榴炮具备较大的射程和载弹量，但只能在停下后攻击，坦克、无人突击车、无人机等则可以在移动中展开攻击。我方需要攻取位于经纬度坐标[100.1247, 13.6615]的夺控点，将陆战装备移动到夺控点处并消灭夺控点附近敌人可占领夺控点，导弹发射车不能机动，固定部署在远处以提供火力支援。推演以帧为单位推进，每一帧对应推演中的1秒，共进行5000帧，推演中装备的移动速度均与现实中类似，可据此估计双方位置。【输入任意字符继续】')
        jiaocheng_prompt_list.append("教程：敌方为蓝方，初始部署位置为[100.1247, 13.6615]，拥有坦克、步兵战车、步兵、无人突击车、巡飞弹、无人机、防空导弹发射车等装备，在东、中、西建筑物内有驻守有蓝方步兵，防空导弹发射车固定部署在夺控点周围一定范围内，在未受打击时能够完全拦截我方导弹。推演开始后，蓝方地面单位将进行机动，靠近建筑物和交通线布防，并派遣巡飞弹、无人机等前出侦察。根据我方行动，敌方有可能沿交通线调动兵力，阻击我方单位前进。以推演结束时对夺控点的占领情况和战损比情况来确定胜负，我方地面单位机动到夺控点并保持40帧即可占领夺控点，战损比以双方分数计算，导弹发射车50分，坦克20分，装甲车辆和无人机15分，步兵和巡飞弹5分。因此，我方应该充分侦察，发挥地面火力优势，优先消灭对方防空导弹发射车后有效利用我方导弹打击敌地面目标。【输入任意字符继续】")   
        jiaocheng_prompt_list.append("教程：例如，输入以下作战意图，开始方案生成：“"+self.get_stage_prompt_plan(0) + "”。【输入字符以继续】")
        jiaocheng_prompt_list.append(self.get_stage_prompt_plan(0))
        prompt_output = jiaocheng_prompt_list[index]
        return prompt_output
    
    def get_one_plan_prompt(self,index):
        # 这个的说法是，把指挥员的输入分成多次，尽量多来一些信息并且显得稍微智能一些。
        one_plan_prompt_list = [] 
        one_plan_prompt_list.append("提示：可指定作战风格和决心，例如“请先进行试探，避免正面冲击敌防线，然后再发起进攻。”  【请键入指挥员意图】")
        one_plan_prompt_list.append("提示：可通过指定全局进攻方向，避开敌防御正面，例如“命令我方地面单位沿地图东侧推进，”  【请键入指挥员意图】")
        one_plan_prompt_list.append("提示：可通过指定特定编组进行控制，例如“自行迫榴炮占据有利射击位置，无人机和巡飞弹前出至建筑物附近侦察。”  【继续键入指挥员意图】")
        one_plan_prompt_list.append("提示：可增加分阶段的指令，例如“随着推演进行，基本摸清敌方动向之后地面部队向北突击，进攻对方防线薄弱位置，并在削弱敌方防御之后尝试占领夺控点。”  【继续键入指挥员意图】")
        one_plan_prompt_list.append("提示：输入完成，开始方案生成......")
        prompt_output = one_plan_prompt_list[index]
        return prompt_output