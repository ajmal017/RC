import random as ra
"""
Algorithm Questions for Sami that he should think about before coding
0. Write the assignment in your own words
1. What conditions must be met to determine if a number is odd
2. What is the idea behind the first to score: (best_of_scenario + 1) / 2?
3. Draw a table of possible scenarios and outcomes
    scenario1: human == 1 (paper) and computer == 2 (scissors)
    scenario2: human == 2 (scissors) and computer == 1 (paper)
    etc
4. How would test the final code. Create a set of test cases


Python Questions for Sami
1. How is a random number generated in Python?
2. How does Python's while statement work?
3. How do you import modules to get extra functions?
4. How does Python accept user input and what does it store? How do you convert string to integer?
5. Understand what the format function does when printing and how to use {} (curly brackets)
6. How do you print a newline
7. How do functions work


"""

def play_paper_scissors_stone():

    # Initialise variable
    best_of_scenario = 0

    # An number is odd if the remainder = 0 when it is divided by 2
    # The % (modulo operator) returns the remainder e.g. 38 % 7 will return 3
    # The while loop will keep asking the player to enter an odd number
    while best_of_scenario % 2 == 0:
        # The input function only accepts an integer
        best_of_scenario = int(input("Enter number of best of scenario (total number of rounds): "))

    # Initialise scores
    human_total_score = human_score = 0
    computer_total_score = computer_score = 0
    round = 0

    # Keep playing until either player gets a score of "(best_of_scenario + 1) / 2"
    while human_total_score != ((best_of_scenario + 1) / 2) and computer_total_score != ((best_of_scenario + 1) / 2):

        round = round + 1

        # Initialise variable that stores the choice the human player
        human_choice = 0

        # Ask the player to enter their choice
        # The while loop will keep asking the player to enter a valid choice of 1, 2 or 3
        while human_choice != 1 and human_choice != 2 and human_choice != 3:
            human_choice = int(input("\nChoose paper(1), scissors(2) or stone(3): "))

        # Now use the random function to generate the computer's choice
        computer_choice = ra.randint(1, 3)

        # Determine score
        human_score, computer_score = get_scores(human_choice, computer_choice)
        winner = "Nobody"
        if human_score > computer_score:
            winner = "Human"
        elif human_score < computer_score:
            winner = "Computer"

        # Update running totals
        human_total_score = human_total_score + human_score
        computer_total_score = computer_total_score + computer_score

        # Print results
        print("Round {} (human chose {}, computer chose {}), winner is: {}".format(
            round, get_paper_scissors_stone(human_choice), get_paper_scissors_stone(computer_choice), winner))

    # Print final results
    final_winner = "Nobody"
    if human_total_score > computer_total_score:
        final_winner = "Human"
    elif human_total_score < computer_total_score:
        final_winner = "Computer"

    print("\n------------------------------")
    print("Total number of rounds played: {}".format(round))
    print("Final winner is {}".format(final_winner))


def get_paper_scissors_stone(x):
    paper_scissors_stone = ''
    if x == 1:
        paper_scissors_stone = "paper"
    elif x == 2:
        paper_scissors_stone = "scissors"
    elif x == 3:
        paper_scissors_stone = "stone"
    return paper_scissors_stone


def get_scores(player1, player2):
    score1 = score2 = 0

    # Both players score 0 if they choose the same
    if player1 == player2:
        score1 = score2 = 0

    # player1 chooses paper and player2 chooses scissors
    elif player1 == 1 and player2 == 2:
        score1 = 0
        score2 = 1

    # player1 chooses scissors and player2 paper
    elif player1 == 2 and player2 == 1:
        score1 = 1
        score2 = 0

    # player1 chooses paper and player2 chooses stone
    elif player1 == 1 and player2 == 3:
        score1 = 1
        score2 = 0

    # player1 chooses stone and player2 chooses paper
    elif player1 == 3 and player2 == 1:
        score1 = 0
        score2 = 1

    # player1 chooses stone and player2 chooses scissors
    elif player1 == 3 and player2 == 2:
        score1 = 1
        score2 = 0

    # player1 chooses scissors and player2 chooses stone
    elif player1 == 2 and player2 == 3:
        score1 = 0
        score2 = 1

    return score1, score2


if __name__ == "__main__":
    play_paper_scissors_stone()
