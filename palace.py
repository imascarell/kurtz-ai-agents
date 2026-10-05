#palace.py

import os
import random
import shutil
import matplotlib.pyplot as plt

DIRS = {
    'W': (-1, 0),
    'D': (0, 1),
    'S': (1, 0),
    'A': (0, -1),
}

ORDER_MOVES = ['W', 'D', 'S', 'A']

GREN = {
    'GW': 'W',
    'GD': 'D',
    'GS': 'S',
    'GA': 'A',
}

EXIT_ACTION = 'X'

TRAP_TYPES = ['F', 'P', 'D']
BAYES_ELEMENTS = ['F', 'P', 'D', 'ES', 'ET']


def in_bounds(position: tuple[int, int], size: int) -> bool:

    """
    This function checks if a given position is inside the board.
    Args:
        position (tuple[int, int]): the position to be studied.
        size (int): the size of the board.
    """

    #initial values
    coord_i, coord_j = position[0], position[1]
    valid = True

    if coord_i not in range(0,size):
        valid = False
    if coord_j not in range(0,size):
        valid = False
    return valid


def neighbors(position: tuple[int, int], size: int) -> list[tuple[int, int]]:

    """
    This function returns valid neighbors (up,right,down,left) of a position to be studied.
    Args:
        position (tuple[int,int]): coord_i, coord_j of the current position whose neighburs are to be obtained.
        size (int): board size.
    Returns:
        ngb (list[tuple[int,int]]): list of neighbors of the current position.
    """

    #initial values
    ngbs = []
    coord_i, coord_j = position[0], position[1]

    for move in ORDER_MOVES:

        dir_i, dir_j = DIRS[move][0], DIRS[move][1]
        position_ngb = (coord_i + dir_i, coord_j + dir_j)

        if in_bounds(position_ngb, size):
            ngbs.append(position_ngb)

    return ngbs


def apply_move(pos: tuple[int, int], action: str, size: int) -> tuple[tuple[int, int], bool]:

    """
    This function applies a movement action to the position.
    Args:
        pos (tuple[int,int]): initial position.
        action (str): the selected action (W/A/S/D).
        size (int): board size.
    Returns:
        newpos (tuple[int,int]): new position if valid.
        moved (bool): True if position is changed.
    """

    #initial values
    coord_i, coord_j = pos[0], pos[1]
    new_pos = pos
    moved = False

    if action in DIRS:
        dir_i, dir_j = DIRS[action]
        candidate_pos = (coord_i + dir_i, coord_j + dir_j)
        if in_bounds(candidate_pos, size):
            new_pos = candidate_pos

    if new_pos != pos:
        moved = True

    return new_pos, moved


def action_between(point_a: tuple[int,int], point_b: tuple[int, int]):

    """
    This function returns the move action that goes from point a to point b (adjacent).
    It is used in the automatic mode.
    Args:
        point_a (tuple[int,int]): intial point of the movement.
        point_b (tuple[int,int]): final point of the movement.
    Returns:
        action (str|None): the obtained W/A/S/D or None.
    """

    #intial values
    pa_i, pa_j = point_a[0], point_a[1]
    pb_i, pb_j = point_b[0], point_b[1]

    if pb_i == pa_i - 1 and pb_j == pa_j:
        return 'W'
    if pb_i == pa_i + 1 and pb_j == pa_j:
        return 'S'
    if pb_i == pa_i and pb_j == pa_j + 1:
        return 'D'
    if pb_i == pa_i and pb_j == pa_j - 1:
        return 'A'

    return None


def grenade_from_move(move_action: str) -> str | None:

    """
    This function maps a move action to grenade action.
    It is used in the automatic mode when the grenade is to be launched.
    Args:
        move_action (str): W/A/S/D.
    Returns:
        grenade_action (str|None): GW/GA/GS/GD or None.
    """
        
    if move_action == 'W':
        return 'GW'
    if move_action == 'A':
        return 'GA'
    if move_action == 'S':
        return 'GS'
    if move_action == 'D':
        return 'GD'
    return None


