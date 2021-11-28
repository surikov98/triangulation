# Triangulation checking
Program for checking if given triangles are the triangulation of the given polygon

# Input arguments
Options:
  * `--input` - path to the file, that contains polygon and triangles descriptions.
  
# Input file example
```
5 # number of points in polygon, after that we have 5 lines with points' coordinates
1 3
-2 4
-3 1
-2 -1
-1 2
0 1 4 # after polygon's points we have triangles descriptions - every line contains three indices
4 1 3
3 1 2
```

# Output
`да` if triangles are triangulation 

`нет` if not

# Usage example
`python main.py --input example-input.txt`

Output should be `да`
