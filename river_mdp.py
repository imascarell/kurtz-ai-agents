# river_mdp.py

import random
import numpy as np


ACTIONS = ['up', 'down', 'left', 'right', 'stay']

MOVE_ACTIONS = {
    'up': (-1, 0),
    'down': (1, 0),
    'left': (0, -1),
    'right': (0, 1),
    'stay': (0, 0),
}


def in_bounds(position: tuple[int, int], size_i: int, size_j: int) -> bool:

    """
    This function checks if a given position is inside the board.
    Args:
        position (tuple[int, int]): the position to be studied.
        size_i (int): the horizontal size of the board.
        size_j (int): the horizontal size of the board.
    """

    #initial values
    coord_i, coord_j = position[0], position[1]
    valid = True

    if coord_i not in range(0,size_i):
        valid = False
    if coord_j not in range(0,size_j):
        valid = False
    return valid
	

def neighbors(position: tuple[int, int], size_i: int, size_j) -> list[tuple[int, int]]:

    """
    This function returns valid neighbors (up,right,down,left) of a position to be studied.
    Args:
        position (tuple[int,int]): coord_i, coord_j of the current position whose neighburs are to be obtained.
        size_i (int): the horizontal size of the board.
        size_j (int): the horizontal size of the board.
    Returns:
        ngb (list[tuple[int,int]]): list of neighbors of the current position.
    """

    #initial values
    ngbs = []
    coord_i, coord_j = position[0], position[1]

    for move in ACTIONS[:-1]:

        dir_i, dir_j = MOVE_ACTIONS[move][0], MOVE_ACTIONS[move][1]
        position_ngb = (coord_i + dir_i, coord_j + dir_j)

        if in_bounds(position_ngb, size_i, size_j):
            ngbs.append(position_ngb)

    return ngbs


def bfs_path_exists(start: tuple[int, int], goal: tuple[int, int], n_rows: int, n_cols: int, blocked: set[tuple[int, int]]) -> bool:
	
    """
    This function studies if a path exists from start to goal avoiding blocked positions. It uses BFS.
    Args:
        start (tuple[int,int]): the start position.
        goal (tuple[int,int]): the goal position.
        n_rows (int): the number of rows.
        n_cols (int): the number of columns.
        blocked (set[tuple[int,int]]): a set that contains all blocked positions (islands).
    Returns:
        bool: The boolean that represents if there is a path. True if yes.
    """
    
    #op1: given pos are blocked
    if start in blocked or goal in blocked:
        return False

    
    #op2: look for path using bfs

    #initial values
    queue = [start]
    head = 0

    while head < len(queue):
        
        #select current pos
        current = queue[head]
        head += 1

        #if current pos is goal -> path exists
        if current == goal:
            return True

        #else: add neighbors of current to be studied
        for other_cand in neighbors(current, n_rows, n_cols):
            if other_cand not in blocked and other_cand not in queue:
                queue.append(other_cand)

    return False