def get_close_by_positions(position: tuple[int, int], size: int) -> set[tuple[int, int]]:

    """
    This function returns a set of the current position and its neighbors.
    Args:
        position (tuple[int, int]): the current positions whose neighbors are to be obtained.
        size (int): the size of the board.
    Returns:
        close_by_pos (set[tuple[int, int]]): the set that contains the current position and its neighbors.
    """

    close_by_pos = {position}
    for nb in neighbors(position, size):
        close_by_pos.add(nb)
    return close_by_pos


def create_environment(size: int, seed=None) -> dict[str: tuple[int,int]|bool|dict]:

    """
    This function creates a random environmentironment.
    Args:
        size (int): the board size (6 as given in the instructions).
        seed (int|None): the random seed.
    Returns:
        environment (dict[str: tuple[int,int]|bool|dict]): all the information about the environmentironment.
    """


    #initial values
    rng = random.Random(seed)
    start = (0, 0)
    
    #all possible pos
    all_positions = []
    for i in range(size):
        for j in range(size):
            if (i, j) != start:
                all_positions.append((i, j))

    #traps pos
    traps = {}
    for t in TRAP_TYPES:
        traps[t] = rng.choice(all_positions)
    trap_positions = set(traps.values())

    #safe pos
    safe_positions = list(set(all_positions) - trap_positions)

    if len(safe_positions) == 0:
        safe_positions = all_positions

    soldier_pos = rng.choice(safe_positions)
    exit_pos = rng.choice(safe_positions)
    kurtz_pos = rng.choice(safe_positions)

    return {
        'size': size,
        'start': start,
        'traps': traps,  
        'soldier_pos': soldier_pos,
        'soldier_alive': True,
        'exit_pos': exit_pos,
        'kurtz_pos': kurtz_pos,
    }


def position_not_safe(environment: dict[str: tuple[int,int]|bool|dict], pos: tuple[int, int]) -> bool:

    """
    This function recieves a position and studies if it is a trap position.
    Args:
        environment (dict[str: tuple[int,int]|bool|dict]): a dictionary that contains all the game and board information.
        pos (tuple[int, int]): the position to be studied.
    Returns:
        bool: True if safe, False if the studied position is a trap position.
    """

    traps = environment['traps']
    for t in TRAP_TYPES:
        if traps[t] == pos:
            return True
    return False


def get_location_percepts(pos: tuple[int, int], size: int) -> tuple[bool, bool, bool, bool]:

    """
    This function gets the location percepts based on the coordinates of the current position and the size of the matrix.
    Args:
        pos (tuple[int, int]): the current position to be studied.
    Returns:
        wall_up, wall_down, wall_left, wall_right (bool): the obtained location percepts.
    """

    #initial values
    coord_i, coord_j = pos[0], pos[1]

    wall_up = (coord_i == 0)
    wall_down = (coord_i == size - 1)
    wall_left = (coord_j == 0)
    wall_right = (coord_j == size - 1)

    return wall_up, wall_down, wall_left, wall_right


def get_percepts(environment: dict, pos: tuple[int, int], scream: bool) -> list[bool]:

    """
    This function returns percepts as a list of booleans as given in the instructions.
    Args:
        environment (dict[str: bool|str]): all the environmentironment info.
        pos (tuple[int,int]): the current agent position.
        scream (bool): True if the last action eliminated the enemy soldier.
    Returns:
        percepts (list[bool]): the list of bools that represents the 8 booleans.
    """

    #initial values
    size = environment['size']
    close_by_pos = get_close_by_positions(pos, size)

    #traps percepts
    traps = environment['traps']
    fire = (traps['F'] in close_by_pos)
    spikes = (traps['P'] in close_by_pos)
    darts = (traps['D'] in close_by_pos)

    enemy_soldier = False
    if environment['soldier_alive']:
        enemy_soldier = (environment['soldier_pos'] in close_by_pos)

    exit = (environment['exit_pos'] in close_by_pos)

    wall_up, wall_down, wall_left, wall_right = get_location_percepts(pos, size)

    return [fire, spikes, darts, enemy_soldier, exit, wall_up, wall_down, wall_left, wall_right, scream]


