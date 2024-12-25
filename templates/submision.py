# 这个是子任务的模板，原则上子任务应该实例化一个这个东西

class submission():
    def __init__(self):
        self.id_str = "none"
        self.target_str = "none"
        self.indicator_list = []
        self.type_str = "none"
        self.time_arrange = [0, 0] 
        self.space_arrange = [0,0,0,0]
        self.spectrum = [[0,1]]
        self.force_arrange = [] 
        self.relation_list = [] 
        self.flag_well_defined = False
    
    def compatibility_check(self, submission2):
        return True
    
    def _init_type(self,type):
        # 根据不同的任务类型，给出各种配置的限制和参考，专门组一个dict好了
        type_dict = {} 
        self.type_dict = type_dict

# 这个先照着劳动竞赛的去写，看看成色。
submission_type_list = ["none","陆地进攻","陆地防御","空中侦察","空中打击","电磁干扰"]
    
    