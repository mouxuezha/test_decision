# 该删除的删除，防止变成屎山。这个在新的环境下要配合着DeLLMa使用了。
# 需要约定一下命令格式了。
import math
import json
from typing import Optional, Dict, List, Tuple, Callable

class text_transfer(object):
    def __init__(self) -> None:
        self.command_type_list = ["move", "stop", "off_board"]
        self.type_transfer = type_transfer()
        self.num_commands = [0,0] # 第一个是转化成功的commands，第二个是转化失败的commands 
        self.ed_lat,  self.ed_lon =  39.70, 2.68984
        self.tar_lat, self.tar_lon = 39.7600, 2.7100

        self.__init_type()

        self.__init_DeLLMa()

    
    def __init_type(self):
        # 这个就是把那些ID的类型弄过来整成一个列表以备后用。
        # 红方坦克：MainBattleTank_ZTZ100，蓝方坦克：MainBattleTank_ZTZ200，红方步兵战车：WheeledCmobatTruck_ZB100，蓝方步兵战车：WheeledCmobatTruck_ZB200，步兵班：Infantry，自行迫榴炮：Howitzer_C100，无人突击车：ArmoredTruck_ZTL100，无人机：ShipboardCombat_plane，导弹发射车：missile_truck。
        self.type_list = ["MainBattleTank_ZTZ100","MainBattleTank_ZTZ200","WheeledCmobatTruck_ZB100","WheeledCmobatTruck_ZB200","Infantry","Howitzer_C100","ArmoredTruck_ZTL100","ShipboardCombat_plane","missile_truck","JammingTruck","RedCruiseMissile","BlueCruiseMissile"]
        self.type_list_CN = ["坦克","坦克","步兵战车","步兵战车","步兵班","自行迫榴炮","无人突击车","无人机","导弹发射车","电子干扰车","巡飞弹","巡飞弹"]
        self.command_type_list = ["move","stop","offboard"] # 
    
    def __init_DeLLMa(self):
        self.state_enmueration_dict = {"敌方经度":["偏西","靠中间","偏东"],
                                  "敌方纬度":["偏北","靠中间","偏南"],
                                  "敌方聚集程度":["分散","一般","集中"],
                                  "我方经度":["偏西","靠中间","偏东"],
                                  "我方纬度":["偏北","靠中间","偏南"],
                                  "我方聚集程度":["分散","一般","集中"]}
        self.state_discription_dict = {"敌方经度":"敌方所有装备所处位置经度的平均值",
                                  "敌方纬度":"敌方所有装备所处位置经度的平均值",
                                  "敌方聚集程度":"敌方各装备相互之间的距离大小、分散程度",
                                  "我方经度":"我方所有装备所处位置经度的平均值",
                                  "我方纬度":"我方所有装备所处位置经度的平均值",
                                  "我方聚集程度":"我方各装备相互之间的距离大小、分散程度"}

    def LLA2XYZ(self, lon, lat, alt):
        Earthe = 0.0818191908426
        Radius_Earth = 6378140.0
        PI = 3.14159265358979
        deg2rad = PI / 180.0
        lat = lat * deg2rad
        lon = lon * deg2rad
        omge = 0.99330562000987
        d = Earthe * math.sin(lat)
        n = Radius_Earth / math.sqrt(1 - math.pow(d, 2))
        nph = n + alt
        x = nph * math.cos(lat) * math.cos(lon)
        y = nph * math.cos(lat) * math.sin(lon)
        z = (omge * n + alt) * math.sin(lat)
        return x, y, z

    def XYZ2LLA(self, x, y, z):
        Radius_Earth = 6378140
        Oblate_Earth = 1.0 / 298.257
        a = Radius_Earth
        b = a * (1 - Oblate_Earth)
        e = math.sqrt(1 - math.pow(b / a, 2))
        x2 = x * x
        y2 = y * y
        root = math.sqrt(x2 + y2)
        e2 = e * e
        error = 1.0
        d = 0.0
        B = 0.0
        H = 0.0
        eps = 1e-10
        PI = 3.14159265358979
        deg2rad = PI / 180.0
        rad2deg = 180.0 / PI

        while error >= eps:
            temp = d
            B = math.atan(z / root / (1 - d))
            sin2B = math.sin(B) * math.sin(B)
            N = a / math.sqrt(1 - e2 * sin2B)
            H = root / math.cos(B) - N
            d = N * e2 / (N + H)
            error = abs(d - temp)
        lat = B
        alt = H
        temp = math.atan(y / x)
        if x >= 0:
            lon = temp
        elif ((x < 0) and (y >= 0)):
            lon = PI + temp
        else:
            lon = temp - PI
        lat = lat * rad2deg
        lon = lon * rad2deg
        alt = alt
        return lon, lat, alt

    def distance(self, lon1, lat1, alt1, lon2, lat2, alt2):
        x1, y1, z1 = self.LLA2XYZ(lon1, lat1, alt1)
        x2, y2, z2 = self.LLA2XYZ(lon2, lat2, alt2)
        x2tox1 = x2 - x1
        y2toy1 = y2 - y1
        z2toz1 = z2 - z1
        distance = math.sqrt(x2tox1 * x2tox1 + y2toy1 * y2toy1 + z2toz1 * z2toz1)
        return distance

    def status_to_text(self, status):
        # print("status_to_text unfinished yet,return a demo")
        status_str = ""
        for obj_id in list(status.keys()):
            unit_status = status[obj_id]
            lon = round(unit_status["VehicleState"]["lon"], 5) 
            lat = round(unit_status["VehicleState"]["lat"], 5)
            alt = round(unit_status["VehicleState"]["alt"], 5)
            unit_type_zhongwen = self.type_transfer.unit_type_transfer(unit_status["UnitType"])
            
            # 当前装备是红方还是蓝方得读相应的字段来体现了。
            if unit_status["PlayerName"] == "redPlayer":
                side_name = "红方"
                pass
            elif unit_status["PlayerName"] == "bluePlayer":
                side_name = "蓝方"
                pass
            else:
                side_name = "其他"

            if unit_type_zhongwen == "其他":
                # 什么BMC3那些就别拿进来了
                continue
            else:
                status_str += side_name + "obj_id为"+str(obj_id)+"的"
                status_str += f"{unit_type_zhongwen}位置在({lon},{lat})处 \n"
        return status_str
    
    def status_to_text2(self,status_json):
        # 这个是来一个简化版的，只说有几个什么东西了。
        # 这个把读出来的JSON文件转换成一段叙述。
        unit_all = status_json
        unit_all_list = list(unit_all.keys())
        result_text_red = "红方："
        result_text_blue = "蓝方："
        for unit_type in self.type_list:
            count_red = 0 
            count_blue = 0 
            record_LLA_red = [] 
            record_LLA_blue = [] 
            record_ID_red = [] 
            record_ID_blue = []             
            for unit_id_single in unit_all_list:
                if unit_type in unit_id_single:
                    
                    lon = unit_all[unit_id_single]["VehicleState"]["lon"]
                    lat = unit_all[unit_id_single]["VehicleState"]["lat"]
                    
                    if unit_all[unit_id_single]["PlayerName"] == "redPlayer":
                        count_red += 1
                        record_LLA_red.append([lon,lat])
                        record_ID_red.append(unit_id_single)
                    else:
                        count_blue += 1
                        record_LLA_blue.append([lon,lat])
                        record_ID_blue.append(unit_id_single)
            # 1112增加的说法：得把坐标也想个办法弄进来

            #然后生成一段话
            if count_red != 0:
                result_text_red += self.type_list_CN[self.type_list.index(unit_type)] + "有" + str(count_red) + "个，obj_id为" + str(record_ID_red)
            if count_blue != 0:
                result_text_blue += self.type_list_CN[self.type_list.index(unit_type)] + "有" + str(count_blue) + "个，obj_id为" + str(record_ID_blue)
            result_text = result_text_red + result_text_blue
        return result_text        

    def detected_to_text(self, detected_state):
        # 这里面的探测到的数据结构还不太一样，所以需要另外开一个函数来实现
        detected_str = ""
        for obj_id in list(detected_state.keys()):
            detected_status = detected_state[obj_id]
            lon = round(detected_status["targetLon"], 5)
            lat = round(detected_status["targetLat"], 5)
            alt = round(detected_status["targetAlt"], 5)
            detected_type_zhongwen = self.type_transfer.unit_type_transfer(detected_status["unitType"])
            if detected_type_zhongwen == "其他":
                continue
            else:
                detected_str +="目标obj_id为"+str(obj_id)+"的"
                detected_str += f"{detected_type_zhongwen}位置在({lon},{lat})处 \n"
        print("text_transfer detected_to_text:" + detected_str)
        return detected_str
        pass 

    def select_by_type(self, status, type = "坦克"):
        return [ obj_id for obj_id , values_ in status.items() if type in values_["type"]]
    
    def find_nearest_enemy(self, our_lat, our_lon, detect_status, range = 2500):
        detect_id_list = [_id for _id in detect_status.keys() if self.distance( our_lat, our_lon, 0, detect_status[_id]["lat"], detect_status[_id]["lon"] ,0 ) < range]
        return self.generate_calculate_unit(detect_id_list, detect_status)
    
    def get_avg_pos(self, idlist, status):
        if len(idlist) == 0:
            return 0, 0
        avg_lat =  sum([status[obj_id]["lat"] for obj_id in idlist])/ len(idlist)
        avg_lon =  sum([status[obj_id]["lon"] for obj_id in idlist])/ len(idlist)
        return avg_lat, avg_lon
    
    def generate_calculate_unit(self, idlist, estatus):
        cal = dict()
        for  _id  in  idlist:
            _val = estatus[_id]
            if _val["type"] not in cal:
                cal[ _val["type"] ] = 1
            else:
                cal[ _val["type"] ] += 1
        
        return cal

    def relative_pos(self, olat, olon, elat, elon):   # 需要优雅一点的写法 
        rdir =  ""
        if  olon > elon :
            rdir +=  "西"
        elif olon < elon:
            rdir +=  "东"
        if olat > elat:
            rdir += "南"
        elif olat < elat:
            rdir += "北"
        return rdir 

    def text_to_commands(self, text:str):
        
        commands = []
        for command_type in self.command_type_list:
            if command_type == "move":
                index_list = self.find_all_str(text, command_type)
                for i in range(len(index_list)):
                    sub_str = text[index_list[i]:-1]
                    try:
                        try:
                            # 再来一层容错，不然遇到能力不够的就傻逼了。
                            x = float(self.cut_from_str(sub_str, "x=", ","))
                        except:
                            x = 100.138
                            print("坐标识别失败，来个容错")
                        try:
                            y = float(self.cut_from_str(sub_str, "y=", "]"))
                        except:
                            y = 13.644
                            print("坐标识别失败，来个容错")
                        obj_id = self.cut_from_str(sub_str, "obj_id=", ",")
                        command_single = {"type": command_type, "obj_id": obj_id, "x": x, "y": y}
                        commands.append(command_single)
                        self.num_commands[0] += 1
                    except:
                        self.num_commands[1] += 1
                        print("G in one move command")
            elif command_type == "stop":
                index_list = self.find_all_str(text, command_type)
                for i in range(len(index_list)):
                    sub_str = text[index_list[i]:-1]
                    try:
                        obj_id = self.cut_from_str(sub_str, "obj_id=", "]")
                        command_single = {"type": command_type, "obj_id": obj_id}
                        commands.append(command_single)
                        self.num_commands[0] += 1 
                    except:
                        self.num_commands[1] += 1
                        print("G in one stop command")
            # elif command_type == "off_board":
            #     index_list = self.find_all_str(text, command_type)
            #     for i in range(len(index_list)):
            #         sub_str = text[index_list[i]:-1]
            #         try:
            #             obj_id = self.cut_from_str(sub_str, "obj_id=", "]")
            #             command_single = {"type": command_type, "obj_id": obj_id}
            #             commands.append(command_single)
            #         except:
            #             print("G in one off_board command")   
        
        # 偷个懒，如果有下车，就让下车的覆盖别的指令好了。另开一个循环，即可。
        # 丑陋但是有用。
        for command_type in self.command_type_list:    
            if command_type == "off_board":
                index_list = self.find_all_str(text, command_type)
                for i in range(len(index_list)):
                    sub_str = text[index_list[i]:-1]
                    try:
                        obj_id = self.cut_from_str(sub_str, "obj_id=", "]")
                        command_single = {"type": command_type, "obj_id": obj_id}
                        commands.append(command_single)
                        self.num_commands[0] += 1
                    except:
                        self.num_commands[1] += 1
                        print("G in one off_board command")      

        print("text_to_commands: valid commands number: "+str(len(commands)))      
        return commands
    
    def get_initial_prompt(self):
        print("get_initial_prompt unfinished yet,return a demo")
        initial_prompt = '请作为兵棋推演游戏的玩家，设想一个陆战攻防场景。'
        '我方为红方，拥有坦克、步兵战车、步兵、自行迫榴炮、无人突击车、巡飞弹、无人机、导弹发射车、电子干扰车等装备，步兵下车后作战，'
        '我方需要攻取位于经纬度坐标(100.1247, 13.6615)的夺控点，将陆战装备移动到夺控点处并消灭夺控点附近敌人可占领夺控点，地图范围为经度100.0923到100.18707，纬度范围为13.6024到13.6724，导弹发射车不能机动。'
        '每隔一定步数，我将告诉你敌我态势和其他信息，并由你来尝试生成作战指令。\n'
        # 还需要一些描述地图的prompt
        initial_prompt = initial_prompt + "地图大部分为陆地，具有河流、桥梁和路网，在经纬度坐标(100.137,13.644),(100.116,13.643),(100.164,13.658)有可供步兵占领和建立防线的建筑物。"
        return initial_prompt

    def get_order_guize(self):
        # 这里面是给大模型设定的规则的格式。
        order_guize = '请按照以下格式给出作战指令。进攻指令：[move, obj_id , x=int, y=int], 如坦克mbt_1进攻坐标(100.1247, 13.6615)，则指令为[move, obj_id=mbt_1, x=100.1247, y=13.6615] \n停止指令：[stop, obj_id], 如坦克mbt_1停止当前行动，则指令为[stop, obj_id=mbt_1] \n步兵下车指令: [off_board, obj_id],如步战车ifv_1内步兵立刻下车,则指令为[off_board, obj_id=ifv_1]'
        return order_guize

    def find_all_str(self, text:str, sub_str:str):
        index_list = [] 
        index = text.find(sub_str)
        while index != -1:
            index_list.append(index)
            index = text.find(sub_str, index + 1)
        
        return index_list
    
    def cut_from_str(self, text:str, str_qian:str, str_hou:str,model ="normal"):
        # 需要把数字从字符串中抠出来
        # 先找到数字的起始位置
        index_qian = text.find(str_qian)
        sub_str = text[index_qian+len(str_qian):]
        if model == "normal":
            index_hou = sub_str.find(str_hou)
        elif model == "json":
            index_hou = sub_str.rfind(str_hou)
        elif model == "infinite":
            # 这个是没有后str，直接一波切到最后
            index_hou = len(sub_str)
        # index_hou = text.find(str_hou)
        number_str = sub_str[0:index_hou]
        # number_float = float(number_str)
        return number_str
    
    def get_json_from_str(self, input_str:str):
        # 切出来，然后转成JSON，转不成就报错。反正是实验代码，要什么稳定性，该报错报错就是了。
        json_str = self.cut_from_str(input_str, "{", "}",model="json")
        json_str = "{" + json_str + "}"
        json_jieguo = json.loads(json_str)
        return json_jieguo
    
    def get_str_from_json(self, json_jieguo:dict):
        # 把json转成字符串
        # 直接转效果不好，还是阳间一点比较好
        # json_str = json.dumps(json_jieguo)
        json_str = ""
        for key in json_jieguo:
            json_str += key+":"
            for key2 in json_jieguo[key]:
                json_str += "“"+key2 + "”：“"+json_jieguo[key][key2] + "”,"
            json_str += "\n"
        return json_str
    
    def get_str_from_json2(self,json_jieguo:dict):
        # 这个是一层的，丑嘛丑一点
        json_str = ""
        for key in json_jieguo:
            json_str += key + ":"
            json_str += json_jieguo[key]
            json_str += "，"
        json_str = json_str[:-1]
        json_str += "。"
        return json_str


    def get_num_commands(self):
        # 这个算是结果处理，用来看有多少
        str_buffer = "成功识别指令{}个，识别失败{}个。".format(self.num_commands[0], self.num_commands[1])
        str_buffer = str_buffer + "\n识别成功率：" + str(self.num_commands[0]/(self.num_commands[0]+self.num_commands[1]+0.0000001))
        
        print(str_buffer)
        return str_buffer
    
    # 这几个prepare开头的是服务于DeLLMa的。
    def prepare_context(self,status=[]):
        # how the context is prepared
        # 这个好说，就是场景和态势嘛，可以从text_JSQL里面抄。
        jieguo = '请作为兵棋推演游戏的玩家，设想一个陆战攻防场景。' + \
            '我方为红方，拥有坦克、步兵战车、步兵、自行迫榴炮、无人突击车、巡飞弹、无人机、导弹发射车、电子干扰车等装备，步兵下车后作战。我方自行迫榴炮具备较大的射程和载弹量，但只能在停下后攻击，坦克、无人突击车、无人机等则可以在移动中展开攻击' + \
            '我方需要攻取位于经纬度坐标(100.1247, 13.6615)的夺控点，将陆战装备移动到夺控点处并消灭夺控点附近敌人可占领夺控点，地图范围为经度100.0923到100.18707，纬度范围为13.6024到13.6724，导弹发射车不能机动，固定部署在远处以提供火力支援。地图大部分为陆地，具有河流、桥梁和路网，在经纬度坐标(100.116,13.643)，(100.137,13.644)，(100.164,13.658)有东、中、西三个可供步兵占领和防御的的建筑物。它们之间有公路和桥梁相连，在中间那座建筑物附近跨越一条南北向河流。在此条公路以北地区，不再有东西方向桥梁供通行，但可以在适当位置隔河打击敌方目标'
        # jieguo += '请按照以下格式给出作战指令。进攻指令： [move, obj_id , x=int, y=int] , \n 如坦克MainBattleTank_ZTZ100_0和无人突击车ArmoredTruck_ZTL100_0进攻坐标(100.1247, 13.6615)，则指令为两条 [move, obj_id=MainBattleTank_ZTZ100_0, x=100.1247, y=13.6615],[move, obj_id=ArmoredTruck_ZTL100_0, x=100.1247, y=13.6615]  \n停止指令： [stop, obj_id],\n  如步兵Infantry0停止当前行动，则指令为[stop, obj_id=Infantry0] \n 步兵下车指令: [off_board, obj_id] , \n 如步战车WheeledCmobatTruck_ZB100_1内步兵立刻下车,则指令为 [off_board, obj_id=WheeledCmobatTruck_ZB100_1] '  
        jieguo += "敌方为蓝方，初始部署位置为(100.1247, 13.6615)，拥有坦克、步兵战车、步兵、无人突击车、巡飞弹、无人机、防空导弹发射车等装备，在东、中、西建筑物内有驻守有蓝方步兵，防空导弹发射车固定部署在夺控点周围一定范围内，在未受打击时能够完全拦截我方导弹。推演开始后，蓝方地面单位将进行机动，靠近建筑物和交通线布防，并派遣巡飞弹、无人机等前出侦察。根据我方行动，敌方有可能沿交通线调动兵力，阻击我方单位前进。因此，我方应该充分侦察，发挥地面火力优势，优先消灭对方防空导弹发射车后有效利用我方导弹打击敌地面目标。"  

        jieguo += "现在我们需要在敌情不确定的情况下做出决策，你作为决策者，目标是在考虑了不确定的敌情的基础上给出最优的的动作。"

        

        return jieguo
    
    def prepare_actions(self, choices:list):
        # how the actions are enumerated
        # 在我们这个里面就有点难顶了，如果真的好好搞的话维度控制不下来了。
        # 但是先不慌，先全部联通试一把。
        actions_str = "以下是可以选择的动作：\n"
        i=0
        for action in choices:
            i=i+1 
            actions_str += "动作" +str(i)+ action + "\n"

        return actions_str

    def prepare_state_prompt(self,state_discription:dict):
        geshu = len(state_discription.keys())
        state_str = ""
        # state_str += "现在我们需要在敌情不确定的情况下做出决策，你作为决策者，目标是在考虑了不确定的敌情的基础上给出最优的的动作。此前你已经给出了未来可能的敌情预测，用于支撑决策。"
        state_str = "态势由一个"+str(geshu)+"维的向量表示，其中每一个都是随机的变量，态势变量和它们的含义如下： \n"
        # 这里还是主要照着人家的那个来搞。
        for key in state_discription.keys():
            state_str += key + " : " + str(state_discription[key]) + "\n"
        
        return state_str
    
    def prepare_state_action_prompt(self,action_choice, state_candidates):
        # how the state-action pair is enumerated
        pair_index = 0 
        pair_str = ""
        state_action_list = [] 
        for action in action_choice:
            for state in state_candidates.keys():
                pair_index += 1
                state_str = "状态："
                state_str += self.get_str_from_json2(state_candidates[state]) 
                # state_str+= "。"
                pair_str += "状态-动作对" + str(pair_index) + " 。 " + state_str + action + "\n"
                state_action_pair_single = {}
                state_action_pair_single["state"] = state_str
                state_action_pair_single["action"] = action
                state_action_list.append(state_action_pair_single)
        # print(pair_str)
        return pair_str, state_action_list
    
    def prepare_belief_prompt(self):
        # 不要骗自己了，直接怎么快怎么来了。
        belief_list_str = ""
        for belief_str in belief2score.keys():
            belief_list_str += "“"+belief_str + "”，"

        return belief_list_str
    
    def prepare_utility_prompt(self,human_intent = "none"):
        # 后面要多方案或者要人工介入的话，就在这里面改。增加效用。
        if human_intent == "none":
            human_intent = "制定一个绕开敌方主要设防区域的进攻方案，控制我方损失，并尽量优先打击敌方防空力量。"
        utility_prompt = "我们是红方指挥官，需要为红方制定进攻方案，方案分步骤分阶段进行，现需要确定当前当前态势下，下一阶段采取的动作。希望达到的效果是" + human_intent + "。"
        
        return utility_prompt 

    def prepare_preference_prompt(self,state_action_batch:list):
        preference_prompt = "前面我已给出一系列状态动作对组合，其中状态从你给出的状态分布预测中取出，动作则从动作空间中均匀选出。现在我希望通过你对状态-动作对的比较，来建立一个效用函数。"
        format_instruction = "你应当以JSON格式给出回应，其中包含以下字段：\n" + \
        "decision: 一个字符串，用于表示你推荐的状态-动作对。输出格式应该和前面列出的状态动作对一致，例如：状态-动作对5\n" + \
        "rank: 一个由整数组成的列表，表示你对状态-动作对的偏好顺序。列表中的每个整数对应一个状态-动作对，以偏好程度降序排列，整数越小表示越偏好。例如，[1, 3, 2] 表示你偏好状态-动作对1，其次状态-动作对3，最后状态-动作对2。 \n" + \
        "explanatioin: 一个字符串，用于详细解释你做出决定的原因，对每个行动方案，应该包含期望的行动方向、所需单位等，以及影响它们的因素"
        
        # 这段是别人那里抄来的，感觉貌似没啥用呀，先放着吧，屎山就屎山一点了先能用再说别的。
        # preference_prompts = [] 
        # for state_action_pairs in state_action_batch:
        #     preference_prompts.append(
        #         format_query(
        #             preference_prompt + "\n\n".join(state_action_pairs) + "\n\n",
        #             format_instruction=format_instruction,
        #         )
        #     )
        
        preference_prompts = preference_prompt + format_instruction

        return preference_prompts