def create_uniform_prior(size: int, start_pos: tuple[int, int]) -> list[list[float]]:

    """
    Create a uniform prior excluding the start position.
    This function creates a uniform prior. It excludes the starting position.
    Args:
        size (int): the size of the board.
        start_pos (tuple[int, int]): the starting position.
    Returns:
        prob_matrix (list[list[float]]): the matrix that contains the prob associated to each pos.
    """
    
    total_pos = (size*size) - 1
    base_prob = 1.0 / float(total_pos)

    prob_matrix = []
    for i in range(size):
        row = []
        for j in range(size):
            if (i, j) == start_pos:
                row.append(0.0)
            else:
                row.append(base_prob)
        prob_matrix.append(row)

    return prob_matrix


def normalize_matrix(matrix: list[list[float]]) -> None:

    """
    This function normalises the matrix so its probs sums to 1.
    Args:
        matrix (list[list[float]]): the probs matrix to be normalised.
    Returns:
        matrix (list[list[float]]): the updated prob matrix.
    """

    #get current prob
    s = 0.0
    for row in matrix:
        for x in row:
            s += float(x)

    if s <= 0.0:
        return

    #normalise prob of each pos
    inv = 1.0 / s
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            matrix[i][j] *= inv

    return matrix


def bayes_update(prior: list[list[float]], sensed: bool, pos: tuple[int, int], size: int) -> list[list[float]]:

    """
    This function receives the prior matrix and the position to be studied. Studies the different outcomes and updates the prob of danger in the studied position.
    Args:
        prior (list[list[float]]): the prior matrix.
        sensed (bool): if a danger is sensed.
        pos (tuple[int, int]): the current position to be studied.
        size (int): the size of the matrix.
    Returns:
        updated_matrix (list[list[float]]): the resulting posterior matrix.
    """

    close_by_pos = get_close_by_positions(pos, size)
    post = []
    for i in range(size):
        row = []
        for j in range(size):

            in_close_by = ((i, j) in close_by_pos)

            #op1: sensed danger but not a ngb -> impossible, p=0
            if sensed and not in_close_by:
                row.append(0.0)

            #op2: not sensed danger and a ngb -> no danger, p=0
            elif (not sensed) and in_close_by:
                row.append(0.0)

            #other options: there is danger -> obtain p from prior 
            else:
                row.append(float(1*prior[i][j]))
        post.append(row)

    return normalize_matrix(post)


def get_traps_matrix(danger1: list[list[float]], danger2: list[list[float]], danger3: list[list[float]]) -> list[list[float]]:

    """
    This function gets the 3 danger matrices and obtains the total traps danger matrix.
    Args:
        danger1 (list[list[float]]): the first danger matrix.
        danger2 (list[list[float]]): the second danger matrix.
        danger3 (list[list[float]]): the third danger matrix.
    Returns:
        traps_matrix (list[list[float]]): the total traps danger matrix that combines the danger probs of each 3 types.
    """

    #initial values
    size = len(danger1)
    traps_matrix = []

    for i in range(size):
        row = []
        for j in range(size):
            row.append(float(danger1[i][j]) + float(danger2[i][j]) + float(danger3[i][j]))
        traps_matrix.append(row)

    return traps_matrix


def add_probs(m1: list[list[float]], m2: list[list[float]]) -> list[list[float]]:

    """
    This function sums the probability in each pos from other 2 matrix.
    It is used to obtain the global danger matrix: all traps + enemy soldier.
    Args:
        m1 (list[list[float]]): the first matrix to be summed.
        m2 (list[list[float]]): the second matrix to be summed.
    Returns:
        global_danger_matrix (list[list[float]]): the resulting matrix after being summed.
    """

    #intial values
    size = len(m1)
    global_danger_matrix = []

    for i in range(size):
        row = []
        for j in range(size):
            row.append(float(m1[i][j]) + float(m2[i][j]))
        global_danger_matrix.append(row)
    return global_danger_matrix


def save_heatmaps(traps_total: list[list[float]],
                  soldier_map: list[list[float]],
                  exit_map: list[list[float]],
                  out_dir: str,
                  step: int,
                  pos: tuple[int, int]) -> None:
    """
    Save 3 heatmaps as PNG automatically.
    """

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    fig, axs = plt.subplots(1, 3, figsize=(10, 3))

    mats = [traps_total, soldier_map, exit_map]
    titles = ['Traps (F+P+D)', 'Soldier (M)', 'Exit (S)']

    for k in range(3):
        ax = axs[k]
        ax.imshow(mats[k], interpolation='nearest')
        ax.set_title(titles[k])
        ax.scatter([pos[1]], [pos[0]], c='cyan', s=60, marker='x')
        ax.set_xticks([])
        ax.set_yticks([])

    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, f'heatmaps_{step:04d}.png'), dpi=140)
    plt.close(fig)



