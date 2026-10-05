#willard.py

import random

#movement defined by WASD
DIRS = {
    'W': (-1, 0),
    'D': (0, 1),
    'S': (1, 0),
    'A': (0, -1),
}

ORDER_MOVES = ['W', 'D', 'S', 'A']

#grenade actions
GREN = {
    'GW': 'W',
    'GD': 'D',
    'GS': 'S',
    'GA': 'A',
}

#exit actions
EXIT_ACTION = 'X'


def in_bounds(pos: tuple[int, int], size: int) -> bool:

    """
    This function checks if pos is inside the board.
    Args:
        pos (tuple[int,int]): coord_i, coord_j of the current.
        size (int): board size.
    Returns:
        valid (bool): True if the current position studied is valid.
    """

    #initial values
    coord_i, coord_j = pos[0], pos[1]
    valid = True

    if coord_i < 0 or coord_i >= size:
        valid = False
    if coord_j < 0 or coord_j >= size:
        valid = False
    return valid


def neighbors(pos: tuple[int, int], size: int) -> list[tuple[int,int]]:

    """
    This function returns valid neighbors (up,right,down,left) of pos.
    Args:
        pos (tuple[int,int]): coord_i, coord_j of the current position whose neighburs are to be obtained.
        size (int): board size.
    Returns:
        ngb (list[tuple[int,int]]): list of neighbors of the current position.
    """

    ngbs = []
    
    for actual_move in ORDER_MOVES:
        dc_i, dc_j = DIRS[actual_move][0], DIRS[actual_move][1]
        pos_ngb = (pos[0] + dc_i, pos[1] + dc_j)

        if in_bounds(pos_ngb, size):
            ngbs.append(pos_ngb)

    return ngbs


def apply_move(pos: tuple[int,int], action: str, size: int) -> tuple[tuple[int,int], bool]:

    """
    This function applies a movement action.
    Args:
        pos (tuple[int,int]): initial position.
        action (str): the selected action (W/A/S/D).
        size (int): board size.
    Returns:
        newpos (tuple[int,int]): new position if valid.
        moved (bool): True if position is changed.
    """

    #initial values
    new_pos = pos
    moved = False

    if action in DIRS:
        dir_i, dir_j = DIRS[action]
        candidate_pos = (pos[0] + dir_i, pos[1] + dir_j)
        if in_bounds(candidate_pos, size):
            new_pos = candidate_pos

    if new_pos != pos:
        moved = True

    return new_pos, moved


def create_environment(size: int, seed=None) -> dict[str: bool|str]:

    """
    This function creates a random environmentironment.
    Args:
        size (int): the board size (6 as given in the instructions).
        seed (int|None): the random seed.
    Returns:
        environment (dict[str: bool|str]): all the information about the environmentironment.
    """

    rng = random.Random(seed)

    #all pos positions
    pos_positions = []
    for i in range(size):
        for j in range(size):
            if (i,j) != (0,0):
                pos_positions.append((i,j))

    #fall traps
    falling_pos, pos_positions = select_positions(3, pos_positions, rng)

    #enemy soldier
    soldier_pos, pos_positions = select_positions(1, pos_positions, rng)

    #colonel kurtz pos
    kurtz_pos, pos_positions = select_positions(1, pos_positions, rng)

    #exit pos
    exit_pos, pos_positions = select_positions(1, pos_positions, rng)

    environment = {
        'size': size,
        'falling_traps': falling_pos,
        'soldier_pos': soldier_pos,
        'soldier_alive': True,
        'kurtz_pos': kurtz_pos,
        'exit_pos': exit_pos,
    }

    return environment


