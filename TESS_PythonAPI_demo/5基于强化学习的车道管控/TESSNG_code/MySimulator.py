import time
from threading import Thread
import numpy as np
import matplotlib.pyplot as plt
import torch
from PySide2.QtCore import *

from DLLs.Tessng import *
from my_code.model_RL import MADDPG
from my_code.functions import calc_state, calc_reward, setup_logger


class MySimulator(QObject, PyCustomerSimulator):
    signalRunInfo = Signal(str)
    forStopSimu = Signal()
    forReStartSimu = Signal()

    def __init__(self):
        QObject.__init__(self)
        PyCustomerSimulator.__init__(self)

        # 最大仿真次数
        self.Max_Simu_Count = 10
        # 仿真精度
        self.Simu_Accuracy = 5
        # 仿真倍速
        self.Simu_Spped = 100

        # 当前仿真次数
        self.current_simu_count = 0
        # 仿真开始时间
        self.simu_start_time = time.time()
        # 日志记录器
        self.logger = setup_logger("Log\\MySimulator.log")

        # 存放各路段的限速值(km/h)
        self.limit_speed = {1: 120, 2: 120, 3: 120, 4: 120}

        # 智能体数量
        self.num_agent = 2
        # 存放各个智能体每轮的reward
        self.all_epoch_rewards = [[] for _ in range(self.num_agent)]
        # 存放各个智能体当前轮的reward
        self.current_epoch_rewards = None

        # 初始化多智能体模型
        self.agent = MADDPG(self.num_agent)
        self.trainer_thread = Thread(target=self.agent.train_in_loop, daemon=True)
        self.trainer_thread.start()

    # 每轮仿真之前
    def ref_beforeStart(self, ref_keepOn):
        iface = tessngIFace()
        simuiface = iface.simuInterface()
        # 设置仿真精度
        simuiface.setSimuAccuracy(self.Simu_Accuracy)
        # 设置仿真倍数
        simuiface.setAcceMultiples(self.Simu_Spped)

        # 仿真次数加1
        self.current_simu_count += 1
        # 本轮仿真各智能体的累加reward
        self.current_epoch_rewards = np.zeros(self.num_agent)

        self.logger.info(f"第【{self.current_simu_count}】次仿真运行开始！")

    # 车辆限速
    def ref_reCalcdesirSpeed(self, vehi, ref_desirSpeed):
        if vehi.roadIsLink():
            ref_desirSpeed.value = self.limit_speed[vehi.roadId()] / 3.6 # m/s
            return True
        return False

    # 每帧仿真之后
    def afterOneStep(self):
        # TESSNG 顶层接口
        iface = tessngIFace()
        # TESSNG 仿真子接口
        simuiface = iface.simuInterface()
        # 当前正在运行车辆列表
        lAllVehi = simuiface.allVehiStarted()
        # 当前已仿真时间，单位：毫秒
        simuTime = simuiface.simuTimeIntervalWithAcceMutiples()
        # 获取当前仿真时间，单位：秒
        currentTime = round(simuTime/1000, 1)

        interval = 5*60 # s

        # 每5分钟计算一次
        if currentTime % interval == 0 and currentTime > 0:
            # 计算当前state
            current_states = np.array([calc_state(lAllVehis) for lAllVehis in ([simuiface.vehisInLink(1), simuiface.vehisInLink(2)], [simuiface.vehisInLink(3), simuiface.vehisInLink(4)])])
            
            if currentTime > interval:
                # 计算reward
                rewards = np.array([calc_reward(lAllVehis) for lAllVehis in ([simuiface.vehisInLink(1), simuiface.vehisInLink(2)], [simuiface.vehisInLink(3), simuiface.vehisInLink(4)])])
                self.logger.info(f"Rewards: {rewards}")
                self.current_epoch_rewards += rewards
                
                # 更新agent
                self.actions = torch.tensor(self.actions)
                rewards = torch.tensor(rewards)
                new_states = torch.tensor(current_states)
                self.agent.update_replay_memory((self.current_states, self.actions, rewards, new_states, False))
                
            # 更新当前state
            self.logger.info(f"Current Time: {currentTime-interval}s ~ {currentTime}s")
            self.logger.info(f"Current States: {[list(value) for value in current_states]}")
            self.current_states = torch.tensor(current_states)

            # 基于状态获取动作
            actions = self.agent.get_actions(self.current_states.float()).detach().numpy()
            self.logger.info(f"Raw actions:{[list(value)[0] for value in actions]}")
            # 网络输出为-1~1,转换为限速值60~120
            self.actions = np.array([min(60 + int((action+1)*3.5)*10, 120) for action in actions])
            self.logger.info(f"Actual Actions:{self.actions}")
            # 更新限速值
            self.limit_speed[1] = self.limit_speed[2] = self.actions[0]
            self.limit_speed[3] = self.actions[1]

            time.sleep(0.1)

        #每秒做一次小计，将结果通过信号发送出云
        if currentTime % 1 == 0:
            display_info = [
                f"最大仿真次数：{self.Max_Simu_Count}",
                f"当前仿真次数：{self.current_simu_count}",
                f"运行车辆数：{len(lAllVehi)}veh",
                f"仿真时间：{currentTime}s",
                f"上游路段的限速值：{self.limit_speed[1]}km/h",
                f"事故路段的限速值：{self.limit_speed[3]}km/h"
            ]
            self.signalRunInfo.emit("\n".join(display_info))

    # 每轮仿真之后
    def afterStop(self):
        spend_time = time.time() - self.simu_start_time
        self.logger.info(f"第【{self.current_simu_count}】次仿真运行结束！当前已经用时为{spend_time:.1f}秒\\n")
        
        # 记录当前轮的reward
        for i in range(self.num_agent):
            self.all_epoch_rewards[i].append(self.current_epoch_rewards[i])
        self.logger.info(f"all_epoch_rewards: {self.all_epoch_rewards}")

        # for i in range(self.num_agent):
        #     epoch_name = 'model_parm/actors_agent{}_epoch{}.pth'.format(i+1, self.mSimuCount)
        #     torch.save(agent.actors[i].state_dict(), epoch_name)
        #
        #     critic_name = 'model_parm/critic_agent{}_epoch{}.pth'.format(i+1, self.mSimuCount)
        #     torch.save(agent.critics[i].state_dict(), critic_name)
        
        # 判断当前仿真次数是否达到最大仿真次数
        if self.current_simu_count < self.Max_Simu_Count:
            # 再次开启仿真
            self.forReStartSimu.emit()
            return

        print(self.all_epoch_rewards)
        
        self.agent.terminate = True
        self.trainer_thread.join()

        # 绘制并保存reward变化图
        for i in range(self.num_agent):
            plt.plot(range(1, self.Max_Simu_Count+1), self.ep_rewards[i], label='agent_{}'.format(i+1))
        plt.legend(loc='best')
        plt.xlabel("SimuCount")
        plt.ylabel("Reward")
        plt.xlim(1,20)
        plt.xticks(range(1, 21, 1))
        plt.savefig('Data\\reward.png')

        spend_time = time.time() - self.simu_start_time
        self.logger.info(f"【{self.Max_Simu_Count}】轮仿真已经全部运行结束，总用时为{spend_time:.1f}秒!!!")


