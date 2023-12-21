import json
from ortools.linear_solver import pywraplp

def maxband():
    # set parameters
    # outbound为东向西
    params = json.load(open('param.json', encoding='utf-8'))
    N = params["N"]    # 交叉口数
    CMax = params["Cmax"]    # 周期时长限制
    CMin = params["Cmin"]
    L = params["outbound_Li"]    # 交叉口间距离
    LBar = params["inbound_Li_bar"]
    R = params["outbound_ri"]    # 协调方向的红灯时间率
    RBar = params["inbound_ri_bar"]
    Delta = params["inbound_outband_Deltai"]    # 上下行绿灯启亮时间的差值
    V = params["outbound_vi"]    # 交叉口间行驶速度
    VBar = params["inbound_vi_bar"]
    K = params["K"]    # 下行方向权重
    solver = pywraplp.Solver('SolverIntegerProblem', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    upperboud = solver.infinity()

    # set decision variables
    o = [solver.NumVar(0.0, 1.0, 'o{:02d}'.format(i)) for i in range(N)]    # 绝对相位差
    w = [solver.NumVar(0.0, upperboud, 'w{:02d}'.format(i)) for i in range(N)]    # 绿波带中心线和绿灯启亮时间的差值
    w_bar = [solver.NumVar(0.0, upperboud, 'w_bar{:02d}'.format(i)) for i in range(N)]
    t = [solver.NumVar(0.0, upperboud, 't{:02d}'.format(i)) for i in range(N - 1)]
    t_bar = [solver.NumVar(-10, 10, 't_bar{:02d}'.format(i)) for i in range(N - 1)]
    delta = [solver.IntVar(-10, 10, 'delta{:02d}'.format(i)) for i in range(N - 1)]    # 上下行绿灯启亮时间的差值
    delta_bar = [solver.IntVar(0.0, upperboud, 'delta_bar{:02d}'.format(i)) for i in range(N - 1)]
    b = solver.NumVar(0, upperboud, 'b')    # 绿波带带宽
    b_bar = solver.NumVar(0, upperboud, 'b_bar')
    z = solver.NumVar(1 / float(CMax), 1 / float(CMin), 'z')    # 周期时长的倒数

    # set constraints
    solver.Add((1 - K) * b_bar >= (1 - K) * K * b)
    for i in range(N):
        solver.Add(b / 2.0 <= w[i])
        solver.Add(w[i] <= (1 - R[i] - b / 2.0))
        solver.Add(b_bar / 2.0 <= w_bar[i])
        solver.Add(w_bar[i] <= (1 - RBar[i] - b_bar / 2.0))
    for i in range(N - 1):
        solver.Add(o[i] + w[i] + t[i] == o[i + 1] + w[i + 1] + delta[i])
        solver.Add(o[i] + Delta[i] + w_bar[i] + delta_bar[i] == o[i + 1] + Delta[i + 1] + w_bar[i + 1] + t_bar[i])
    for i in range(N - 1):
        solver.Add(t[i] == L[i] / V[i] * z)
        solver.Add(t_bar[i] == LBar[i] / VBar[i] * z)
    solver.Add(o[0] == 0)

    # set objective function
    obj_fn = [b, K * b_bar]
    solver.Maximize(solver.Sum(obj_fn))
    result_status = solver.Solve()

    # obtain the result
    assert result_status == pywraplp.Solver.OPTIMAL
    print('西向东方向绿波带带宽：{}个周期'.format(b.SolutionValue()))
    o_lst = [i.SolutionValue() for i in o]    # 协调相位差
    C = 1 / z.SolutionValue()    # 协调周期时长
    return C, o_lst



def cal_groups(origin_groups, C, o_lst):
    params = json.load(open('param.json', encoding='utf-8'))
    N = params["N"]
    cor_groups = params['groupIdLst']
    R = params['outbound_ri']
    cor_phases = params["inbound_phase"]
    new_groups = {}    # 干道绿波新信控方案
    for i in range(N):   # 遍历协调交叉口
        group_id = cor_groups[i]
        group = origin_groups[group_id]
        origin_period_time = group['period_time']    # 原周期时间
        new_period_time = int(C)    # 新周期时间
        new_phase_dict = {}
        sum_green_time = 0    # 用于校核周期时长、
        for phase_id, phase in group['phases'].items():
            if phase_id in cor_phases:
                start_time = int(new_period_time * o_lst[i])
                new_green_interval = int(new_period_time * (1 - R[i]) - phase['yellow_interval'])
            else:
                last_phase = max(new_phase_dict.items(), key=lambda x: x[0])[1]     # 取上一个相位，当前相位绿灯将在上一个相位黄灯时间后启亮
                start_time = last_phase['start_time'] + last_phase['green_interval'] + last_phase['yellow_interval']
                if start_time > new_period_time:    # 校核绿灯启亮时间在一个周期内
                    start_time = start_time - new_period_time
                new_green_interval = int(new_period_time * R[i] * ((phase['green_interval'] + phase['yellow_interval']) / (origin_period_time * R[i]))) - phase['yellow_interval']   # 按比例分配非协调相位绿灯时间
            yellow_interval = phase['yellow_interval']
            all_red_interval = phase['all_red_interval']
            sum_green_time += new_green_interval + yellow_interval
            new_phase_dict[phase_id] = {'phase_id': phase_id, 'start_time': start_time,
                                        'green_interval': new_green_interval, 'yellow_interval': yellow_interval,
                                        'all_red_interval': all_red_interval}
        if sum_green_time != new_period_time:    # 如果相位总绿灯时间不等于周期时间，需校核
            last_one_phase = max(new_phase_dict.items(), key=lambda x: x[0])    # 取最后一个相位
            phase_id = last_one_phase[0]
            phase = last_one_phase[1]
            phase.update({'green_interval': phase['green_interval'] + (new_period_time - sum_green_time)})
            new_phase_dict.update({phase_id: phase})
        new_groups[group_id] = {'period_time': new_period_time, 'phases': new_phase_dict}
    return new_groups