def select_positions(number_pos: int, pos_positions: list[tuple[int, int]], rng: random.Random) -> tuple[list[tuple[int, int]], list[tuple[int,int]]]:

    """
    This function selects a given number of positions.
    Args:
        number_pos (int): the number of positions to be selected.
        pos_positions (list[tuple[int, int]]): the pos positions used to select.
        rng (): the randomness seed.
    Returns:
        selected_positions (list[tuple[int, int]]): the selected positions.
        pos_positions (list[tuple[int, int]]): the remaining pos positions to be selected.
    """
    
    selected_positions = []
    for i in range(number_pos):

        idx = rng.randrange(0, len(pos_positions))
        selected_pos = pos_positions[idx]

        selected_positions.append(selected_pos)
        pos_positions.remove(selected_pos)

    if number_pos == 1:
        return selected_positions[0], pos_positions
    return selected_positions, pos_positions
    


def get_percepts(environment: dict[str: bool|str], pos: tuple[int,int], scream: bool):

    """
    This function returns percepts in the required order.
    [Breeze, Snore, Glow, WallUp, WallDown, WallLeft, WallRight, Scream]
    Args:
        environment (dict[str: bool|str]): all the environmentironment info.
        pos (tuple[int,int]): the current agent position.
        scream (bool): True if the last action eliminated the enemy soldier.
    Returns:
        percepts (list[bool]): the list of bools that represents the 8 booleans.
    """

    #initial values
    size = environment['size']
    coord_i, coord_j = pos[0], pos[1]

    wall_up, wall_down, wall_left, wall_right = get_location_percepts(coord_i, coord_j, size)

    breeze = False
    snore = False
    glow = False

    #use neighbors to update current percepts
    neighs = neighbors(pos, size)
    for ngb in neighs:
        if ngb in environment['falling_traps']:
            breeze = True
        if environment['soldier_alive'] and ngb == environment['soldier_pos']:
            snore = True
        if ngb == environment['exit_pos']:
            glow = True

    if pos == environment['exit_pos']:
        glow = True

    return [breeze, snore, glow, wall_up, wall_down, wall_left, wall_right, scream]


def get_location_percepts(coord_i: int, coord_j: int, size: int) -> tuple[bool, bool, bool, bool]:

    """
    This function gets the location percepts based on the coordinates of the current position and the size of the matrix.
    Args:
        coord_I (int): the horizontal coordinate of the current position.
        coord_j (int): the vertical coordinate of the current position.
    Returns:
        wall_up, wall_down, wall_left, wall_right (bool): the obtained location percepts.
    """

    wall_up = (coord_i == 0)
    wall_down = (coord_i == size - 1)
    wall_left = (coord_j == 0)
    wall_right = (coord_j == size - 1)

    return wall_up, wall_down, wall_left, wall_right


class Willard:

    def __init__(self, size: int):

        """
        Args:
            self
            size (int): the board size.
        """
        self.size = size

        #state
        self.pos = (0, 0)
        self.grenade = True
        self.kurtz_found = False

        #kb
        self.visited = set()
        self.no_fall = set()
        self.no_soldier = set()
        self.falling_traps_deduced = set()
        self.soldier_deduced = None
        self.soldier_dead = False

        #logic
        self.breeze_susp = {}  
        self.snore_susp = {}   

        self.exit_candidates = set()
        for i in range(self.size):
            for j in range(self.size):
                if (i,j) != (0,0):
                    self.exit_candidates.add((i,j))

        self.exit_known = None

        #start (safe)
        self.no_fall.add((0, 0))
        self.no_soldier.add((0, 0))


def kb_is_safe(w: Willard, cell: tuple[int, int]) -> bool:

    """
    This function checks if KB entails a cell is safe.
    Args:
        w (Willard): the agent.
        cell (tuple[int,int]): the studied cell.
    Returns:
        safe (bool): True if certainly no danger (no fall and no soldier).
    """

    safe = False
    if cell in w.no_fall:
        if w.soldier_dead:
            safe = True
        else:
            if cell in w.no_soldier:
                safe = True
    return safe