class type_transfer(object):
    # 这个是用来把抽象的装备类型化简一下的，搞成中文的。
    def __init__(self):
        self.unit_type_dict = {
            'ArmoredTruck': '无人战车' , 
            'Howitzer' : '自行迫榴炮', 
            'infantry': '步兵',
            'MainBattleTank' : '坦克',
            'ShipboardCombat_plane' : '无人机',
            'WheeledCmobatTruck':'步战车', 
            'missile_truck' : '导弹发射车',
            'CruiseMissile': '巡飞弹',
            'JammingTruck': '干扰车'
        }
    def unit_type_transfer(self, unit_type:str):
        for key in list(self.unit_type_dict.keys()):
            if key in unit_type:
                unit_type_zhongwen = self.unit_type_dict[key]
                break
            else:
                unit_type_zhongwen = "其他"
        return unit_type_zhongwen

def format_query(
    query: str,
    format_instruction: str = "你应该把回答格式化为JSON对象",
):
    # 抄就完事儿了，好好看好好学，能抄就抄。
    return f"{query}\n{format_instruction}"

belief2score: Dict[str, float] = {
        "很可能": 6,
        "可能": 5,
        "有点可能": 4,
        "较不可能": 3,
        "不太可能": 2,
        "几乎不可能": 1,
        }

