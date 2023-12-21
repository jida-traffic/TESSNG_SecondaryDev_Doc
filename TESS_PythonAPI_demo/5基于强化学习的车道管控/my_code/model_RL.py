import numpy as np
import time
import random
from copy import deepcopy
from collections import deque
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import Adam


class Critic(nn.Module):
    def __init__(self, n_agent, dim_observation, dim_action):
        super(Critic, self).__init__()
        self.n_agent = n_agent
        self.dim_observation = dim_observation
        self.dim_action = dim_action
        obs_dim = dim_observation * n_agent
        act_dim = self.dim_action * n_agent
        
        self.FC1 = nn.Linear(obs_dim, 196)
        self.FC2 = nn.Linear(act_dim, 128)
        self.FC3 = nn.Linear(196 + 128, 128)
        self.FC4 = nn.Linear(128, 64)
        self.FC5 = nn.Linear(64, 1)

    # obs: batch_size * obs_dim
    def forward(self, obs, acts):
        result = F.leaky_relu(self.FC1(obs), 0.2)
        act_result = F.leaky_relu(self.FC2(acts), 0.2)
        combined = torch.cat([result, act_result], 1)
        result = F.leaky_relu(self.FC3(combined), 0.2)
        return self.FC5(F.leaky_relu(self.FC4(result), 0.2))


class Actor(nn.Module):
    def __init__(self, dim_observation, dim_action):
        super(Actor, self).__init__()
        self.FC1 = nn.Linear(dim_observation, 256)
        self.FC2 = nn.Linear(256, 128)
        self.FC3 = nn.Linear(128, 64)
        self.FC4 = nn.Linear(64, dim_action)

    def forward(self, obs):
        result = F.leaky_relu(self.FC1(obs), 0.2)
        result = F.leaky_relu(self.FC2(result), 0.2)
        result = F.leaky_relu(self.FC3(result), 0.2)
        result = torch.tanh(self.FC4(result))
        return result


class MADDPG:
    def __init__(self, n_agents, dim_obs=3, dim_act=1, REPLAY_MEMORY_SIZE=6_000, MIN_REPLAY_MEMORY_SIZE=10, MINIBATCH_SIZE=10):
        self.replay_memory = deque(maxlen=REPLAY_MEMORY_SIZE)
        self.MIN_REPLAY_MEMORY_SIZE = MIN_REPLAY_MEMORY_SIZE
        self.MINIBATCH_SIZE = MINIBATCH_SIZE

        self.target_update_counter = 0
        self.n_agents = n_agents
        self.terminate = False
        self.last_logged_episode = 0
        self.training_initialized = False

        self.notBegin = True
        self.GAMMA = 0.95
        self.tau = 0.01

        self.var = [1 for _ in range(n_agents)]
        self.criterion = nn.MSELoss()

        self.actors = [Actor(dim_obs, dim_act) for _ in range(n_agents)]
        self.critics = [Critic(n_agents, dim_obs, dim_act) for i in range(n_agents)]
        
        self.actors_target = deepcopy(self.actors)
        self.critics_target = deepcopy(self.critics)

        self.n_agents = n_agents
        self.n_states = dim_obs
        self.n_actions = dim_act
        self.critic_optimizer = [Adam(x.parameters(), lr=0.1) for x in self.critics] # 默认0.001
        self.actor_optimizer = [Adam(x.parameters(), lr=0.1) for x in self.actors] # 默认0.001

        self.train_step = 0
        self.scale_reward = 0.1

    def update_replay_memory(self, transition):
        self.replay_memory.append(transition)

    def train(self):
        if len(self.replay_memory) < self.MIN_REPLAY_MEMORY_SIZE:
            return

        FloatTensor = torch.FloatTensor
        c_loss = []
        a_loss = []
        for agent in range(self.n_agents):
            minibatch = random.sample(self.replay_memory, self.MINIBATCH_SIZE)

            state_batch = np.array([transition[0].detach().numpy() for transition in minibatch])
            action_batch = np.array([transition[1].detach().numpy() for transition in minibatch])
            reward_batch = np.array([transition[2].detach().numpy() for transition in minibatch])
            dones_batch = np.array([transition[4] for transition in minibatch])

            tensor_current_states = torch.from_numpy(np.array(state_batch).reshape((-1, self.n_agents, self.n_states))).float()

            tensor_actions = torch.from_numpy(np.array(action_batch).reshape((-1, self.n_agents, self.n_actions))).float()

            tensor_rewards = torch.from_numpy(np.array(reward_batch).reshape((-1, self.n_agents))).float()

            tensor_dones = torch.from_numpy(np.array(dones_batch).reshape((-1,1))).float()
            whole_state = tensor_current_states.view(self.MINIBATCH_SIZE, -1)
            whole_action = tensor_actions.view(self.MINIBATCH_SIZE, -1)
            self.critic_optimizer[agent].zero_grad()
            current_Q = self.critics[agent](whole_state, whole_action)

            new_current_states = np.array([transition[3].detach().numpy() for transition in minibatch])

            tensor_new_current_states = torch.from_numpy(np.array(new_current_states).reshape((-1, self.n_agents, self.n_states))).float()

            non_final_next_actions = [self.actors_target[i](tensor_new_current_states[:,i,:]) for i in range(self.n_agents)]
            non_final_next_actions = torch.stack(non_final_next_actions)

            target_Q = torch.zeros(self.MINIBATCH_SIZE).type(FloatTensor)

            target_Q = self.critics_target[agent](
                tensor_new_current_states.view(-1, self.n_agents * self.n_states),
                non_final_next_actions.view(-1,self.n_agents * self.n_actions)
            ).squeeze()
            # scale_reward: to scale reward in Q functions

            target_Q = (target_Q.unsqueeze(0) * (1 - tensor_dones) * self.GAMMA) + (tensor_rewards[:, agent].unsqueeze(1))

            loss_Q = nn.MSELoss()(current_Q, target_Q.detach())
            loss_Q.backward()

            self.critic_optimizer[agent].step()

            self.actor_optimizer[agent].zero_grad()
            state_i = tensor_current_states[:, agent, :]
            action_i = self.actors[agent](state_i)
            ac = tensor_actions.clone()
            ac[:, agent, :] = action_i
            whole_action = ac.view(self.MINIBATCH_SIZE, -1)
            actor_loss = -self.critics[agent](whole_state, whole_action)
            actor_loss = actor_loss.mean()
            actor_loss.backward()

            self.actor_optimizer[agent].step()
            c_loss.append(loss_Q)
            a_loss.append(actor_loss)

            self.train_step += 1

    def get_actions(self, state_batch):
        # state_batch: n_agents x state_dim
        actions = torch.zeros(
            self.n_agents,
            self.n_actions)

        state_batch = torch.Tensor(state_batch)
        FloatTensor = torch.FloatTensor
        for i in range(self.n_agents):
            sb = state_batch[i, :].detach()

            act = self.actors[i](sb.unsqueeze(0))
            # print('Actor{}的原始输出为:{}'.format(i, act))

            act += torch.from_numpy(
                (np.random.rand(1) - 0.5) * self.var[i]).type(FloatTensor)

            if self.var[i] > 0.05:
                self.var[i] *= 0.9998

            act = torch.tanh(act)

            actions[i, :] = act
            # print('Actor{}的最终输出为:{}'.format(i, act))

        return actions

    def train_in_loop(self):
        self.training_initialized = True

        while True:
            if self.terminate:
                return
            
            self.train()
            time.sleep(0.01)


print(Actor(4, 1))
print(Critic(4, 1, 2))
