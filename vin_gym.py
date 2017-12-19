"""Contains classes defining the environment for Vindinium."""
import json

import numpy as np

import gym
from gym import spaces
from gym.utils import seeding

import vindinium as vin
import vindinium.models.game

from vindinium.ai.minimax import simulation
from vindinium.ai.minimax.state import State


ACTION_MAP = {
    0: vin.NORTH,
    1: vin.SOUTH,
    2: vin.WEST,
    3: vin.EAST,
    4: vin.STAY,
}


class VindiniumEnv(gym.Env):
    """The Vindinium environment class that is used by keras-rl agents."""

    def __init__(self):
        """Create environment instance."""
        self.np_random = None
        self.game = None
        self.state = None
        self.hero = {'id': 1, 'gold': 0, 'life': 100, 'mine_count': 0}
        self.reward_range = (-np.inf, np.inf)
        self.action_space = spaces.Discrete(len(ACTION_MAP))
        # TODO: implement padding and unify shape of observation space
        self.observation_space = spaces.Box(low=-4, high=4, shape=(12, 12))
        self._seed()

    def __del__(self):
        """Close this environment."""
        self.close()

    def __str__(self):
        """Return string representing this environment."""
        return '<{} instance>'.format(type(self).__name__)

    def _step(self, action):
        """Run one timestep of the environment's dynamics.

        Accepts an action and returns a tuple (observation, reward, done, info)

        # Arguments
            action (object): An action provided by the environment.

        # Returns
            observation (object): Agent's observation of the current
                                  environment.
            reward (float) : Amount of reward returned after previous action.
            done (boolean): Whether the episode has ended, in which case
                            further step() calls will return undefined results.
            info (dict): Contains auxiliary diagnostic information (helpful
                         for debugging, and sometimes learning).
        """
        # manipulate game state by executing action
        assert self.state
        # TODO assert that action is in action_space
        move = ACTION_MAP[action]
        print('============= turn %d / %d ============='
              % (self.state.turn + 1, self.game.max_turns))
        print('my hero\'s move: %s.' % move)
        simulation.simulate(self.state, move)  # simulation manipulates state

        # simulate the opponents' moves
        for h in self.game.heroes:
            if not h.id == self.hero['id']:
                _move = ACTION_MAP[self.np_random.choice([0, 1, 2, 3, 4])]
                print('hero %d\'s move: %s.' % (h.id, _move))
                simulation.simulate(self.state, _move)

        # update game state
        self._update()

        # encode game state in observation object
        observation = self._encode()
        print(self.game)
        print(observation)

        # done, if last round finished
        done = self.game.turn >= self.game.max_turns

        # compute reward
        reward = 0.0 if done else self._compute_reward()
        print('Reward for this turn\'s action: %.1f.' % reward)

        return observation, reward, done, {}

    def _reset(self):
        """Reset the state of the environment and returns an initial observation.

        # Returns
            observation (object): The initial observation of the space.
                                  Initial reward is assumed to be 0.
        """
        # load initial state
        json_data = open('simple_game.json').read()
        state = json.loads(json_data)

        # define observation space
        # size = state['game']['board']['size']
        # self.observation_space = spaces.Box(low=-4, high=4, shape=(size, size))

        # create new game instance
        self.game = vindinium.models.game.Game(state)
        self.state = State(self.game)
        observation = self._encode()

        print('============= initial board =============')
        print(self.game)
        print(observation)
        return observation

    def _render(self, mode='human', close=False):
        """Render the environment.

        Note: This environment does not support rendering.

        # Arguments
            mode (str): The mode to render with.
            close (bool): Close all open renderings.
        """
        pass

    def _close(self):
        """Perform any necessary cleanup.

        Environments will automatically close() themselves when
        garbage collected or when the program exits.
        """
        pass  # close connection?

    def _seed(self, seed=None):
        """Set the seed for this env's random number generator(s).

        # Returns
            Returns the list of seeds used in this env.
        """
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _configure(self, *args, **kwargs):
        """Provide runtime configuration to the environment."""
        pass

    def _encode(self):
        """Encode current game state as observation.

        # Returns
            Returns a numpy array representing the current game state.
        """
        # encode game board
        observation = self.game.map.observe()

        # TODO: use information from self.state

        # add (negative) hero ids
        for hero in self.game.heroes:
            # NOTE: on map, x is horizontal and y vertical direction
            observation[hero.y, hero.x] = -hero.id

        return observation

    def _update(self):
        """Update game state."""
        # update heroes
        for h, hero in zip(self.state.heroes, self.game.heroes):
            assert h['id'] == hero.id
            hero.x = h['x']
            hero.y = h['y']
            hero.gold = h['gold']
            hero.mine_count = h['mine_count']
            hero.life = h['life']

        # update mines
        for mine in self.game.mines:
            mine.owner = self.state.mines[(mine.x, mine.y)]

        # update turn
        self.game.turn = self.state.turn

    def _compute_reward(self):
        """Compute reward for this turn's action."""
        my_hero = self.game.heroes[0]
        assert my_hero.id == self.hero['id']

        # gold gained (or lost, if negative) in this turn
        gained_gold = my_hero.gold - self.hero['gold']
        self.hero['gold'] = my_hero.gold  # update for next turn

        # life gained (or lost, if negative) in this turn
        gained_life = my_hero.life - self.hero['life']
        self.hero['life'] = my_hero.life  # update for next turn

        # mines conquered (or lost)
        gained_mines = my_hero.mine_count - self.hero['mine_count']
        self.hero['mine_count'] = my_hero.mine_count

        # reward
        reward = gained_gold + gained_life / 10 + gained_mines * 4
        return reward