def kb_mark_all_no_soldier(w: Willard, except_cell=None) -> None:

    """
    This function marks all positions as no_soldier except one optional cell.
    Args:
        w (Willard): agent
        except_cell (tuple[int,int]|None): cell not marked
    Returns:
        None
    """

    for i in range(w.size):
        for j in range(w.size):
            pos = (i,j)
            if except_cell is None:
                w.no_soldier.add(pos)
            else:
                if pos != except_cell:
                    w.no_soldier.add(pos)


def kb_propagate(w: Willard):
    
    """
    This function propagates susp to deduce falling_traps/soldier.
    Args:
        w (Willard): the agent.
    Returns:
        None
    """
    
    changed = True
    while changed:  #if a change has been made
        changed = False

	#falling_traps
    observation_list = list(w.breeze_susp.keys())
    for observation in observation_list:
        
        #filter candidates
        candidate = w.breeze_susp[observation] - w.no_fall

        #looks for neighbors already deducted
        satisfied = False
        for nb in neighbors(observation, w.size):
            if nb in w.falling_traps_deduced:
                satisfied = True

        #if a neighbour is a certainly a falling trap -> delete from suspicious
        if satisfied:
            if observation in w.breeze_susp:
                del w.breeze_susp[observation]
            changed = True

        #no -> study the candidate
        else:
            w.breeze_susp[observation] = candidate

            #last possible candidate -> surely the falling trap
            if len(candidate) == 1:
                p = next(iter(candidate))
                if p not in w.falling_traps_deduced:
                    w.falling_traps_deduced.add(p)
                    changed = True
                if observation in w.breeze_susp:
                    del w.breeze_susp[observation]
                    changed = True

        #enemy soldier
        if (not w.soldier_dead) and (w.soldier_deduced is None):  #if soldier is still alive and not found
            observation_list = list(w.snore_susp.keys())
            
            for observation in observation_list:
                candidate = w.snore_susp[observation] - w.no_soldier 
                w.snore_susp[observation] = candidate
                
                #last possible candidate -> surely the enemy soldier
                if len(candidate) == 1:
                    w.soldier_deduced = list(candidate)[0]
                    changed = True

            if w.soldier_deduced is not None:
                kb_mark_all_no_soldier(w, except_cell=w.soldier_deduced)
                w.snore_susp = {}
                changed = True


def kb_update_exit(w: Willard, glow: bool) -> None:

    """
    Update exit candidate set using glow percept.
    If glow is True: exit must be in {pos} U neighbors(pos).
    If glow is False: exit cannot be in {pos} U neighbors(pos).
    Args:
        w (Willard): the agent.
        glow (bool): signal of exit
    Returns:
        None
    """

    #initial values
    neighs = neighbors(w.pos, w.size)
    local = set()
    local.add(w.pos)
    for nb in neighs:
        local.add(nb)

    #possible exit
    if glow:
        newset = set()
        for p in w.exit_candidates:
            if p in local:
                newset.add(p)
        w.exit_candidates = newset  #update pos exit positions
    else:
        for p in local:
            if p in w.exit_candidates:
                w.exit_candidates.remove(p)

    #last candidate -> certainly the exit
    if len(w.exit_candidates) == 1:
        w.exit_known = list(w.exit_candidates)[0]