text_demo = '进攻指令：\n[move, obj_id=MainBattleTank_ZTZ100_0, x=100.138, y=13.6196],\n[move, obj_id=MainBattleTank_ZTZ100_1, x=100.138, y=13.6196],\n[move, obj_id=MainBattleTank_ZTZ100_2, x=100.138, y=13.6196],\n[move, obj_id=MainBattleTank_ZTZ100_3, x=100.138, y=13.6196],\n[move, obj_id=ArmoredTruck_ZTL100_0, x=100.138, y=13.6196],\n[move, obj_id=ArmoredTruck_ZTL100_1, x=100.138, y=13.6196],\n[move, obj_id=WheeledCmobatTruck_ZB100_0, x=100.138, y=13.6196],\n[move, obj_id=WheeledCmobatTruck_ZB100_1, x=100.138, y=13.6196],\n[move, obj_id=Howitzer_C100_0, x=100.138, y=13.6196],\n[move, obj_id=ShipboardCombat_plane0, x=100.137, y=13.644],\n[move, obj_id=RedCruiseMissile_0, x=100.116, y=13.643],\n[move, obj_id=RedCruiseMissile_1, x=100.164, y=13.658]'

text_demo_blue = '进攻指令：\n[move, obj_id=MainBattleTank_ZTZ200_0, x=100.138, y=13.6196],\n[move, obj_id=MainBattleTank_ZTZ200_1, x=100.138, y=13.6196],\n[move, obj_id=MainBattleTank_ZTZ200_2, x=100.138, y=13.6196],\n[move, obj_id=MainBattleTank_ZTZ200_3, x=100.138, y=13.6196],\n[move, obj_id=WheeledCmobatTruck_ZB200_0, x=100.138, y=13.6196],\n[move, obj_id=WheeledCmobatTruck_ZB200_1, x=100.138, y=13.6196],\n[move, obj_id=ShipboardCombat_plane1, x=100.137, y=13.644],\n[move, obj_id=BlueCruiseMissile_0, x=100.116, y=13.643],\n[move, obj_id=BlueCruiseMissile_1, x=100.164, y=13.658]'

