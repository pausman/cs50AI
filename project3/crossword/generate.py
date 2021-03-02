import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)

         the words must be the length of the crossword variable.
        """
        for var in self.domains:
            for w in self.crossword.words:
                if len(w) != var.length:
                    self.domains[var].remove(w)

        # raise NotImplementedError

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlaps = self.crossword.overlaps[x, y]
        # print(f"overlaps are {overlaps} for {x} and {y}")
        revise = False
        a, b = overlaps
        # print(f"{self.domains[x]}")
        # print(f"{self.domains[y]}")
        # print(f"overlap xy is {overlaps}")
        # for each word in x check y words to see if there is a match a overlaps
        awords_to_delete = set()
        for aword in self.domains[x]:
            aword_is_good = 0
            # print(f"looking at {aword} and {self.domains[y]} at {a} {b}")
            for bword in self.domains[y]:
                if aword != bword and aword[a] == bword[b]:
                    # print(f"MATCH for {aword} and {bword} at {overlaps}")
                    aword_is_good = 1
                    break
            if aword_is_good == 0:
                awords_to_delete.add(aword)
                # print(f"Found a word that has no match {aword}")
        for aw in awords_to_delete:
            # print(self.domains[x])
            self.domains[x].remove(aw)
            revise = True
            # print(self.domains[x])
        return revise
        # raise NotImplementedError

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if not arcs:
            arcs = []
            for var in self.domains:
                n = self.crossword.neighbors(var)
                for neighbor in n:
                    arcs.append((var, neighbor))

            queue = arcs
        else:
            queue = list(arcs)
        while queue:
            x, y = queue.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                n = self.crossword.neighbors(x)
                for z in n:
                    if z != y:
                        queue.append((z, x))

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        go through the variables and see if they are in assignment. If not return false.
        """
        for v in self.crossword.variables:
            if v not in assignment.keys():
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for x in assignment:
            word1 = assignment[x]
            if x.length != len(word1):
                return False

            for y in assignment:
                word2 = assignment[y]
                if x != y:
                    if word1 == word2:
                        return False

                    overlap = self.crossword.overlaps[x, y]
                    if overlap:
                        a, b = overlap
                        if word1[a] != word2[b]:
                            return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighbors = self.crossword.neighbors(var)
        for i in assignment:
            if i in neighbors:
                neighbors.remove(i)
        result = []
        # for every value in domain, check for overlaps that don't satisfy criteria
        for val in self.domains[var]:
            total_ruled_out = 0
            for var2 in neighbors:
                for val2 in self.domains[var2]:
                    overlap = self.crossword.overlaps[var, var2]
                    if overlap:
                        a, b = overlap
                        if val[a] != val2[b]:
                            # if values don't match, they need to removed
                            total_ruled_out += 1
            result.append([val, total_ruled_out])
        result.sort(key=lambda x: (x[1]))
        return [i[0] for i in result]
        #raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        lv = []
        for v in self.crossword.variables:
            if v not in assignment.keys():
                lv.append((len(self.domains[v]), v,
                           len(self.crossword.neighbors(v))))
        if len(lv) == 0:
            return None
        # sort by min num of remaining values and then the most neighbors
        lv.sort(key=lambda x: (x[0], -x[2]))
        # return the variable
        return lv[0][1]

        #raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # if assignment complete:
        if self.assignment_complete(assignment):
            return assignment
        # find a variable that has not been assigned
        var = self.select_unassigned_variable(assignment)
        # for value in Domain-Values(var, assignment, csp):
        # try assigning every possible domain value for that variable, one at a time
        for val in self.order_domain_values(var, assignment):
            # copy the assignemnt
            new_assigment = assignment.copy()
            # assign the word val to the assignemnt with key of var
            # add {var = value} to assignment
            new_assigment[var] = val

            # if value consistent with assignment:
            if self.consistent(new_assigment):
                # backtrack with the new assignment
                # result = Backtrack(assignment, csp)
                result = self.backtrack(new_assigment)
                # if result ≠ failure:return result
                if result:
                    return result
                # remove {var = value} from assignment which means dont add it
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
