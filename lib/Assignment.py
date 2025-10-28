class Assignment:
    def __init__(self, assignment: dict[str, str]):
        self.assignment = assignment

    def isValid(self, R: dict[str, set[str]]) -> bool:
        print(self)

        # for each assigned letter
        for letter, assignment_letter in self.assignment.items():
            # check if it's a valid choice out of the elements in the R_i sets
            if assignment_letter not in R[letter]:
                print(f"is not valid: letter {letter} has invalid assignment {assignment_letter}")
                return False

        print("is valid: all letters have valid assignments\n")
        return True

    def __str__(self):
        string = ""
        for letter, assignment_letter in self.assignment.items():
            string += f"{letter} --> {assignment_letter}\n"
        return string