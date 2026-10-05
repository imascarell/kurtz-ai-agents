#kurtz.py

from willard import create_environment, Willard, run_game

def main():

    """
    This function initialises and runs the game in manual mode.
    Args:
        None.
    Returns:
        None. It runs the game.
    """

    size = 6
    environment = create_environment(size, None)
    willard = Willard(size)
    run_game(environment, willard, 500)

if __name__ == "__main__":
    main()