class BayesianWillard:

    def __init__(self, size: int, risk_threshold: float = 0.15) -> None:

        """
        This function initialises Bayesian agent with uniform priors.
        """

        self.size = size
        self.pos = (0, 0)
        self.grenade = True
        self.kurtz_found = False

        self.visited = {self.pos: 1} #dict to count how many times a pos has been visited -> no loops
        self.last_pos = None 
        
        self.soldier_dead = False

        self.prob_base = float(risk_threshold)
        self.prob = float(risk_threshold)

        self.step = 0
        self.exit_tried = set()

        self.maps = {}
        for element in BAYES_ELEMENTS:
            self.maps[element] = create_uniform_prior(size, (0, 0))


    def mark_current_safe(self) -> None:

        """
        This function marks current positions as safe. 
        Args:
            self
        Returns:
            None. Updates internal values.
        """

        #initial values
        coord_i, coord_j = self.pos[0], self.pos[1]

        for t in TRAP_TYPES:
            self.maps[t][coord_i][coord_j] = 0.0
            normalize_matrix(self.maps[t])

        if not self.soldier_dead:
            self.maps['ES'][coord_i][coord_j] = 0.0
            normalize_matrix(self.maps['ES'])

        #update visit count
        if self.pos in self.visited:
            self.visited[self.pos] += 1
        else:
            self.visited[self.pos] = 1


    def update_beliefs(self, percepts: list[bool]) -> None:

        """
        This function updates the agent beliefs using the obtained percepts.
        Args:
            self
            percepts (list[bool]): the percepts list as a boolean list.
        Returns:
            None. It updates internal values.
        """

        fire, spikes, darts, enemy_soldier, exit = percepts[0], percepts[1], percepts[2], percepts[3], percepts[4]
        scream = percepts[9]

        #if scream heard -> enemy soldier is no more on the board -> update danger matrix
        if scream:

            self.soldier_dead = True
            zero_matrix = []
            
            for i in range(self.size):
                row = [] 
                for j in range(self.size):
                    row.append(0.0) 
                zero_matrix.append(row)
            self.maps['ES'] = zero_matrix

        #traps maps
        self.maps['F'] = bayes_update(self.maps['F'], fire, self.pos, self.size)
        self.maps['P'] = bayes_update(self.maps['P'], spikes, self.pos, self.size)
        self.maps['D'] = bayes_update(self.maps['D'], darts, self.pos, self.size)

        #enemy soldier map
        if not self.soldier_dead:
            self.maps['ES'] = bayes_update(self.maps['ES'], enemy_soldier, self.pos, self.size)

        #exit map
        self.maps['ET'] = bayes_update(self.maps['ET'], exit, self.pos, self.size)

        self.mark_current_safe()


    def traps_total(self) -> list[list[float]]:

        """
        This function gets the total traps danger matrix.
        Args:
            self
        Returns:
            traps_danger_matrix (list[list[float]]): the resulting traps matrix.
        """

        return get_traps_matrix(self.maps['F'], self.maps['P'], self.maps['D'])


    def risk_map(self) -> list[list[float]]:

        """
        This function updates glboal risk map. It gets traps danger map and adds enemy soldier danger map.
        Args:
            self
        Returns:
            global_danger_map (list[list[float]]): the resulting matrix of suming all possible dangers.
        """
        base = self.traps_total()
        if self.soldier_dead:
            return base
        return add_probs(base, self.maps['ES'])
    

    def evaluate_risk_update_p(self) -> tuple[list[list[float]], tuple[int, int] | None]:

        """
        This function calculates risk map and updates the agent's prob of danger based on neighbors.
        Args:
            self
        Returns:
            risk_map (list[list[float]]): the matrix that represents the risk en each position of the board.
            best (tuple[int, int]): the best position to go based on risk.
        """
        
        #initial values
        risk_map = self.risk_map()
        ngbs = neighbors(self.pos, self.size)
        
        if len(ngbs) == 0:
            return risk_map, None

        safe_positions, unvisited_candidates = self.obtain_all_pos_candidates(ngbs, risk_map)
    
        #decision logic: new safe pos, no new safe pos, risk it in a new unsafe pos (penalty)

        #prioritize new safe pos
        if unvisited_candidates:
            
            #sort by low risk
            unvisited_candidates.sort(key=lambda x: x[0])
            best = unvisited_candidates[0][1]
            self.last_pos = self.pos
            return risk_map, best

        #no new safe pos -> trackback
        if safe_positions:
            
            #prioritize no last position
            candidates = []
            for nb in safe_positions:
                if nb != self.last_pos:
                    candidates.append(nb)
            if not candidates:
                candidates = safe_positions  #only safe pos = last one
            
            #sort by visited times
            candidates.sort(key=lambda nb: self.visited[nb])
            
            best = candidates[0]
            self.last_pos = self.pos
            return risk_map, best

        #if no safe options -> accept risk action
        return self.risky_action(ngbs, risk_map)


    def obtain_all_pos_candidates(self, ngbs: list[tuple[int, int]], risk_map: list[list[float]]) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:

        """
        This function gets all the surrounding positions of a current pos and classifies them in order to select where to move.
        Args:
            self
            ngbs (list[tuple[int, int]]): the surrounding positions of the current position.
            risk_map (list[list[float]]): a matrix that represents the risk of each position of the board.
        Returns:
            safe_positions (list[tuple[int, int]]): the safe surrounding positions (visited or with very low risk).
            unvisited_candidates (list[tuple[int, int]]): new acceptable (based on the risk accepted) candidates positions.
        """

        #identify safe neighbors (0 risk or visited)
        safe_positions = []
        for nb_study in ngbs:
            coord_i, coord_j = nb_study[0], nb_study[1]
            if nb_study in self.visited and float(risk_map[coord_i][coord_j]) < 0.01:
                safe_positions.append(nb_study)
        
        #identify acceptable candidates (risk ander established p)
        unvisited_candidates = []
        for nb_study in ngbs:
            if nb_study not in self.visited:
                risk = float(risk_map[nb_study[0]][nb_study[1]])
                if risk <= self.prob:
                    unvisited_candidates.append((risk, nb_study))

        return safe_positions, unvisited_candidates


    def risky_action(self, ngbs: list[tuple[int, int]], risk_map: list[list[float]]) -> tuple[list[list[float]], tuple[int, int]]:

        """
        This function selects the less dangerous risky action. It is only used when no safe movement is found.
        Args:
            self
            ngbs (list[tuple[int, int]]): the surrounding positions of the current position.
            risk_map (list[list[float]]): a matrix that represents the risk of each position of the board.
        Returns:
            risk_map (list[list[float]]): the updated matrix that represents the risk of each position of the board.
            best_pos (tuple[int, int]): the less dangerous position to move to.
        """

        #accept higher risk probs
        self.prob = min(0.45, self.prob + 0.05)
        
        #initial values for search of less bad neighbor
        best_pos = None
        best_score = 1e9
        
        for nb_sutdy in ngbs:

            risk = float(risk_map[nb_sutdy[0]][nb_sutdy[1]])
            
            #penalise visit
            visit_count = self.visited.get(nb_sutdy, 0)
            penalty = 0.1 * visit_count 
            score = risk + penalty
            
            if score < best_score:
                best_score = score
                best_pos = nb_sutdy
        
        self.last_pos = self.pos
        return risk_map, best_pos
    
    
    def choose_action_auto(self, percepts: list[bool]) -> str | None:

        """
        This function chooses the action to execute in the automatic mode. It follows a policy.
        Args:
            self
            percepts (list[bool]): a list of booleans that represents the percepts.
        Returns:
            action (str|None): the selected action to be executed.
        """

        #po 1: exit if possible
        if self.kurtz_found and self.pos not in self.exit_tried:
            if float(self.maps['ET'][self.pos[0]][self.pos[1]]) >= 0.90:
                return EXIT_ACTION

        #op2: kill enemy soldier
        if (not self.soldier_dead) and self.grenade and percepts[3]:

            best_ngb = None
            best_value = -1.0
            enemy_soldier_prob = self.maps['ES']

            #find most prob position where enemy soldier can be
            for ngb in neighbors(self.pos, self.size):
                ngb_value = float(enemy_soldier_prob[ngb[0]][ngb[1]])
                if ngb_value > best_value:
                    best_value = ngb_value
                    best_ngb = ngb

            #get action
            if best_ngb is not None:
                move = action_between(self.pos, best_ngb)
                if move is not None:
                    grenade_dir = grenade_from_move(move)
                    if grenade_dir is not None:
                        return grenade_dir

        #op3: move -> find best position to move
        risk_map, best_position = self.evaluate_risk_update_p()

        if best_position is None:
            return None

        return action_between(self.pos, best_position)


    def choose_action_manual(self) -> str:

        """
        This function asks the user to select an action to be executed.
        Args:
            self
        Returns:
            action (str): the action selected by the user.
        """

        print('\n', '-'*8, 'All possible action', '-'*8, '\n')
        print('  - Movement: W | A | S | D'
            '\n  - Grenade: GW | GA | GS | GD'
            '\n  - Exit: E\n')
        
        while True:
            action = input('Action: ').strip().upper()
            if action in DIRS or action in GREN or action == EXIT_ACTION:
                return action
            print('Invalid action.')


