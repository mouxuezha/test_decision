# 该删除的删除，防止变成屎山。这个在新的环境下要配合着DeLLMa使用了。
# 需要约定一下命令格式了。
import os.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import math
import json
from typing import Optional, Dict, List, Tuple, Callable
import random,copy 
from templates.gis import gis

class text_transfer(object):
    def __init__(self) -> None:
        self.command_type_list = ["move", "stop", "off_board"]
        self.type_transfer = type_transfer()
        self.num_commands = [0,0] # 第一个是转化成功的commands，第二个是转化失败的commands 
        self.ed_lat,  self.ed_lon =  39.70, 2.68984
        self.tar_lat, self.tar_lon = 39.7600, 2.7100

        self.__init_type()

        self.__init_DeLLMa()

        self.gis=gis()

    
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
        self.planned_str = ""

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
        json_str = self.del_note_from_str(json_str)
        json_str = "{" + json_str + "}"
        try:
            json_jieguo = json.loads(json_str)
        except:
            print("text_transfer: json_str is not a valid json, please check the input_str")
            json_jieguo = {} 
        return json_jieguo
    
    def del_note_from_str(self, input_str:str):
        str_qian = "//"
        str_hou = "\n"

        str_qianhou_list = [] 
        str_qianhou_list.append(["//","\n"])
        str_qianhou_list.append(["（","）"])
        str_qianhou_list.append(["(",")"])
        
        output_str = input_str
        for str_qianhou in str_qianhou_list:
            str_qian = str_qianhou[0]
            str_hou = str_qianhou[1]
        
            while(str_qian in output_str):
                index_qian = output_str.find(str_qian)
                sub_str = output_str[index_qian:]
                index_hou = sub_str.find(str_hou)
                sub_str2 = sub_str[0:index_hou]
                output_str = output_str.replace(sub_str2, "") # 也行吧，AI给出来的这个写法比我想的似乎还舒服一些。

        return output_str
    
    def clean_the_str(self, input_str:str):
        # 这个是清理字符串的，把一些没用的符号去掉.
        clean_list = ["**","//"]
        for clean_str in clean_list:
            while clean_str in input_str:
                input_str = input_str.replace(clean_str,"")

        # 然后特殊处理。
        while "\n\n" in input_str:  
            input_str = input_str.replace("\n\n","\n")

        # 然后继续特殊处理，把json切走。
        if "json" in input_str:
            # 那就是说里面有怪东西
            index_qian = input_str.find("json")
            sub_str = input_str[index_qian:]
            if "```" in sub_str:
                index_hou = sub_str.rfind("```")
            else:
                index_hou = sub_str.find("}")
            
            input_str = input_str.replace(sub_str[0:index_hou+1],"")

        return input_str
    
    def clean_the_str2(self,input_str:str):
        # 为了防止影响别的地方的json识别，把输入的字符串里面的会影响的东西都弄走。
        clean_list = ["json","```","``","`","{","}","\n","\\n"," ","    "]
        for clean_str in clean_list:
            while clean_str in input_str:
                input_str = input_str.replace(clean_str,"")
        
        # 然后保险起见把英文标点符号都弄成中文的。
        input_str = input_str.replace("\"","“")
        input_str = input_str.replace(":","：")
        input_str = input_str.replace(",","，")
        input_str = input_str.replace("(","（")
        input_str = input_str.replace(")","）")
        input_str = input_str.replace("[","（")
        input_str = input_str.replace("]","）")

        return input_str

    def get_str_from_json(self, json_jieguo:dict):
        # 把json转成字符串
        # 直接转效果不好，还是阳间一点比较好
        # json_str = json.dumps(json_jieguo)
        json_str = ""
        for key in json_jieguo:
            json_str += key+":"
            for key2 in json_jieguo[key]:
                json_str += "“"+key2 + "”：“"+str(json_jieguo[key][key2]) + "”,"
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
    
    def get_planned_str(self,planned_str):
        # 叠层数多了，一直传参有点傻逼，干脆搞个这个了。丑点儿但是能用。
        self.planned_str = planned_str
    
    def get_planned_unit_type(self,planned_unit_type):
        self.planned_unit_type = planned_unit_type

    def get_num_commands(self):
        # 这个算是结果处理，用来看有多少
        str_buffer = "成功识别指令{}个，识别失败{}个。".format(self.num_commands[0], self.num_commands[1])
        str_buffer = str_buffer + "\n识别成功率：" + str(self.num_commands[0]/(self.num_commands[0]+self.num_commands[1]+0.0000001))
        
        print(str_buffer)
        return str_buffer
    
    # 这几个prepare开头的是服务于DeLLMa的。
    def prepare_context(self,status=[],**kargs):
        # how the context is prepared
        # 加了相对专业一些的gis数据处理，讲道理。
        # 这东西引用的地方有点多，还是直接在这里改吧。
        if ("gis_str" in kargs) or True:
            # gis_str = kargs["gis_str"]
            print("prepare_context: gis str enabled.")
            gis_str = self.gis.get_gis_str()
        else:
            gis_str = "地图范围为经度100.0923到100.18707，纬度范围为13.6024到13.6724，地图大部分为陆地，具有河流、桥梁和路网，在经纬度坐标[100.116,13.643]，[100.137,13.644]，[100.164,13.658]有东、中、西三个可供步兵占领和防御的建筑物。它们之间有公路和桥梁相连，在中间那座建筑物附近跨越一条南北向河流。在此条公路以北地区，不再有东西方向桥梁供通行，但可以在适当位置隔河打击敌方目标。" # 这个是原版的，随便写了几句，放这里是为了保持兼容性。

        # 这个好说，就是场景和态势嘛，可以从text_JSQL里面抄。
        jieguo = '请作为兵棋推演游戏的玩家，设想一个陆战攻防场景。' + \
            '我方为红方，拥有坦克、步兵战车、步兵、自行迫榴炮、无人突击车、巡飞弹、无人机、导弹发射车、电子干扰车等装备，步兵下车后作战。我方自行迫榴炮具备较大的射程和载弹量，但只能在停下后攻击，坦克、无人突击车、无人机等则可以在移动中展开攻击' + gis_str + \
            '我方需要攻取位于经纬度坐标[100.1247, 13.6615]的夺控点，将陆战装备移动到夺控点处并消灭夺控点附近敌人可占领夺控点，导弹发射车不能机动，固定部署在远处以提供火力支援。推演以帧为单位推进，每一帧对应推演中的1秒，共进行5000帧，推演中装备的移动速度均与现实中类似，可据此估计双方位置'
        # jieguo += '请按照以下格式给出作战指令。进攻指令： [move, obj_id , x=int, y=int] , \n 如坦克MainBattleTank_ZTZ100_0和无人突击车ArmoredTruck_ZTL100_0进攻坐标(100.1247, 13.6615)，则指令为两条 [move, obj_id=MainBattleTank_ZTZ100_0, x=100.1247, y=13.6615],[move, obj_id=ArmoredTruck_ZTL100_0, x=100.1247, y=13.6615]  \n停止指令： [stop, obj_id],\n  如步兵Infantry0停止当前行动，则指令为[stop, obj_id=Infantry0] \n 步兵下车指令: [off_board, obj_id] , \n 如步战车WheeledCmobatTruck_ZB100_1内步兵立刻下车,则指令为 [off_board, obj_id=WheeledCmobatTruck_ZB100_1] '  
        jieguo += "敌方为蓝方，初始部署位置为[100.1247, 13.6615]，拥有坦克、步兵战车、步兵、无人突击车、巡飞弹、无人机、防空导弹发射车等装备，在东、中、西建筑物内有驻守有蓝方步兵，防空导弹发射车固定部署在夺控点周围一定范围内，在未受打击时能够完全拦截我方导弹。推演开始后，蓝方地面单位将进行机动，靠近建筑物和交通线布防，并派遣巡飞弹、无人机等前出侦察。根据我方行动，敌方有可能沿交通线调动兵力，阻击我方单位前进。以推演结束时对夺控点的占领情况和战损比情况来确定胜负，我方地面单位机动到夺控点并保持40帧即可占领夺控点，战损比以双方分数计算，导弹发射车50分，坦克20分，装甲车辆和无人机15分，步兵和巡飞弹5分。因此，我方应该充分侦察，发挥地面火力优势，优先消灭对方防空导弹发射车后有效利用我方导弹打击敌地面目标。"  
        if len(self.planned_str)>0:
            # 那就是之前已经有了，把之前的传进来。
            jieguo += self.planned_str
        else:
            # 没有就先给个默认的。
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
        
        # 为了防止后面报错，这里做一个兼容，就是如果循环完了都没有list，那么list里面补充一个空的。
        if len(state_action_list)==0:
            state_action_list.append({"state":"","action":""})
            print("这种情况按说不应该出现，查查为啥。")

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

    def plan_list_to_str(self,plan_list:list):
        # 这个是想一个转换的方式把方案给过去。
        geshu = len(plan_list)
        plan_list_dict = {}
        for i in range(geshu):
            plan_single = plan_list[i]
            if plan_single.id_str == "none":
                # 那就改个名字。
                plan_single.id_str = "方案" + str(i+1)
            
            # 真的开始提炼了。先搞成dict，再统一转好了。
            plan_list_dict[plan_single.id_str] = self.plan_single_to_str(plan_single)


        # 最后转成字符串拿出去，岂不美哉。
        plan_list_str = json.dumps(plan_list_dict,ensure_ascii=False)
        return plan_list_str
    
    def plan_list_to_str2(self,plan_list:list):
        # 行吧，这个是按照雪楠哥他们的格式重新弄的。
        plan_list_str = "{\"SchemesDataList\":["
        geshu = len(plan_list)
        for i in range(geshu):
            plan_single = plan_list[i]
            if plan_single.id_str == "none":
                # 那就改个名字。
                plan_single.id_str = "方案" + str(i+1)
            plan_single_str = self.plan_single_to_str2(plan_single)
            plan_list_str += plan_single_str + ","

        plan_list_str = plan_list_str[0:-1] # 删除一个多余的逗号
        # plan_list_str += "],\"msgCommid\":\"\"}" 
        # 这里得加一个默认的颜色，用来和新的结构对应上
        plan_list_str += "],\"msgCommid\":\"\",\"color\":"+str(1)+"}" 
        return plan_list_str
    
    def plan_single_to_str(self,plan_single):
        # 这个是想一个转换的方式把方案给过去。
        plan_single_dict = {} 
        plan_single_dict["id_str"] = plan_single.id_str
        plan_single_dict["target_str"] = plan_single.target_str
        plan_single_dict["submission_list_num"] = len(plan_single.submission_list)
        for submission_single in plan_single.submission_list:
            submission_single_dict = self.submission_single_to_str(submission_single)
            submission_id = submission_single.id_str
            plan_single_dict[submission_id] = submission_single_dict

        return plan_single_dict
    
    def plan_single_to_str2(self, plan_single):
        # 行吧，这个是按照雪楠哥他们的格式重新弄的。
        plan_singe_str = "{\"SchemesName\":\""+ plan_single.id_str +"\",\"SchemesNameText\":\""+plan_single.target_str+"\",\"schemesItems\":["
        # index = 0 
        for submission_single in plan_single.submission_list:
            submission_single_str = self.submission_single_to_str2(submission_single)
            plan_singe_str += submission_single_str + ","
            # # 这里加点儿电磁的东西。
            # if(submission_single.force_arrange == "装甲车等其他地面力量"):
            #     submission_single_ECM = self.submission_single_to_ECM(submission_single,index=index)
            #     submission_single_ECM_str = self.submission_single_to_str2(submission_single_ECM)
            #     plan_singe_str += submission_single_ECM_str + ","            
            # index=index+1
        
        plan_singe_str = plan_singe_str[0:-1] # 删除一个多余的逗号
        plan_singe_str +="]}"
        
        return plan_singe_str
    
    def submission_dict_to_str(self,submission_dict):
        all_dict = {}
        all_dict["SchemesDataList"] = submission_dict
        all_dict["msgCommid"] = ""
        all_dict["color"] = 0
        # submission_str = json.dumps(all_dict,ensure_ascii=False)
        submission_str = json.dumps(submission_dict, ensure_ascii=False)
        return submission_str

    def submission_single_to_ECM(self,submission_single,index=0):
        # 修改生成电子战方案。原则上不应该放这里的，不过不管了下次一定。
        submission_single_new = copy.deepcopy(submission_single)
        model_selected, submodel_selected = self.generate_ECM_model()

        submission_single_new.id_str = "电子对抗" + str(index)
        submission_single_new.type_str = model_selected
        submission_single_new.force_arrange = "电子干扰车"
        submission_single_new.target_str = submodel_selected
        
        return submission_single_new

    def submission_single_to_str2(self,submission_single):
        
        # 行吧，这个是按照雪楠哥他们的格式重新弄的。每个子任务分别处理
        # 为了复用接口，直接用alt传time_arrange[0]了，丑陋但是有用。
        submission_str = "{\"alt\":"+str(submission_single.time_arrange[0])+",\"force_arrange\":\""+submission_single.force_arrange+"\",\"id\":\""+submission_single.id_str+"\",\"lat\":"+str(submission_single.space_arrange[1])+",\"lon\":" + str(submission_single.space_arrange[0]) + ",\"type\":\"" + submission_single.type_str+"\"}"
        
        return submission_str
        # pass
    
    def submission_single_to_str(self,submission_single):
        # 这个是想一个转换的方式把方案给过去。每个子任务分别处理。
        submission_single_dict = {} 
        submission_single_dict["id_str"] = submission_single.id_str
        submission_single_dict["target_str"] = submission_single.target_str
        submission_single_dict["type_str"] = submission_single.type_str
        submission_single_dict["time_arrange"] = submission_single.time_arrange
        submission_single_dict["space_arrange"] = submission_single.space_arrange
        submission_single_dict["force_arrange"] = submission_single.force_arrange
        # submission_single_dict["space_arrange"] = submission_single.space_arrange
        # submission_single_dict["space_arrange"] = submission_single.space_arrange
        # submission_single_dict["space_arrange"] = submission_single.space_arrange
        # submission_single_dict["space_arrange"] = submission_single.space_arrange

        return submission_single_dict
    
    def response_wrap(self, response_str:str, color = 1 ):
        # 这个是包装一下 # 这边有颜色显示，0,：白的，123：彩色。
        response_str = self.clean_the_str(response_str)
        response_str = self.clean_the_str2(response_str)
        if "秒期间" in response_str:
            color = 2 
        wrapped_str = "{\"SchemesDataList\":[],\"msgCommid\":\""+response_str+"\", \"color\" : "+str(color)+"}"        
        return wrapped_str

    def generate_ECM_model(self):
        # 生成电子干扰的说法。
        model_dict ={}
        model_dict["电子攻击"] = ["噪声干扰，通过发射高功率噪声信号，阻塞敌方通信频段，使其无法有效通联。在发现敌巡飞弹后将波束集中于其上，全力确保我地面单位不受其影响","欺骗干扰，通过发射虚假信号，误导敌方探测，使其产生错误的目标信息。", "反辐射攻击，确定敌方主要辐射源位置后同步至我方自行迫榴炮和远程火力，选配相应弹种对其进行反辐射打击。"]
        model_dict["电子防护"] = ["频率捷变，快速改变通信工作频率，避开敌方干扰，优先保障我方各个作战单元之间的态势及时共享和命令及时传达。","功率管理，动态调整发射功率，降低我方电子干扰车被侦测和干扰的概率。","多路径传输，通过多条路径传输信号，提高抗干扰和抗截获能力，保障在受扰条件下我前线各地面作战单元之间仍能及时共享态势"] 
        model_dict["电子侦察"] = ["信号情报，通过侦测、截获和分析敌方电磁信号，获取战术情报，主要关注敌电子干扰车位置、模式和巡飞弹动向","测向与定位，确定敌方电子信号源的方向和精确位置，引导我远程火力打击敌电子干扰车和地面防空力量，并引导我地面作战力量规避敌方无人机和巡飞弹的打击与侦察。","被动侦察，仅接收敌方电磁信号，不主动发射信号，避免暴露我方电子干扰车位置。"]
        model_dict["电子静默"] = ["暂时关机，以防敌方进行针对性反辐射打击。","撤收转移，主动撤收并转移阵地，以规避敌方地面作战单元和远程反辐射火力，保全自身力量。"]

        model_list = list(model_dict.keys())
        index1 = random.randint(0,len(model_list)-1)
        model_selected = model_list[index1]
        submodel_list = model_dict[model_selected]
        index2 = random.randint(0,len(submodel_list)-1)
        submodel_selected = submodel_list[index2]

        return model_selected,submodel_selected


    def state_forcaste_to_str(self, state_forcaste:dict):
        # 这个是把state_forcaste转成字符串，面向输出，所以需要搞一些
        # return json.dumps(state_forcaste,ensure_ascii=False)
        state_forcaste_str = "  经过综合考虑当前推演场景、我方已决策的子任务序列、敌方的既往可能活动，方案智能生成分系统对后续局势做出如下推测：\n"
        for key_str in list(state_forcaste.keys()):
            state_forcaste_str += key_str
            state_forcaste_str += "："
            try:
                kenengxing_list = list(state_forcaste[key_str].keys())
            except:
                kenengxing_list = [] # 解析不出来就算了，反正拼接文字的，拉了一点儿也不是太有所谓。

            for i in range(len(kenengxing_list)):
                kenengxing_key = kenengxing_list[i]
                kenengxing_value = state_forcaste[key_str][kenengxing_key]
                state_forcaste_str += str(kenengxing_value)
                state_forcaste_str += kenengxing_key
                state_forcaste_str += "，"
            state_forcaste_str += "\n"

        return state_forcaste_str

    def str_squeeze(self,str_input,len_max=300):
        # 这个就是如果字符串太多了就把中间部分略去，搞成显示出来不那么抽象的效果。
        flag = False
        if flag:
            # 这个是选择开不开压缩功能了。直接在这里关比到处找引用来得快。
        
            len_qian = int(len_max*2/3) 
            len_hou = int(len_max*1/3)
            
            # 先前处理一下
            str_input = self.clean_the_str2(str_input)
            zishu = len(str_input)

            if zishu > len_max:
                # 那就启动压缩。
                
                str_qian = str_input[0:len_qian]
                str_hou = str_input[zishu-len_hou:-1]
                str_zhongjian = "……【过长显示已折叠】……"
                str_output = str_qian + str_zhongjian + str_hou
            else:
                str_output = str_input
        else:
            str_output = str_input
        
        return str_output
    
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

