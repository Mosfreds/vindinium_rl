"""Simulates progress in a game state."""
import vindinium as vin


def kill(state, id, killer=None):
    """Recursively kills a hero."""
    hero = state.heroes[id]

    for i, h in enumerate(state.heroes):
        if h == hero:
            continue

        if h['x'] == hero['spawn_x'] and h['y'] == hero['spawn_y']:
            kill(state, i)

    hero['x'] = hero['spawn_x']
    hero['y'] = hero['spawn_y']
    hero['mine_count'] = 0
    hero['life'] = 100

    for pos in state.mines:
        value = state.mines[pos]
        if value == id + 1:
            if killer is None:
                state.mines[pos] = None
            else:
                state.mines[pos] = killer + 1
                state.heroes[killer]['mine_count'] += 1


def simulate(state, move):
    """Simulate a movement in vindinium given a minimax state.

    Arguments:
        state (State): a minimax state instance.
        move (string): the next movement.
    """
    id = state.turn % 4
    hero = state.heroes[id]

    # Compute next position
    # TODO: change to dictionary
    if move == vin.NORTH:
        dir_ = vin.DIR_NORTH
    elif move == vin.SOUTH:
        dir_ = vin.DIR_SOUTH
    elif move == vin.WEST:
        dir_ = vin.DIR_WEST
    elif move == vin.EAST:
        dir_ = vin.DIR_EAST
    elif move == vin.STAY:
        dir_ = vin.DIR_STAY

    x_, y_ = hero['x'] + dir_[0], hero['y'] + dir_[1]
    hero_ = None

    for h in state.heroes:
        if h['x'] == x_ and h['y'] == y_:
            hero_ = h
            break

    # Compute side effects of movement
    tile = state._game.map[x_, y_]
    print('DEBUG: ', tile)

    if (tile == 0 or tile == 2) and not hero_:
        # NOTE: if hero moves to another hero's spawn point, and other hero is
        # killed in his next turn, hero will be killed too (c.f. kill()).
        # EMPTY
        hero['x'] = x_
        hero['y'] = y_

    elif tile == 3:
        # TAVERN
        if hero['gold'] > 2:
            hero['gold'] -= 2
            hero['life'] = min(hero['life'] + 50, 100)

    elif tile == 4:
        # MINE
        mine = state.mines[x_, y_]

        # hero is not the mine's owner
        if mine != id + 1:

            # get mine
            if hero['life'] > 20:
                hero['life'] -= 20
                hero['mine_count'] += 1

                # remove mine from previous owner
                if mine is not None:
                    state.heroes[mine - 1]['mine_count'] -= 1

                state.mines[x_, y_] = id + 1

            # dies trying
            else:
                kill(state, id)

    # Fight
    for i, h in enumerate(state.heroes):
        if h == hero:
            continue

        # Attack if 1-tile distance
        if abs(hero['x'] - h['x']) + abs(hero['y'] - h['y']) == 1:

            if h['life'] > 20:
                h['life'] -= 20

            else:
                kill(state, i, id)

    # Mining
    hero['gold'] += hero['mine_count']

    # Thirst
    hero['life'] = max(hero['life'] - 1, 1)

    state.turn += 1