def execute_action(environment: dict, agent: BayesianWillard, action: str) -> tuple[bool, bool, str]:

    """
    Execute an action and return (scream, done, result).
    This function executes a given action and updates the values following its consequences.
    Args:
        environment (dict[str: bool|str]): all the environmentironment info.
        agent (BayesianWillard): the agent.
        action (str): the action to be executed.
    Returns:
        scream (bool): a signal if the enemy soldier is killed.
        done (bool): a boolean to control the game execution.
        result (str): a str that describes the result of executing the given action.
    """

    #initial values
    size = environment['size']
    scream = False
    done = False
    result = 'RUNNING'

    #movement action
    if action in DIRS:
        new_pos, moved = apply_move(agent.pos, action, size)
        agent.pos = new_pos

        if moved and agent.pos == environment['kurtz_pos'] and not agent.kurtz_found:
            agent.kurtz_found = True
            print('You found Colonel Kurtz.')

        if position_not_safe(environment, agent.pos):
            return scream, True, 'DEADTRAP'

        if environment['soldier_alive'] and agent.pos == environment['soldier_pos']:
            return scream, True, 'DEADSOLDIER'

        return scream, done, result

    #grenade action
    if action in GREN:
        if not agent.grenade:
            print('Grenade is not available right now.')
            return scream, done, result

        agent.grenade = False
        move_dir = GREN[action]
        target, moved = apply_move(agent.pos, move_dir, size)

        if environment['soldier_alive'] and target == environment['soldier_pos']:
            environment['soldier_alive'] = False
            scream = True
            print('Scream! The enemy soldier has been eliminated.')
        else:
            print('The grenade exploded, nothing happened.')

        return scream, done, result

    #exit action
    if action == EXIT_ACTION:
        agent.exit_tried.add(agent.pos)

        if agent.pos == environment['exit_pos'] and agent.kurtz_found:
            return scream, True, 'WIN'

        print('Exit is not possible right now.')
        return scream, done, result

    print('Invalid action.')
    return scream, done, result