text_DeLLMa_state2 = '```json\n{\n    "敌方经度": {\n        "靠中间": "很可能",\n        "偏西": "可能",\n        "偏东": "较不可能"\n    },\n    "敌方纬度": {\n        "靠北": "很可能",  // 考虑到夺控点位置及蓝方初始部署，敌方可能在夺控点附近偏北位置\n        "中间": "不太可能",\n        "靠南": "几乎不可能"\n    },\n    "敌方聚集程度": {\n        "集中": "可能",  // 蓝方可能在中、东、西建筑物附近集中布防\n        "分散": "有点可能",\n        "非常分散": "不太可能"\n    },\n    "我方经度": {\n        "偏东": "很可能",  // 考虑到我方已确定偏东出击方向\n        "靠中间": "不太可能",\n        "偏西": "几乎不可能"\n    },\n    "我方纬度": {\n        "中间": "很可能",  // 我方在推进过程中可能处于地图的中间纬度区域\n        "靠北": "可能",\n        "靠南": "较不可能"\n    },\n    "我方聚集程度": {\n        "集中": "有点可能",  // 我方在攻击前可能会进行一定程度的集中以形成火力优势\n        "分散": "可能",  // 但为了侦察和机动，部分单位可能分散\n        "非常分散": "不太可能"\n    }\n}\n```\n\n**解说员视角下的兵棋推演比赛解说**：\n\n各位观众，欢迎来到这场紧张刺激的陆战攻防兵棋推演比赛。此刻，红方与蓝方正在一片广袤的陆地上展开激烈的较量，双方都在为夺取位于关键坐标(100.1247, 13.6615)的夺控点而竭尽全力。\n\n从当前态势来看，红方已经明确了偏东的出击方向，他们的坦克和自行迫榴炮等重型装备正在稳步向前推进。根据我们的信度分布分析，红方很可能在经度上偏东，纬度上处于中间位置，且他们的装备相对集中，以形成强大的火力优势。\n\n而蓝方方面，他们似乎并不打算轻易放弃这个重要的夺控点。他们的装备在经度上可能更加靠近中间位置，纬度上则更可能偏北，以利用地形和建筑物进行防御。蓝方的装备分散程度适中，既能够保持灵活性，又能够在关键时刻形成局部优势。\n\n现在，比赛进入了关键的阶段。红方需要充分发挥他们的地面火力优势，特别是要优先消灭蓝方的防空导弹发射车，以解除对我方导弹的威胁。同时，红方还需要利用无人机和巡飞弹等侦察手段，不断搜集敌方的情报，为后续的进攻提供有力的支持。\n\n而蓝方则可能会采取灵活的机动战术，利用河流、桥梁和路网等地形条件，不断调动兵力，阻击红方的进攻。他们还可能会利用建筑物作为掩体，进行顽强的抵抗。\n\n在接下来的推演中，我们可以期待双方更加精彩的战术运用和火力对决。红方能否成功突破蓝方的防线，占领夺控点？蓝方又能否凭借他们的坚韧和机智，守住这个重要的战略要地？让我们拭目以待，共同见证这场陆战攻防的巅峰对决！'

