# Tiny Git 

### Tiny Git is a simplified version of Git with only the basic functionalities to gain better understanding of git internals.

## Implemented Functionalities 
- init :    initialize an empty repository.
- add :     Add files to the staging area.
- status :  Shows working directory status.
- commit :  Commits the staged files to the repository.
- ls-files: List all the files in the cache/index.
- cat-file: Displays a git object in a specific format according to the mode argument.

## Usage

```bash
git clone https://github.com/a7medayman6/Tiny-Git

mkdir repo
cd repo

# initialize a repository in repo/
python3 ../Tiny-Git/tinygit.py init .

# create a new file
echo "hello world" > helloworld.txt

# show the status
python3 ../Tiny-Git/tinygit.py status 

# add helloworld.txt to the staging area
python3 ../Tiny-Git/tinygit.py add helloworld.txt

# commit the files in staging area to the repo
python3 ../Tiny-Git/tinygit.py commit -m "commit msg goes here" -a "author name goes here"

```

### Resources 
- [Mastering Git’s index - Charles Bailey](https://www.youtube.com/watch?v=lFBW2qBAcaU)
- [pygit story - by Ben Hoyt](https://benhoyt.com/writings/pygit/)