def run_game(size: int, seed: int|None, mode: str, out_dir: str) -> None:

    """
    This function handles the game execution. It initialises the environment and starts the game.
    It also handles the creation of an empty directory to save the heatmaps.
    Args:
        size (int): the size of the board.
        seed (int|None): the seed used for randomy generating the environment.
        mode (str): the selected mode of execution.
        out_dir (str): the directory where the heatmaps are saved.
    Returns:
        None. It executes the game.
    """

    clean_directory(out_dir)

    #initial values
    env = create_environment(size, seed)
    agent = BayesianWillard(size, risk_threshold=0.15) # Updated to match init
    done = False
    last_scream = False

    #general loop of exectuion
    while not done and agent.step < 500:

        percepts = get_percepts(env, agent.pos, last_scream)
        last_scream = False

        agent.update_beliefs(percepts)

        #autosave heatmaps every step (required)
        save_heatmaps(
            traps_total=agent.traps_total(),
            soldier_map=agent.maps['ES'],
            exit_map=agent.maps['ET'],
            out_dir=out_dir,
            step=agent.step,
            pos=agent.pos,
        )

        if mode == 'AUTO':
            
            #obtain risk map
            risk_map, _ = agent.evaluate_risk_update_p()

            #print all info
            print_info(agent, percepts, risk_map)

            #action
            action = agent.choose_action_auto(percepts)
            print(f'Chosen action (AUTO): {action}')
            if action is None:
                print('No action available. Stopping.')
                return
        else:

            #update p logic for manual mode as well to keep state consistent
            risk_map, _ = agent.evaluate_risk_update_p()
            print_info(agent, percepts, risk_map)
            action = agent.choose_action_manual()

        scream, done, result = execute_action(env, agent, action)
        if scream:
            last_scream = True
            agent.soldier_dead = True

        if done:
            print(f'Result: {result}')
            return

        agent.step += 1

    print('Max steps reached. Stopping.')