text_DeLLMa_state = '{\n    "敌方经度": {\n        "靠中间": "很可能",\n        "偏西": "不太可能",\n        "偏东": "较不可能"\n    },\n    "敌方纬度": {\n        "靠北": "可能",\n        "中间": "很可能",\n        "靠南": "有点可能"\n    },\n    "敌方聚集程度": {\n        "高度聚集": "可能",\n        "中度分散": "很可能",\n        "极度分散": "较不可能"\n    },\n    "我方经度": {\n        "靠中间": "很可能",\n        "偏西": "不太可能",\n        "偏东": "几乎不可能"\n    },\n    "我方纬度": {\n        "靠北": "较不可能",\n        "中间": "很可能",\n        "靠南": "可能"\n    },\n    "我方聚集程度": {\n        "高度聚集": "几乎不可能",\n        "中度分散": "很可能",\n        "极度分散": "不太可能"\n    }\n}\n\n**决策解说**：\n\n根据当前设定的战场态势，我们首先生成了一个信度分布来描述敌我双方的战场可能状态。\n\n对于**敌方经度**，我们认为敌方很可能处于战场中间区域，这是因为蓝方初始部署位置就在夺控点附近，且他们可能会围绕建筑物和交通线进行布防。偏西和偏东的可能性相对较低，但也不能完全排除，因为敌方可能会根据战场形势进行机动。\n\n**敌方纬度**方面，我们认为敌方可能处于中间或靠北的位置，因为中间区域有建筑物和交通线，是双方争夺的焦点，而靠北区域则可能作为敌方的支援或预备队集结地。靠南的可能性相对较低。\n\n在**敌方聚集程度**上，我们认为敌方可能处于中度分散状态，因为他们需要在不同建筑物和交通线进行布防，同时又要保持一定的机动性以应对我方攻击。高度聚集和极度分散的可能性都相对较低。\n\n对于**我方经度**，我们很确定我方处于战场中间区域，因为我们的目标是攻取夺控点。偏西和偏东的可能性很低，因为我们没有理由偏离主要攻击方向。\n\n在**我方纬度**上，我们认为我方很可能处于中间区域，因为我们需要接近夺控点进行攻击。靠北的可能性相对较低，但也不能完全排除，因为我们可能需要利用北部地区进行迂回或侧翼攻击。靠南的可能性更低，因为那将远离我们的攻击目标。\n\n对于**我方聚集程度**，我们认为我方可能处于中度分散状态，因为我们需要利用不同的装备和战术手段对敌方进行多点攻击和侦察。高度聚集可能会使我们过于集中，容易受到敌方火力打击；而极度分散则可能降低我们的攻击力和协同作战能力。\n\n基于以上信度分布，我们可以制定以下初步决策：\n\n1. **优先侦察**：利用无人机和巡飞弹对敌方进行侦察，确定其具体位置、部署和动向。\n\n2. **火力打击**：在侦察到敌方防空导弹发射车后，立即利用导弹发射车进行远程火力打击，削弱其防空能力。\n\n3. **地面攻击**：在防空威胁降低后，利用坦克、步兵战车和无人突击车等地面装备对敌方进行多点攻击，同时利用自行迫榴炮提供远程火力支援。\n\n4. **占领夺控点**：在消灭敌方有生力量后，迅速将陆战装备移动到夺控点处并消灭附近敌人，占领夺控点。\n\n5. **灵活机动**：在攻击过程中，要根据战场形势灵活调整兵力部署和攻击方向，以应对敌方的机动和反击。\n\n以上决策需要根据实际情况进行动态调整和优化，以确保最终取得胜利。'

