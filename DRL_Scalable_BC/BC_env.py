import gym
import math
from gym import spaces, logger
from gym.utils import seeding
import random
import numpy as np
from action_space import ActionSpace
from ShardDistribution import ShardDistribute


class BCnetenv(gym.Env):
    '''
Actions:
    Type: MultiDiscrete form.
    1) Block_Size(shard)   :   Discrete 4  - 2MB[0], 4MB[1], 6MB[2], 8MB[3],   - params: min: 2, max: 8  (megabytes)
    2) Time Interval       :   Discrete 4  - 2[0]  ,   4[1],   6[2],   8[3]    - params: min: 2, max: 8  (seconds)
    3) number of shard (K) :   Discrete 4  - 1[0],     2[1],   4[2],   8[3]    - params: min: 1, max: 8
    MultiDiscrete([ 4, 4, 4 ])  -> we use discrete expression (64)
    0, 0 ,0 ->0
    0, 0, 1 ->1
    0, 0, 2 ->2
    ...
    3, 3, 3 -> 63

state space:
    Type:
    Num       state                    Min       Max     format
    0    data transmission link      10MHZ    100MHZ      nxn
    1     computing capability       10GHZ     30GHZ      nx1
    2      consensus history           0         1        nxn
    3 estimated faulty probability     0        1/3       nx1

:
    Type: Box(2)
    num     observation        min       max
    0        latency           0         48
    1   required shard limit   1          8

    '''

    def __init__(self):
        # Simulation parameters
        self.nb_nodes = 200
        self.tx_size = 200 #bytes
        self.B_max = 8 #Megabytes
        self.Ti_amx = 8 #seconds
        self.K_max = 8 # maximum shard number
        self.sign = 2 # MHZ
        self.MAC = 1 # MHZ
        self.batchsize =  3
        self.u = 6  # consecutive block confirm
        self.trans_prob = 0.1 # Transition Probability in Finitie Markov Chain
                                                   
        # define action space & observation_space
        self.action_space = ActionSpace(64)
        self.observation_space = spaces.Box(low=np.array([0, 1]), high=np.array([48, 8]), dtype=np.float32)

        self.seed()
        self.viewer = None
        self.state = None
        self.steps_beyond_done = None

        # state 불러오기. ShardDist함수의 return값을 각각 R,c,H,e_prob로 할당하도록함.
        # 여기서 state는 main의 진짜 state에 필요한 구성요소들을 각각 업데이트하는것임.
        self.R_transmission = None
        self.c_computing = None
        self.H_history = None
        self.e_prob = None




    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]






    def step(self, action):
        # step 함수 진행하면서 state space 를 update

        assert self.action_space.contains(action), "%r (%s) invalid"%(action, type(action))
        state = self.state
        R, C, H, e_prob = state
        
        # state라는 지역변수에 self.state 입력. (추후 self.state = 를 다시 입력해 state를 업뎃해야함
        # state는 R,C,H,e_prob 로 구성
        # action 진행시 현재 state를 받아오고, 해당 action을 import한 뒤 다음 state를 출력할 수 있어야함.


