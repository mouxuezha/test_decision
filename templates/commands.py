# 这个用于统一定义一下前后端之间的指令类型
import json

class command_transfer:
    # 这个是用来统一实现报文组装的。早年的时候报文的组装是直接放在Env里面的，这样可读性差一些。现在报文类型多了，就拆出来了。
    # 同时，由于完全不服务于方案生成功能，或者说完全没技术性，所以也不合text_transfer搅在一起。
    # 故放在此处。

    def __init__(self):
        self.__init_function()
        pass 

    def __init_function(self):
        # 这里定义一些指令的映射关系。或者说，给前端发的内容里面表头是什么。
        self.communication_list = [] 
        self.communication_list.append("GetCurrentStatus")
        self.communication_list.append("HumanIntent")
        self.communication_list.append("Plans") # 方案生成结果
        self.communication_list.append("Evaluate") # 方案评估结果
        # self.communication_map[""]
        # command = {"CMD": "GetCurrentStatus"}
        pass

    def arrange_communication(self, Action, communication_type:str):
        # 这个是组装报文用的。根据指令类型，组装成报文

        # 先检查一下type是不是合法的。
        if not(communication_type in self.communication_list):
            raise Exception("communication_type is not valid")
        command = {"CMD": communication_type}
        if Action != None:
            if type(Action) == dict:
                command.update(Action)
            elif type(Action) == str:
                command["Str"] = Action
            else:
                raise Exception("unfinished yet in arrange_communication: Action type is invalid")
        # command_str = json.dumps(command)
        command_str = str(command)
        return command_str