def kb_update(w: Willard, percepts: list[bool]) -> None:

    """
    This function updates KB with percepts at current position.
    Args:
        w (Willard): agent
        percepts (list[bool]): percept list
    Returns:
        None
    """

    #update current values
    w.visited.add(w.pos)
    w.no_fall.add(w.pos)
    w.no_soldier.add(w.pos)

    #initial values
    breeze = percepts[0]
    snore = percepts[1]
    glow = percepts[2]
    scream = percepts[7]

    kb_update_exit(w, glow)

    if scream:
        w.soldier_dead = True
        w.soldier_deduced = None
        w.snore_susp = {}
        kb_mark_all_no_soldier(w, except_cell=None)

    #obtain ngbs -> positions to be studied if necessary
    neighs = neighbors(w.pos, w.size)

    #breeze -> falling_traps susp
    if not breeze:
        for nb in neighs:
            w.no_fall.add(nb)
        if w.pos in w.breeze_susp:
            del w.breeze_susp[w.pos]
    else:
        candidates = set(neighs) - w.no_fall
        w.breeze_susp[w.pos] = candidates

    #snore -> soldier susp
    if not w.soldier_dead:
        if not snore:
            for nb in neighs:
                w.no_soldier.add(nb)
            if w.pos in w.snore_susp:
                del w.snore_susp[w.pos]
        else:
            candidates = set(neighs) - w.no_soldier
            w.snore_susp[w.pos] = candidates

    #update with new knowledge
    kb_propagate(w)


def execute_action(environment: dict[str: bool|str], w: Willard, action: str) -> tuple[bool, bool, str, str]:

    """
    This function executes an action in the environmentironment and updates the state of Willard.
    Args:
        environment (dict): the environmentironment.
        w (Willard): the agent.
        action (str): the action to be executed (W/A/S/D/GW/GA/GS/GD/X).
    Returns:
        scream (bool): True if the soldier has been eliminated by grenade.
        done (bool): True if the game is finished.
        result (str): The result after executing the action ('RUNNING','WIN','DEAD_FALL','DEAD_SOLDIER').
        message (str): the message to be print after executing the action.
    """

    #initial values
    scream = False
    done = False
    result = 'RUNNING'
    message = ''
    size = environment['size']

    #action -> movement
    if action in DIRS:
        newpos, moved = apply_move(w.pos, action, size)
        w.pos = newpos

        if not moved:
            message = 'Move blocked by wall.'

        if w.pos == environment['kurtz_pos']:
            w.kurtz_found = True

        if w.pos in environment['falling_traps']:
            done = True
            result = 'DEAD_FALL'
            message = 'You fell into a falling trap.'

        if (not done) and environment['soldier_alive'] and (w.pos == environment['soldier_pos']):
            done = True
            result = 'DEAD_SOLDIER'
            message = 'You entered the soldier cell and died.'

    #action -> throw grenade
    if (not done) and (action in GREN):
        if w.grenade:
            w.grenade = False

            move_dir = GREN[action]
            target, moved = apply_move(w.pos, move_dir, size)

            if environment['soldier_alive'] and target == environment['soldier_pos']:
                environment['soldier_alive'] = False
                scream = True
                message = 'Scream! Soldier eliminated.'
            else:
                message = 'Grenade exploded, nothing happened.'
        else:
            message = 'No grenade available.'

    #action -> exit
    if (not done) and (action == EXIT_ACTION):
        #Important: if not on exit, world does not change (just a no-op)
        if w.pos == environment['exit_pos']:
            if w.kurtz_found:
                done = True
                result = 'WIN'
                message = 'You escaped with Colonel Kurtz.'
            else:
                message = 'You are on the exit, but you do not have Kurtz.'
        else:
            message = 'You are not on the exit.'

    return scream, done, result, message


def print_local_map(w: Willard, size: int):

    """
    This function prints the board showing deducted information of the current position, its neighbors, visited and deduced cells.
    Args:
        w (Willard): the agent.
        size (int): the size of the board.
    Returns:
        None.
    """

    #initial values and print
    print('\n', '-'*3, 'The board', '-'*3, '\n')
    ngbs = set(neighbors(w.pos, size))

    #paint board
    for i in range(size):
        row_str = ''
        for j in range(size):
            position = (i, j)
            
            #player
            if position == w.pos:
                row_str += 'W '
            
            #neighbors, visited or deduced positions
            elif (position in ngbs or 
                  position in w.visited or 
                  position == w.soldier_deduced or 
                  position in w.falling_traps_deduced):
                
                if position == w.soldier_deduced:
                    row_str += 'S '
                elif position in w.falling_traps_deduced:
                    row_str += 'P ' 
                elif kb_is_safe(w, position):
                    row_str += 'O '
                else:
                    row_str += '? ' 
            
            else:
                row_str += '. ' 
        
        print(row_str)


