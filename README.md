# Finding Colonel Kurtz — Logical, Bayesian and MDP Agents

Final project for **Foundations of Artificial Intelligence** (iMAT, ICAI, Universidad Pontificia Comillas, 2025/26). Individual project.

A Wumpus-style grid world: Captain Willard must explore a palace with hidden hazards, find Colonel Kurtz and escape alive, with only partial information.

## Part 1 — Logical agent (`willard.py`, `kurtz.py`)

- 6×6 board with pits, an enemy soldier (killable with a single grenade), Kurtz and a hidden exit.
- Knowledge base of safe / visited / dangerous / suspicious cells built from 8 boolean percepts (breeze, snore, glow, walls, scream).
- Logical inference: marks safe cells, confirms a hazard when only one candidate remains, narrows the set of exit candidates.
- Manual mode: the agent shows its deductions and the user picks the action.

## Part 2a — Bayesian agent (`palace.py`)

- Three trap types plus soldier and exit, each with its own **probability map** (uniform prior, Bayesian update on every percept, normalization).
- Combined risk map; decision policy with an **adaptive risk threshold** that grows only when no safe move exists, back-tracking to low-risk visited cells, and a loop penalty.
- Grenade aimed at the most likely soldier cell; exit attempted only when its posterior is high.
- Manual and automatic modes; heatmaps saved every turn to visualise belief evolution.
- **20 automatic runs: 95 % success, 40.2 steps on average.**

## Part 2b — Markov Decision Process (`river_mdp.py`)

- 7×6 river with random per-column currents (stochastic transitions), two random islands and an exit on the far bank.
- Full MDP (states, actions, transitions, rewards) solved with **Value Iteration** (Bellman optimality, γ = 0.95) and policy extraction; BFS check that a feasible path exists.
- **20 simulated episodes: mean reward 76.65, range [61, 86].**

## Run

Python ≥ 3.12.

```bash
pip install numpy matplotlib
python kurtz.py       # Part 1 – logical agent (manual)
python palace.py      # Part 2a – Bayesian agent (manual / auto)
python river_mdp.py   # Part 2b – MDP + value iteration
```

Full write-up: [`report/memoria.pdf`](report/memoria.pdf) (Spanish). Code comments are in English.

## Author

Ignacio Mascarell Agúndez
