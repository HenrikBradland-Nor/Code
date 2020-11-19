import gym
import myCode.snake_envs

env_dict = gym.envs.registration.registry.env_specs.copy()


for env in env_dict:
    if 'Snake-v1' in env:
        print("Remove {} from registry".format(env))
        del gym.envs.registration.registry.env_specs[env]


env = gym.make('snake_envs:Snake-v1')


