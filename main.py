# system
from pathlib import Path

# thrid party

# local
from astroid_parser import astroid_parser
from astroid_solver import AstroidSolver

if __name__ == "__main__":
    # read input png
    path = Path("images/example3.png")
    astroid_location = astroid_parser(path, 0.5)    
    
    # return if none
    if astroid_location is None:
        print("No astroid location found.")
        exit(0)
    
    # created by ET01
    MINER_BLUEPRINT = "SHAPEZ2-2-H4sIAN0dd2cA/6xaXW+bMBT9L9Ye0YTNl0Haw7J2UrVEqtqs2jRVE0qcDo1C5JBtUZX/PhIMNRCofU37ELXhnHt8fX2uDbygBxRhbHsWmt2i6AW9Kw5bhiJ0s0vjbI0sdLPKs9MXV3ERo+gHSsq/o+rb2zResWeWFeVl53+n8SHfF+/n54+f97/iLVskGePIyvZpKi66ft4WB/R4tNB1VvCE7UrWF7QsY17AoZksarZP0nWSPQ3JKgUVm5w/70TAKuruxBfd7avfXuRvKPIt9B1FZQ7uUORYZy3X/woer4qcX7FNvE+Lm6xgPIvTh5gncTnio3VGBmAklZBYCxmCkZVaV1Y7Y2khQHO26QIXCec5Z+uawO8TzJNNgb9uFcBN9HmjW4r+Oed/Y74ezRYMizF4kgRUccA9sbXM25wX9yxbM95FWOhTec2Xj+efD01Y5xLDHVux5M8QRwl/xRNwiYjQIKgLz7MrD3jB+BPjZJnj+Rslhb1uotRrWWBbI9WsR38Aq7wYKgKiGdwfxY4UpqgLA9liQcB0Y9sAHPalD9dJp5p90BxXEQOD+jiFV7XadmEIJKwyBsEqE2ybxA8vDFt9NQs0GUia0tBdcFsEQakMdQBtHAQVgj31ddzJUgv5dkN7jQdu3UCw8BvQ3NRYxcF2q/FVt2Eb71Jo93FQjdTBXXg7hmXdbQ1awaO9XpYUOpl3YXTqVUXA9lwXFcwf60lxYLK9AYPULkxPam0OuDq9CQbT2gxUxbI8HwDHywuy+XEN+rlQS1smMotXv8cwbo2pjA8oOJTwGLBGQpjx+ibgRjlcM1AtRCeVdd5v06Qor8bL3BlfxVSe0lNJkNEmKlBVRgkgNW4bD6lfINg3ARNp2RG4ZwXDNBqW5Yx6gPIdkEDzGEJk4zZOwmUe7SwMbrTf3j8S2AZfoLHBBp+C7Nsf9SOlg4Wt3KICeZRYp2METajG8R34zYVasoKjBVJ+nJah6SiGm1otVXsrZMOsTB/ndqYGqhbeiqFotzNFBsqJkXICOzja5gcwG+qUdCDzBkL6REA5ZCo54D4SNizgu2sYq+/8bbn3aPlqDcWmxioRqe4VbTlJWt7aVg0xV9xSC6oU/yKFxl4Dd1I/gRKTJdTWQ6bSA9+LBfLBUkXI4qkjJOiefYAMOk47RIGNKahuoQznYxIeffMfyc0kRFS3dEczRKbKEJkqQwZEocEZITQ4IwirvnCrRqtBUcnpTfpTaw2pN6mg3x7P8q/yv5nyAIBNiho7MTVsCXSiDkUnaVB0ov5EDduT3X7xAvxM0O0vDYU9X/Oqy8gdUMXHxoYMgQFDvZHzjLPYonA004jd0e2v6pNdUwpiToHNKWxjitCYoeUUo9P4aKFZksX88MD4Ljm9+XZ6Z+94fDwe/wsgwABYhMLTwicAAA==$"
    
    optimizer = AstroidSolver()
    optimizer.add_astroid_locations(astroid_location)
    optimizer.run_solver()
    optimizer.save_variables("variables.txt")
    blueprint = optimizer.get_solution_blueprint(MINER_BLUEPRINT)
    print(blueprint)
    optimizer.show_solution_image()