# 还是逃不了，还是得来个主函数才比较阳间一点儿
from support.Env import *
from templates.commands import command_transfer
from mission_arrange.mission_arrange import mission_arrange
from text_transfer.text_transfer import text_transfer
import argparse, queue, time,threading

class auto_run_comunicator():
    # 还是那个路数，开个进程一直转着，看GUI那头有什么东西发过来。发过来的先缓存着，然后每隔一段时间处理一次。
    # 意图识别、调用不同函数的，在这里面先做一个比较拉但是能用的。后面如果要好的，再说。
    def __init__(self) -> None:
        
        self.__init_envs()
        self.__init_seat()
        
        self.flag_init = True # 这个用来标记当前是不是第一步。
        self.flag_debug = False
        self.config = {} 

        self.mission_arrange = mission_arrange() 
        self.text_transfer = text_transfer()

        self.commands_queue = queue.Queue(114514)
        self.send_queue = queue.Queue(114514) # 干脆上来先打好基础，发送的专门整个消息队列好了，不然不是就乱了嘛。
        # 感叹一句，再往下是不是就要来线程锁什么的了。
        self.receive_queue = queue.Queue(114514) # 接收过来的先不解析，先存着一下。

        self.command_transfer = command_transfer()

        pass

    def __init_envs(self):
        self.env_dict = {} 
        net_args = self.__init_net(ip = "127.0.0.1", port = 30001)
        self.max_episode_len = self.net_args.max_episode_len
        # self.env = Env(self.net_args.ip, self.net_args.port)
        env_single = Env_server(self.net_args.ip, self.net_args.port,seat="commandor")
        self.env_dict["commandor"] = env_single
        print("__init_envs: unfinished yet")


    def __init_net(self,ip = "127.0.0.1", port = 30001):
        parser = argparse.ArgumentParser(description='Provide arguments for agent.')
        parser.add_argument("--ip", type=str, default="127.0.0.1", help="Ip to connect")
        # parser.add_argument("--ip", type=str, default="192.168.43.93", help="Ip to connect")
        parser.add_argument("--port", type=str, default=30001, help="port to connect")
        parser.add_argument("--epochs", type=int, default=200, help="Number of training epochs to run")  # 设置训练轮次数
        parser.add_argument("--max-episode-len", type=int, default=3000, help="maximum episode length")
        net_args = parser.parse_args()
        # self.net_args = net_args
        return net_args        
    
    def __init_seat(self):
        # 分席位的处理也是在这里处理一下算了。原则上只需要跑这一个后端python，是有机会把分席位的事情都干了的。有几分劳动竞赛那个对战的意思了，但是要防止像当时那样来回修改和屎山化。各方比较好接受的是前端大哥们写，然后我能改多少改点儿。
        self.seat_access = {} 
        self.seat_access["status"] = ["态势评估"] # 态势情报席位
        self.seat_access["support"] = ["装备编辑","子任务编辑","历史方案编辑"] # 信息支援席位
        self.seat_access["commandor"] = ["root"] # 指挥控制席位，完全权限。
        self.seat_access["evaluator"] = ["方案编辑","方案评估"] # 方案评估席位
        pass
    
    def run_mul(self):
        # 和之前类似，这个就是开起来跑着就好的多线程不阻塞的
        for env in self.env_dict.values():
            env.init_socket()
        
        thread1 = threading.Thread(target=self.run_single_receive)
        thread2 = threading.Thread(target=self.run_single_send)
        thread3 = threading.Thread(target=self.run_single_handle)

        # 然后就启动线程呗
        thread1.start()
        thread2.start()    
        thread3.start()

        print("auto_run_communicator: successfully started, wuhu, qifei")    
        pass 

    def run_single_receive(self):
        # 这个是单线程的，无限循环写在这里面。


        while(True):
            time.sleep(1.14514)
            for seat in self.env_dict.keys():
                gui_order_str = self.env_dict[seat].receive_str()
                # 从方便调试的角度考虑，接收进来应该先放队列，然后再统一处理
                gui_order_dict = {seat:gui_order_str}
                self.receive_queue.put(gui_order_dict)

        pass

    def run_single_send(self):
        # 这个是单线程的，无限循环写在这里面。
        while(True):
            time.sleep(1.14514)
            if not self.send_queue.empty():
                send_str = self.send_queue.get()
                for seat in self.env_dict.keys():
                    self.env_dict[seat].send_str(send_str)
        pass

    def run_single_handle(self):
        # 这个是单线程的，无限循环写在这里面。
        # 这个是处理指令的
        while(True):
            if not self.receive_queue.empty():
                receive_dict_single = self.receive_queue.get()
                receive_str = receive_dict_single.value()
                receive_seat = receive_dict_single.key()
                flag_pass = self.check_seat_expedient(receive_seat,receive_seat)

        pass

    def get_command(self):
        # 这个就是从GUI那边拿指令的。每一步执行一次的，收命令过来弄到队列里面去。
        pass

    def send_response(self,response_str:str):
        # 这次在后端就分开，显示的命令是显示的命令，增加点儿掌控力.
        pass 

    def send_plan(self,new_plans:list):
        # 把多方案解析解析，给GUI发过去。
        pass

    def send_evaluate(self, pinggu):
        # 给GUI发个评估结果。
        pass

    def handle_command_expedient(self,command):
        # 也是权宜之计。这个就是执行一条完整的指令，比如一次方案编辑，之类的。其实是在为后面做准备了有点儿.
        # 这个和收信息那个应该放在不同的线程。
        pass

    def check_seat_expedient(self, seat, command:str ):
        # 权宜之计。鉴权的说法。
        search_key = self.seat_access[seat]
        flag_pass = True
        if command.find(search_key)>0:
            # 那就认为是合法的。
            flag_pass = True
        else:
            flag_pass = False
        return flag_pass

  