text_yanshi2 = '“decision“：“状态-动作对1“，“rank“：（1，4，7，2，5，8，3，6，9，10，11，12），“explanation“：“在分析了当前态势和可选动作后，我决定推荐状态-动作对1作为最优方案。\\n\\n首先，考虑到敌方很可能在中间经度区域活动，且纬度偏北，同时敌方单位可能处于中度分散状态，这为我们提供了一定的战术灵活性。我方当前位置很可能在中间经度偏西，纬度偏南，且我方单位中度分……【过长显示已折叠】……的推演中，我们可以期待双方更加精彩的战术运用和火力对决。红方能否成功突破蓝方的防线，占领夺控点？蓝方又能否凭借他们的坚韧和机智，守住这个重要的战略要地？让我们拭目以待，共同见证这场陆战攻防的巅峰对决'

# text_yanshi2 = '"\n' # 破案了，传这个过去会导致暴毙。# 但是并不止这一个，应该是沾了JSON的都不行本质上。

# text_yanshi2 = '```json\n{\n    "decision": "状态-动作对19",\n    "rank": [\n        19,\n        1,\n        4,\n        7,\n        10,\n        13,\n        16,\n        22,\n        2,\n        5,\n        8,\n        11,\n        14……【过长显示已折叠】……、多层次的进攻态势，以迷惑和分散敌方注意力，最终达成占领夺控点的目标。\\n\\n综上所述，空中侦察是当前态势下的最优选择，它能够为我方提供宝贵的情报支持，为后续进攻行动的成功奠定坚实基础。"\n}\n``'

if __name__ == "__main__":
    # 测试一下
    shishi = text_transfer()
    # commands = shishi.text_to_commands(text_demo)
    # shishi.get_num_commands()
    # shishi.get_json_from_str(text_DeLLMa_state2)
    shishi_str = shishi.str_squeeze(text_DeLLMa_utility+text_DeLLMa_state2)
    # shishi_str = shishi.clean_the_str2(text_DeLLMa_state2)
    print(shishi_str)
    pass 