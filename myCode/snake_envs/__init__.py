from gym.envs.registration import register

register(
    id='SnakeSim-v1',
    entry_point='snake_envs.envs:SnakeEnv',
)
'''
register(
    id='Snake-v1',
    entry_point='snake_envs.envs:ImitationEnv',
)
'''