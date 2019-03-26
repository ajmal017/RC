import random


def maths_game():

    arithmetic_type = input("Which game shall we play? (+, -, *, /")

    if arithmetic_type == "+":
        number1 = random.randint(1, 20)
        number2 = random.randint(1, 20)
        correct_answer = number1 + number2

    elif arithmetic_type == "-":
        number1 = random.randint(1, 20)
        number2 = random.randint(1, 20)
        # swap numbers
        if number1 < number2:
            n = [number1, number2]
            number1 = n[1]
            number2 = n[0]
        correct_answer = number1 - number2

    elif arithmetic_type == r"\\":
        number1 = random.randint(1, 12)
        number2 = random.randint(1, 12)
        dividend = number1 * number2

    else:
        arithmetic_type = "*"
        number1 = random.randint(2, 12)
        number2 = random.randint(2, 12)
        correct_answer = number1 * number2

    print("\nWhat is ", number1, arithmetic_type, number2)
    student_answer = int(input("Answer: "))

    if student_answer == correct_answer:
        print("Correct")
    else:
        print("Wrong. You are a Lord Mordor. Correct answer is {}".format(number1 * number2))


def J1():
    print("my name is jasmine\n"*5)


if __name__ == "__main__":
    #multiplication_game()
    J1()