## 선택된 action에 대한 local variable 반환
        a=action//16        # action을 16으로 나눈 몫
        b=(action%16)//4    # action을 16으로 나눈 나머지를 다시 4로나눈 몫
        c=action%4          # action을 4로 나눈 나머지

        b_size = 2*(a+1)    # block size 2,4,6,8
        t_interval = 2*(b+1)  # time interval 2,4,6,8
        n_shard = 2**c         # number of shard 1,2,4,8


        # R 업데이트 finite markov channel 기반.
        for i in range (0,self.nb_nodes):
            for j in range (i+1,self.nb_nodes):
                random_number = random.random()
                if (R[i,j] == 10*(10**6)):
                    if (random_number < self.trans_prob):
                        R[i,j] += 10*(10**6)
                        R[j,i] = R[i,j]
                elif (R[i,j] == 100*(10**6)):
                    if (random_number < self.trans_prob):
                        R[i,j] -= 10*(10**6)
                        R[j,i] = R[i,j]        
                else :
                    if (random_number < self.trans_prob):
                        R[i,j] += 10*(10**6)
                        R[j,i] = R[i,j]
                    elif (self.trans_prob <= random_number < 2*self.trans_prob):
                        R[i,j] -= 10*(10**6)
                        R[j,i] = R[i,j]                
        
        # C 업데이트 finite markov channel 기반.
        for i in range (0,self.nb_nodes):
            random_number = random.random()
            if (C[i] == 10*(10**9)):
                if (random_number < self.trans_prob):
                    C[i] += 5*(10**9)
            elif (C[i] == 30*(10**9)):
                if (random_number < self.trans_prob):
                    C[i] -= 5*(10**9)        
            else :
                if (random_number < self.trans_prob):
                    C[i] += 5*(10**9)
                elif (self.trans_prob <= random_number < 2*self.trans_prob):
                    C[i] -= 5*(10**9)
                    
        # H, e_prob 계산. (ShardDist)
        env2 = ShardDistribute()
        H,e_prob,NodesInShard = env2.ShardDist(n_shard)


        self.state = [R, C, H, e_prob]  ## 여기서 e_prob를 받았는데 nx1형식임.
        # 뒤에 constraint에 넣기위해 float32로 바꿔줌
        e_p = e_prob[0,0]  # constraint에 쓸 변수를 여기서 미리 불러옴

### latency computation
        # latency 계산시 R,c로부터 max/min값을 추출하여 latency 세부요소들 전부 계산
        # M,theta,C_numb,alpha,B,timeout 값 설
        M = 3
        theta = 2*(10**6)
        C_numb = len(NodesInShard[n_shard])
        alpha = 10**6
        B = b_size
        timeout = 1000000000000000000000000 # 거의 무한으로 해놓음 (무의미)

        # 1) Intra 샤드에서 validation time 계산
        T_k_in_val = []
        primary = []
        for K in range(n_shard):
            primary.append(NodesInShard[K][random.randint(0,len(NodesInShard[K])-1)])
            
            T_in_val = []
            for i in NodesInShard[K]:
                if (i == primary[K]):
                    T_in_val.append((M*theta + (M*(1+C_numb) + 4*(len(NodesInShard[K])-1))*alpha) / C[i][0])
                else :
                    T_in_val.append((M*theta + (C_numb*M + 4*(len(NodesInShard[K])-1))*alpha) / C[i][0])
            T_k_in_val.append(max(T_in_val))
        T_k_in_val = (1/M)*max(T_k_in_val)
        # 2) Intra 샤드에서 propagation time 계산
        T_k_in_prop = []
        for K in range(n_shard):
            
            T_in_preprepare = []
            T_in_prepare = []
            T_in_commit = []
            
            for i in NodesInShard[K]:
                for j in NodesInShard[K]:
                    if (j != i):
                        if (i == primary[K]):
                            T_in_preprepare.append((M*B)/R[i,j])
                        else :
                            T_in_prepare.append((M*B)/R[i,j])
                        T_in_commit.append((M*B)/R[i,j])
                                           
            T_k_in_prop.append( min(max(T_in_preprepare),timeout) + min(max(T_in_prepare),timeout) + min(max(T_in_commit),timeout) )
        T_k_in_prop = (1/M)*max(T_k_in_prop)        

        # 3) DC (Final shard)에서 validation time 계산                
        primary_DC = NodesInShard[n_shard][random.randint(0,len(NodesInShard[n_shard])-1)] 
           
        T_k_f_val = []
        for i in NodesInShard[n_shard]:
            if (i == primary_DC):
                T_k_f_val.append((n_shard*M*theta + (n_shard*M + 4*(C_numb-1) + (self.nb_nodes-C_numb)*M)*alpha) / C[i][0])
            else :
                T_k_f_val.append((n_shard*M*theta + (4*(C_numb-1) + (self.nb_nodes-C_numb)*M)*alpha) / C[i][0])
        T_k_f_val = (1/M)*max(T_k_f_val)        
                
        # 4) DC (Final shard)에서 propagation time 계산   
        T_k_f_request = []
        T_k_f_preprepare = []
        T_k_f_prepare = []
        T_k_f_commit = []
        T_k_f_reply = []
        
        for i in primary:
            for j in NodesInShard[n_shard]:
                T_k_f_request.append((M*B)/R[i,j])
        
        for i in NodesInShard[n_shard]:
            for j in NodesInShard[n_shard]:
                if (j != i):
                    if (i == primary_DC):
                        T_k_f_preprepare.append((M*B)/R[i,j])
                    else:
                        T_k_f_prepare.append((M*B)/R[i,j])
                    T_k_f_commit.append((M*B)/R[i,j])
        
        for i in NodesInShard[n_shard]:
            for j in primary:
                T_k_f_reply.append((M*B)/R[i,j])
        
        T_k_f_prop = (1/M)*(min(max(T_k_f_request),timeout) + min(max(T_k_f_preprepare),timeout) 
                              + min(max(T_k_f_prepare),timeout) + min(max(T_k_f_commit),timeout) + min(max(T_k_f_request),timeout))
        # 최종 latency의 값은 block interval + 위 4가지 time
        Tlatency = t_interval + (T_k_in_val + T_k_in_prop + T_k_f_val + T_k_f_prop)


