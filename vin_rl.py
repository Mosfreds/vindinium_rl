"""Simple reinforcement learning test."""
import numpy as np

import vin_gym

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory

# define environment
ENV_NAME = 'Vindinium-v0'  # unused, because not yet registered

# Get the environment and extract the number of actions available
env = vin_gym.VindiniumEnv()
np.random.seed(42)
env.seed(42)
num_actions = env.action_space.n

# test environment
# env._reset()
# env._step(action=0)
# env._step(action=2)
# env._step(action=2)

# build model
model = Sequential()
model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(num_actions))
model.add(Activation('linear'))
print(model.summary())

policy = EpsGreedyQPolicy()
memory = SequentialMemory(limit=50000, window_length=1)
dqn = DQNAgent(model=model,
               nb_actions=num_actions,
               memory=memory,
               nb_steps_warmup=10,
               target_model_update=1e-2,
               policy=policy)
dqn.compile(Adam(lr=1e-3), metrics=['mae'])

# Okay, now it's time to learn something! We visualize the training here for
# show, but this slows down training quite a lot.
dqn.fit(env, nb_steps=50, visualize=False, verbose=2)

# test model
dqn.test(env, nb_episodes=5, visualize=False)