text_DeLLMa_utility = '```json\n{\n    "decision": "状态-动作对1",\n    "rank": [1, 4, 7, 2, 5, 8, 3, 6, 9, 10, 11, 12],\n    "explanation": "在分析了当前态势和可选动作后，我决定推荐状态-动作对1作为最优方案。\\n\\n首先，考虑到敌方很可能在中间经度区域活动，且纬度偏北，同时敌方单位可能处于中度分散状态，这为我们提供了一定的战术灵活性。我方当前位置很可能在中间经度偏西，纬度偏南，且我方单位中度分散，这有利于我们进行灵活的兵力调配。\\n\\n在选择进攻方向时，我们需要绕开敌方主要设防区域，并优先打击敌方防空力量。由于敌方防空导弹发射车固定部署在夺控点周围，因此我们需要尽快接近并摧毁这些威胁。偏东方向进攻可以让我们利用地形和建筑物作为掩护，同时避开敌方可能设置的防线。\\n\\n在兵力配置上，选择坦克和自行迫榴炮作为先头部队是合理的。坦克具有强大的机动性和火力，能够在移动中攻击敌方目标，而自行迫榴炮则可以在停下后提供远程火力支援。这样的组合既能保证火力输出，又能保持一定的机动性。\\n\\n相比之下，其他方案要么兵力过于集中（如状态-动作对3、6、9、12），可能遭受敌方集中火力的打击；要么进攻方向不够灵活（如状态-动作对2、5、8），容易被敌方预判；要么兵力配置不够合理（如状态-动作对10、11），可能导致火力不足或机动性下降。\\n\\n因此，综合考虑敌方位置、我方位置、兵力配置和进攻方向等因素，我认为状态-动作对1是最优的选择。它既能保证我方兵力的有效利用，又能最大限度地减少损失，同时优先打击敌方防空力量，为后续进攻创造有利条件。"\n}\n```'
if __name__ == "__main__":
    # 测试一下
    shishi = text_transfer()
    commands = shishi.text_to_commands(text_demo)
    shishi.get_num_commands()
    pass 