# 这个试图实现一个“根据当前的帧数判断是什么阶段”的东西，从而做一个“到一定步数就命令全员A到点里去”这样的。
# TODO: 再做一个输入态势之后计算敌我啥的，然后生成一堆文字来描述态势的功能。


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
            plan_prompt = "请尽快完成作战任务，占领夺控点。为达成此目的，可接受一定程度的损失，直接从正面展开进攻。无人机和巡飞弹适当深入敌方设防区域，尽早确定敌方动向。"
        elif index == 2:
            plan_prompt = "请以保存自身实力为主，广泛进行侦察，沿着敌方防线寻找敌方防线的薄弱点进行试探，若无十足把握则不要轻易进攻。命令我方地面单位沿地图西面前出，自行迫榴炮占据有利射击位置，无人机和巡飞弹侦察监控地面部队周围区域，并为炮火提供引导。"
        
        print("get_stage_prompt_plan: unfinished yet.")
        return plan_prompt