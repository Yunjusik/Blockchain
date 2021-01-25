
def select_action(state, e_p):
    global steps_done
    sample = random.random()
    eps_threshold = EPS_END + (EPS_START - EPS_END) * \
        math.exp(-1. * steps_done / EPS_DECAY)
    steps_done += 1
    if sample > eps_threshold:
        with torch.no_grad():
            # t.max(1) will return largest column value of each row.
            # second column on max result is index of where max element was
            # found, so we pick action with the larger expected reward.
            constraint = (200 * (1 - (3 * e_p)) - 1) / (3 * 200 * e_p + 1) ## const1 기준
            K_prime = math.floor(constraint)
            if K_prime == 0 :
                K_prime = 1
            if K_prime >= 8 :
                K_prime = 8
            duplicate_net = policy_net(state).detach().cpu().numpy()  ## state 입력시 policy_net의 output단을 복제함.
            ### CUDA에들어간 tensor를 조작하려면, 뉴럴넷에서 detach를 하여 추적을  중지시키고
            ###cpu 램에 할당하여 numpy로 다시 반환
            ### 이때 duplicate_net.shape은 1 x n_actions 인 array가 됨.
            #반복문 생성, duplicate_net의 아웃풋단에서, action중 K_prime을 넘는 샤드갯수를 가진 액션에 대해 모두 0값 처리.
            shard_set = [1, 2, 3, 4, 5, 6, 7, 8]
            for i in range(0, K_prime):
                del(shard_set[0])   ## K_Prime만큼 인덱스제거, 이 연산 후 shard_set은 action bound를 넘은 shard_set이됨.
            ## ex, K_prime이 3이면, shard_Set은 [4,5,6,7,8]만 남는다. 이때, 4,5,6,7,8 의 샤드를  갖는 모든 action을 duplicate_net에서 제거해줘야함
            for i in range(0, 512):
                a = i // 128  # block size (0~3)  2, 4, 6, 8
                b = (i - 128 * a) // 16  # # of shard (1~8)  1, 2 ,3 ,4 ,5 ,6, 7, 8
                n_shard=b+1
                if n_shard in shard_set: # 만약 선택된 action의 샤드갯수가, shard_set(bound 넘는) list에 있다면
                    duplicate_net[0][i] = 0  # 해당 값을 0으로 초기화

            best_action = torch.as_tensor(duplicate_net.argmax()).to(device).view(1,1)


            return best_action

    else:
            return torch.tensor([[random.randrange(n_actions)]], device=device, dtype=torch.long)
           ## 리턴값이  torch.tensor.
           ## select action을 통해 torch.tensor형으로 감싸진 action 이 나오는데, 이 값이 env.step으로 다시들어감.