def print_info(agent: BayesianWillard, percepts: list[bool], risk_map): 

    """
    This function prints information for the user to play in manual mode.
    Args:
        agent (BayesianWillard): the agent.
        percepts (list[bool]): the percepts as a boolean list.
        risk_map (list[list[float]]): the global risk map.
    Returns:
        None. It just prints the information.
    """

    print('\n\n', '-'*8, f'STEP {agent.step+1}', '-'*8, '\n')

    #map
    print_board(agent, risk_map)

    #percepts
    to_paint_text = []
    if percepts[0]: to_paint_text.append('FIRE')
    if percepts[1]: to_paint_text.append('SPIKES')
    if percepts[2]: to_paint_text.append('DARTS')
    if percepts[3]: to_paint_text.append('ENEMY SOLDIER')
    if percepts[4]: to_paint_text.append('GLOW')
    if percepts[5]: to_paint_text.append('WALL UP')
    if percepts[6]: to_paint_text.append('WALL DOWN')
    if percepts[7]: to_paint_text.append('WALL LEFT')
    if percepts[8]: to_paint_text.append('WALL RIGHT')
    if percepts[9]: to_paint_text.append('SCREAM')

    if not to_paint_text:
        print('\n  - Percepts: None obtained')
    else:
        print(f'\n  - Percepts: {' | '.join(to_paint_text)}')

    #current knowledge
    print('\n', '-'*3, 'Current information', '-'*3, '\n')
    print(f'  - Grenade: {'YES' if agent.grenade else 'NO'}')
    print(f'  - Found Kurtz:   {'YES' if agent.kurtz_found else 'NO'}')
    

def print_board(agent: BayesianWillard, risk_map: list[list[float]]) -> None:

    """
    This function prints the board for the manual mode.
    Args:
        agent (BayesianWillard): the agent.
        risk_map (list[list[float]]): the risk map to be printed.
    Returns:
        None. It just prints the board.
    """

    for i in range(agent.size):

        row = ' '
        for j in range(agent.size):

            position = (i,j)
            if position == agent.pos:
                row += 'W    '
            else:
                row += f'{risk_map[i][j]:.2f} '
        print(row)


def clean_directory(out_dir: str) -> None:

    """
    This function cleans the directory if possible in order to save current heatmaps.
    Args:
        out_dir (str): the directory where the heatmaps are to be saved.
    Returns:
        None.
    """

    #create directory if necessary
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    for filename in os.listdir(out_dir):

        file_path = os.path.join(out_dir, filename)

        #delete earlier data
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path) 
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path) 
        except Exception as e:
            print(f'Could not delete earlier data.')


def main() -> None:

    """
    This function handles the global execution of the game.
    Args:
        None.
    Returns:
        None.
    """

    print('-'*8,' BAYESIAN PALACE ', '-'*8)
    
    print('Games mode:' \
    '\n\t1. Manual mode.' \
    '\n\t2. Automatic mode.')
    selected_mode = input('Select a game mode (1/2): ').strip()

    if selected_mode == '1':
        mode = 'MANUAL'
    else:
        mode = 'AUTO'

    run_game(size=6, seed=None, mode=mode, out_dir='heatmaps')


if __name__ == '__main__':
    main()