class RiverMDP:

    def __init__(self, n_rows: int, n_cols: int, n_islands: int, seed: int|None, gamma: float, reward_exit: int, reward_danger: int, reward_step: int, allow_stay: bool) -> None:
        
        """
        This function initiliases the environment and the MDP parameters.
        Args:
            n_rows (int): the number of rows of the board.
            n_cols (int): the number of columns of the board.
            n_islands (int): the number of islands.
            seed (int|None): the seed used for generating the environment randomly.
            gamma (float): the discount factor for value iteration (MDP).
            reward_exit (int): the reward for reaching the exit.
            reward_danger (int): the reward for falling into a dangerous position.
            reward_step (int): the reward per step (negative to encourage short paths).
            allow_stay (bool): include 'stay' action in the action set.
        """
        
        #initial values
        self.n_rows = int(n_rows)
        self.n_cols = int(n_cols)
        self.n_islands = int(n_islands)

        #mdp values
        self.gamma = float(gamma)
        self.reward_exit = int(reward_exit)
        self.reward_danger = int(reward_danger)
        self.reward_step = int(reward_step)

        self.rng = random.Random(seed)
        self.start = (0, 0)
        self.exit = (self.rng.randrange(0, self.n_rows), self.n_cols - 1)
        self.islands = set()
        self.currents = []

        #actions
        self.actions = ['up', 'down', 'left', 'right']
        if allow_stay:
            self.actions.append('stay')

        self.generate_valid_world()

        #functionality
        self.all_outcomes = {} 
        self.precompute_model()


    def generate_valid_world(self) -> None:

        """
        This function generates the board and its elements. It ensures there's a solution.
        Args:
            self
        Returns:
            None
        """

        attempts = 0

        while True and attempts < 10000:

            attempts += 1

            #currents by columns
            self.currents = []
            for j in range(self.n_cols):
                if j == 0 or j == self.n_cols - 1:
                    self.currents.append(0.0)
                else:
                    current_value = round(self.rng.uniform(0.06, 0.94), 1)
                    self.currents.append(float(current_value))

            #islands
            self.islands = set()
            while len(self.islands) < self.n_islands:
                
                #select islands positions randomly
                i, j = self.rng.randint(1, self.n_rows - 2), self.rng.randint(1, self.n_cols - 2)
                pos = (i, j)
                
                #add if pos is valid
                if pos != self.start and pos != self.exit:
                    self.islands.add(pos)

            #confirm there is a solution
            if bfs_path_exists(self.start, self.exit, self.n_rows, self.n_cols, self.islands):
                return


    def precompute_model(self) -> None:

        """
        This function explores all the environment and saves all the possible outcomes in each position with its probability.
        Args:
            self
        Returns:
            None
        """

        for i in range(self.n_rows):
            for j in range(self.n_cols):

                position = (i, j)

                #study only non-terminal positions
                if position not in self.islands and not self.study_terminal(position):
                    
                    self.all_outcomes[position] = {}

                    for action in self.actions:

                        #obtain data of the pos
                        transitions = self.get_transitions(position, action)
                        outcomes = []
                        for next_state, prob in transitions.items():
                            r = self.reward(next_state)
                            outcomes.append((prob, next_state, r))
                        
                        #save obtained data
                        self.all_outcomes[position][action] = outcomes


    def get_river_strength(self, j: int) -> float:

        """
        This function returns the current strength of a column.
        Args:
            self
            j (int): column index.
        Returns:
            float: column current strength.
        """

        return float(self.currents[j])


    def study_terminal(self, current_position: tuple[int, int]) -> bool:

        """
        This function checks if a state is terminal.
        Args:
            self
            current_position (tuple[int,int]): the position to be studied.
        Returns:
            bool: a boolean that represents if the state is terminal. True if yes.
        """

        if current_position == self.exit:
            return True
        return False
    

    def execute_action(self, current_pos: tuple[int, int], action: str) -> tuple[int, int]:
        
        """
        This function recieves an action and a position and executes the action returning the resulting position..
        Args:
            self
            current_pos (tuple[int,int]): the current position.
            action (str): the action to be executed.
        Returns:
            tuple[int,int]: candidate next position.
        """

        coord_i, coord_j = current_pos[0], current_pos[1]
        dir_i, dir_j = MOVE_ACTIONS.get(action, (0, 0))

        return (coord_i + dir_i, coord_j + dir_j)


    def validate_destination(self, initial_pos: tuple[int, int], dest_pos: tuple[int, int]) -> tuple[int, int]:
        
        """
        This function studies if the destination position is valid (in bounds and no island)
        Args:
            self
            initial_pos (tuple[int,int]): original state.
            dest_pos (tuple[int,int]): candidate destination.
        Returns:
            tuple[int,int]: corrected destination.
        """

        if not in_bounds(dest_pos, self.n_rows, self.n_cols):
            return initial_pos
        if dest_pos in self.islands:
            return initial_pos
        return dest_pos
    

    def get_transitions(self, current_position: tuple[int, int], action: str) -> dict[tuple[int, int]: float]:
        
        """
        This function applies the transition model P(S'|s,a) for MDP.
        Args:
            self
            current_position (tuple[int,int]): the current position of the agent.
            action (str): the action.
        Returns:
            dict[tuple[int,int]: float]: the dictionary of each possible outcoming position and its probability.
        """

        #terminal state -> prob = 1
        if self.study_terminal(current_position):
            return {current_position: 1.0}

        coord_i, coord_j = current_position[0], current_position[1]

        #op1: action = down -> current helps movement
        if action == 'down':
            position_down = self.validate_destination(current_position, (coord_i + 1, coord_j))
            return {position_down: 1.0}

        #op2: action != down -> fight against current for movement
        probs = self.movement_against_current(current_position, action)

        return probs
    
    def movement_against_current(self, current_position: tuple[int, int], action: str) -> dict[tuple[int, int]: float]:
        
        """
        This function handles the probability of each possible resulting position after movement.
        Args:
            self
            current_position (tuple[int, int]): the current position of the agent.
            action (str): the action to be executed.
        Returns:
            probs (dict[tuple[int, int]: float]): the dictionary of each possible outcoming position and its probability.
        """

        #initial values
        coord_i, coord_j = current_position[0], current_position[1]
        curr_strength = self.get_river_strength(coord_j)
        prob_dir = 1.0 - curr_strength
        prob_down = curr_strength

        #possible resulting positions
        position_dir_raw = self.execute_action(current_position, action)
        position_down_raw = (coord_i + 1, coord_j)

        #validate outcomes
        target_act = self.validate_destination(current_position, position_dir_raw)
        target_down = self.validate_destination(current_position, position_down_raw)

        #dictionary with probs
        probs = {}
        probs[target_act] = probs.get(target_act, 0.0) + float(prob_dir)
        probs[target_down] = probs.get(target_down, 0.0) + float(prob_down)

        return probs

    def reward(self, target_position: tuple[int, int]) -> int:
        
        """
        This function gets the reward of executing and action R(s, a, s').
        Args:
            target_position (tuple[int,int]): the next position.
        Returns:
            int: the reward value.
        """

        if target_position == self.exit:
            return self.reward_exit

        if target_position in self.islands:
            return self.reward_danger

        return self.reward_step


    def value_iteration(self, theta: float, max_iters: int) -> np.ndarray:

        """
        This function executes the value iteration using the data obtained with self.all_outcomes.
        Args:
            self
            theta (float): 
            max_iters (int): a limit of iterations to help with possible loops.
        Returns:
            V_MATRIX (np.ndarray): the matrix containing the value for each position.
        """

        #initial values
        V_MATRIX = np.zeros((self.n_rows, self.n_cols), dtype=float)
        delta = float(theta) + 1.0 
        iteration = 0

        while iteration < max_iters and delta >= theta:

            iteration += 1
            delta = 0.0
            V_new = V_MATRIX.copy()

            #study only non-terminal states and all its possible outcomes
            for state, actions_data in self.all_outcomes.items():
                
                best_val = -float('inf')
                for action, outcomes in actions_data.items():
                    q_value = 0.0
                    
                    #bellman ecuation
                    for prob, next_state, r in outcomes:
                        val_next = V_MATRIX[next_state[0], next_state[1]]
                        q_value += prob * (r + self.gamma * val_next)
                    
                    if q_value > best_val:
                        best_val = q_value

                #update values
                V_new[state[0], state[1]] = best_val
                
                curr_val = V_MATRIX[state[0], state[1]]
                diff = abs(best_val - curr_val)
                if diff > delta:
                    delta = diff
            
            V_MATRIX = V_new

        return V_MATRIX


    def get_policy(self, V: np.ndarray) -> dict[tuple[int, int]: str]:
        
        """
        This function gets the best policy based on V.
        Args:
            V (np.ndarray): the values matrix.
        Returns:
            policy_action (dict[tuple[int,int]: str]): the dictionary of each position and its best possible action.
        """

        policy_action = {}

        for i in range(self.n_rows):
            for j in range(self.n_cols):

                current_position = (i, j)

                if current_position not in self.islands and not self.study_terminal(current_position):
                    
                    #initial values for iteration
                    best_a = None
                    best_val = -float('inf')

                    for a in self.actions:
                        transitions = self.get_transitions(current_position, a)

                        #bellman ecuation
                        q_value = 0.0
                        for target_pos, prob in transitions.items():
                            r = self.reward(target_pos)
                            q_value += float(prob) * (float(r) + self.gamma * float(V[target_pos[0], target_pos[1]]))

                        if q_value > best_val:
                            best_val = q_value
                            best_a = a

                    if best_a is None:
                        best_a = 'stay'

                    policy_action[current_position] = best_a

        return policy_action


    def select_next_pos(self, transitions: dict[tuple[int, int]: float]) -> tuple[int, int]:

        """
        Sample a next state using Python's built-in weighted choice.
        This function samples randomly the next movement.
        Args:
            self
            transitions (dict[tuple[int, int]: float]): the dictionary that contains each possible resulting position and its probability.
        Returns:
            selected_pos (tuple[int, int]): the randomly selected position.
        """

        states = list(transitions.keys())
        probs = list(transitions.values())
        
        return self.rng.choices(states, weights=probs, k=1)[0]


    def paint_board(self, agent_pos: tuple[int, int]|None) -> None:
        
        """
        This function paints the board game.
        Args:
            agent_pos (tuple[int,int]|None): the agent position.
        Returns:
            None
        """
        print('\n', '-'*8, 'THE BOARD', '-'*8, '\n')

        for i in range(self.n_rows):
            row = []
            for j in range(self.n_cols):

                position = (i, j)

                #obtain the representation of each element
                if agent_pos is not None and position == agent_pos:
                    row.append('A')
                elif position == self.start:
                    row.append('S')
                elif position == self.exit:
                    row.append('E')
                elif position in self.islands:
                    row.append('I')
                else:
                    row.append('-')
            print(' '.join(row))

        print('\nCurrents:', self.currents)


    def paint_policy(self, policy: dict[tuple[int, int]: str]) -> None:

        """
        This function paints the board policy.
        Args:
            policy (dict[tuple[int,int]: str]): the dictionary that contains the best policy in each position.
        Returns:
            None
        """
        
        #initial values
        action_simbols = {
        'right': 'R',
        'down': 'D',
        'up': 'U',
        'left': 'L'
        }

        print('\n', '-'*8, 'BEST POLICY', '-'*8, '\n')

        for i in range(self.n_rows):
            row = []
            for j in range(self.n_cols):

                position = (i, j)

                #obtain the representation of each element
                if position == self.start:
                    row.append('S')
                elif position == self.exit:
                    row.append('E')
                elif position in self.islands:
                    row.append('I')
                else:
                    action = policy.get(position, 'stay')
                    action_trad = action_simbols[action]
                    row.append(action_trad)

            print(' '.join(row))
        
        #leyend
        print('\n- Leyend - \n')
        print('S: start' \
        '\nE: exit' \
        '\nI: island' \
        '\nU: up' \
        '\nD: down' \
        '\nR: right' \
        '\nL: left')


    def simulate_episode(self, policy: dict[tuple[int, int]: str], max_steps: int, see_details: bool) -> tuple[bool, int, int]:
        
        """
        Simulate one episode following a given policy.
        Args:
            policy (dict[tuple[int,int]: str]): policy mapping.
            max_steps (int): cap on steps.
            see_details (bool): if True, print step-by-step transitions.
        Returns:
            tuple[bool, int, int]:
                - success (bool): True if exit reached.
                - steps (int): number of steps taken.
                - total_reward (int): cumulative reward.
        """

        #initial values and paint board
        position = self.start
        total_reward = 0

        for i in range(max_steps):
            if self.study_terminal(position):
                if see_details:
                    print(f'\nSuccess.\nSteps: {i} \nTotal reward: {total_reward}')
                return True, i, total_reward

            action = policy.get(position, 'stay')
            trans = self.get_transitions(position, action)
            next_pos = self.select_next_pos(trans)

            r = self.reward(next_pos)
            total_reward += int(r)

            if see_details:
                print(f'{i+1}. Position: {position} | Action: {action} | Next position: {next_pos} | Reward: {r}')

            position = next_pos

        if see_details:
            print(f'\nSTOP (step cap). Total reward: {total_reward}')

        return False, max_steps, total_reward


if __name__ == '__main__':

    print('\n--- RIVER MDP ---\n')

    mdp = RiverMDP(7, 6, 2, None, 0.95, 100, -100, -1, True)

    V_MATRIX = mdp.value_iteration(1e-6, 50000)
    policy = mdp.get_policy(V_MATRIX)

    mdp.paint_board(agent_pos=None)
    mdp.paint_policy(policy)

    print('\nSimulating execution:\n')
    mdp.simulate_episode(policy, 200, True)