### constraint (latency & shard)
        done = Tlatency > self.u * t_interval \
               or n_shard >= (self.nb_nodes*(1-(3*e_p))-1)/(3*self.nb_nodes*e_p + 1)
        done = bool(done)

        #done 이 1인경우, 즉 끝났다면(조건을 위반하여) reward는 0
        #done이 0인 경우, reward는 TPS를 반영한다.

        if not done:
            reward = (n_shard * (math.floor((b_size/self.tx_size)*1024*1024)))/t_interval
        elif self.steps_beyond_done is None:   ## step beyond done?
            self.steps_beyond_done = 0
            reward = 1.0
        else:
            if self.steps_beyond_done == 0:
                logger.warn("You are calling 'step()' even though this environment has already returned done = True. "
                            "You should always call 'reset()' once you receive 'done = True' -- any further steps are undefined behavior.")
            self.steps_beyond_done += 1
            reward = 0.0
##### state change 적용해서 R,C,H,e_prop 업데이트.
### 리턴되어야 하는 값은, action이 들어왔을때, 변경된 R,C,H,e-Prob

        return self.state, reward, done, {}   ## 카트폴에서는 self.state에 np.array가 있는데, 여기서는 풀어줘야함
    # 왜냐하면, R,C,H,e_prob는 모두 차원이 달라 np.array를 쓰면 차원오류가 뜸.
    # 144번라인에서 self.state = [R, C, H, e_prob] 에 의해, 각 원소들이 state로 들어감.
    # state[0], state[1], state[2], state[3]을 통해 각각 R,C,H,e_prob를 반환할 수 있다.



    def reset(self):
        # state space - > R,c,H reset.
        R_transmission = np.zeros((self.nb_nodes,self.nb_nodes))
        c_computing = np.zeros((self.nb_nodes,1))
        
        for i in range (0,self.nb_nodes):
            for j in range (i+1,self.nb_nodes):
                R_transmission[i,j] = random.randrange(10,101,10)
                R_transmission[j,i] = R_transmission[i,j]
        R_transmission = (10**6)*R_transmission

        for i in range (0,self.nb_nodes):
            c_computing[i] = random.randrange(10,31,5)
        c_computing = (10**9)*c_computing
 
        
        n_shard = 2**(random.randrange(1,5)-1)

        env2 = ShardDistribute()
        H,e_prob,NodesInShard = env2.ShardDist(n_shard)
        
        self.state = [R_transmission, c_computing, H, e_prob]
        
        return self.state
        
        
        
