import pandas as pd
import json
import os
import shutil
import sys
import ray
import ray.rllib.agents.sac as sac
import ray.rllib.agents.ppo as ppo
import ray.rllib.agents.ddpg as ddpg
import ray.rllib.agents.dqn as dqn
import gym
import myCode.snake_envs
import matplotlib.pyplot as plt

import tensorflow_probability as tfp

TRAINING_STEP = 2 # 1 = imitation, 2 = simulation
ALGORITHM = 1 # 1 = SAC,  2 = PPO, 3 = DDPG/TD3, 4 = DQN
RESTORE_AGENT = False
file_number = "11984"
N_ITER = 5
EPOCH = 2000
checkpoint_root = "tmp/sac/imitation4/snake"

if TRAINING_STEP == 1:
    SELECT_ENV = 'Snake-v1'
else:
    SELECT_ENV = 'SnakeSim-v1'

print("\n  ", SELECT_ENV, "  \n")

for env in gym.envs.registration.registry.env_specs.copy():
    if SELECT_ENV in env:
        print("Remove {} from registry".format(env))
        del gym.envs.registration.registry.env_specs[env]


#env = gym.make('snake_envs:Snake-v1')
#env = gym.make('snake_envs:SnakeSim-v1')

env = gym.make('snake_envs:'+SELECT_ENV)

ray.init(ignore_reinit_error=False)


if not RESTORE_AGENT:
    shutil.rmtree(checkpoint_root, ignore_errors=True, onerror=None)

    '''Sof Actor-Critic'''
if ALGORITHM == 1:
    config = sac.DEFAULT_CONFIG.copy()
    config["log_level"] = "WARN"
    config["train_batch_size"] = 5
    config["env"] = SELECT_ENV
    config["framework"] = "torch"
    config["use_state_preprocessor"] = True
    config["Q_model"]["fcnet_activation"] = "relu"
    config["Q_model"]["fcnet_hiddens"] = [256, 256]
    config["policy_model"]["fcnet_activation"] = "relu"
    config["policy_model"]["fcnet_hiddens"] = [256, 256]

    agent = sac.SACTrainer(config)

    '''Proximal Policy Optimization'''
elif ALGORITHM == 2:
    config = ppo.DEFAULT_CONFIG.copy()
    agent = ppo.PPOTrainer(config, env=SELECT_ENV)

    '''Deep Deterministic Policy Gradient'''
elif ALGORITHM == 3:
    config = ddpg.DEFAULT_CONFIG.copy()
    agent = ddpg.DDPGTrainer(config, env=SELECT_ENV)

    '''Deep Q-Network'''
elif ALGORITHM == 4:
    config = dqn.DEFAULT_CONFIG.copy()
    agent = dqn.DQNTrainer(config, env=SELECT_ENV)



if RESTORE_AGENT:
    agent.restore(checkpoint_root+"/checkpoint_"+file_number+"/checkpoint-"+file_number)

results = []
episode_data = []
episode_json = []

n = 0
r = []
t = []

def rewardConvargance():
    if n < 200:
        return False
    for i in range(100):
        if results[n-i]['episode_reward_mean'] > results[n - i - 100]['episode_reward_mean']:
            return False
    return True

while n < EPOCH: # not rewardConvargance():
    n += 1
    for g in range(N_ITER):
        result = agent.train()
        results.append(result)
        if g == 0:
            episode = {'n': n,
                       'episode_reward_min': result['episode_reward_min'],
                       'episode_reward_mean': result['episode_reward_mean'],
                       'episode_reward_max': result['episode_reward_max'],
                       'episode_len_mean': result['episode_len_mean']
                       }

            episode_data.append(episode)
            episode_json.append(json.dumps(episode))
            file_name = agent.save(checkpoint_root)

            print(f'{n + 1:3d}/{EPOCH}: Min/Mean/Max reward: {result["episode_reward_min"]:8.4f}/{result["episode_reward_mean"]:8.4f}/{result["episode_reward_max"]:8.4f}, len mean: {result["episode_len_mean"]:8.4f}. Checkpoint saved to {file_name}')
    t.append(n)
    r.append(result["episode_reward_mean"])
import pprint

policy = agent.get_policy()
model = policy.model



#pprint.pprint(model.variables())
#pprint.pprint(model.value_function())

#print(model.base_model.summary())




plt.plot()
plt.plot(t, r)
plt.show()