def print_manual_info(w: Willard, percepts: list[bool], step: int) -> None:

    """
    This function prints information for the user to play in manual mode.
    Args:
        w (Willard): the agent.
        percepts (list[bool]): the percepts as a boolean list.
        step (int): the number of iterations.
    Returns:
        None. It just prints the information.
    """

    print('\n', '-'*8, f'STEP {step+1}', '-'*8, '\n')
    
    #map and current position
    print('Current position: ', w.pos)
    print_local_map(w, w.size)
    

    #percepts
    print_manual_percepts(percepts)

    #current knowledge
    print('\n', '-'*3, 'Current information', '-'*3, '\n')
    print(f"  - Grenade: {'YES' if w.grenade else 'NO'}")
    print(f"  - Found Kurtz:   {'YES' if w.kurtz_found else 'NO'}")
    
    #exit info
    if w.exit_known:
         print(f'  - Confirmed exit in: {w.exit_known}')
    else:
         print(f'  - Possible exits: {len(w.exit_candidates)}')


def print_manual_percepts(percepts: list[bool]) -> None:

    """
    This function prints the percepts obtained. It is used when the user must select an action to execute.
    Args:
        percepts (list[bool]): the percepts to be printed.
    Returns:
        None. It just prints the percepts.
    """

    to_paint_text = []
    if percepts[0]: to_paint_text.append('BREEZE')
    if percepts[1]: to_paint_text.append('SNORE')
    if percepts[2]: to_paint_text.append('GLOW')
    if percepts[3]: to_paint_text.append('WALL UP')
    if percepts[4]: to_paint_text.append('WALL DOWN')
    if percepts[5]: to_paint_text.append('WALL LEFT')
    if percepts[6]: to_paint_text.append('WALL RIGHT')
    if percepts[7]: to_paint_text.append('SCREAM')
    
    if not to_paint_text:
        print('\n  - Percepts: None obtained')
    else:
        print(f"\n  - Percepts: {' | '.join(to_paint_text)}")


def manual_choose_action():

    """
    This function asks user for an action.
    Args:
        None
    Returns:
        action (str): valid action
    """
    
    print('\n', '-'*8, 'All possible action', '-'*8, '\n')
    print('  - Movement: W | A | S | D'
          '\n  - Grenade: GW | GA | GS | GD'
          '\n  - Exit: X\n')


    valid = False
    action = None
    while not valid:
        action = input('Select action: ').strip().upper()

        if action in DIRS:
            valid = True
        elif action in GREN:
            valid = True
        elif action == EXIT_ACTION:
            valid = True
        else:
            print('You must select a valid action.')

    return action


def run_game(environment: dict[str: bool|str], willard: Willard, max_steps=500):

    """
    This function runs the full game loop.
    Args:
        environment (dict[str: bool|str]): environmentironment
        willard (Willard): agent
        mode (str): 'MANUAL' or 'AUTO'
        max_steps (int): step cap
    Returns:
        None
    """

    #initial values
    steps = 0
    done = False
    last_scream = False

    while (not done) and (steps < max_steps):

        percepts = get_percepts(environment, willard.pos, last_scream)
        kb_update(willard, percepts)

        action = None

        print_manual_info(willard, percepts, steps)
        action = manual_choose_action()

        if action is None:
            done = True
            print('No safe actions can not be executed based on current knowledge. Stopping the game.')
        else:
            last_scream, done, result, message = execute_action(environment, willard, action)

            if done:
                print('Result: ', result)

        steps += 1

    if (not done) and (steps >= max_steps):
        print('Max steps have been reached. Stopping the game.')