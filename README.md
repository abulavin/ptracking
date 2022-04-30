# petition-tracking

## How to Run

### Python Requirements

- Use Python 3. Preferably Python >=3.8
- Virtualenv. Easiest way to set up an isolated python environment.

### Running

- Clone repo.
- Setup a virtualenv in the base directory of the repo, using `python3.8 -m venv venv`
- Upgrade Pip if necessary `python -m pip install --upgrade pip`
- Run: `pip install -r requirements.txt`
- Run: `python3.8 -m nltk.downloader wordnet stopwords averaged_perceptron_tagger` 
- Check everything works ok: `python -m unittest discover`
- Check the module build went OK: `cd ~; python -c 'import ptracking; print("OK")`

#### Installing Mallet LDA Model

We use the Mallet LDA model alongside Gensim's typical implementation. As this is a Java-based implementation, it requires
building from source.

The source code for the latest version of mallet is contained in `ptracking/topics/`. Note that you need to install Java Runtime and
Apache Ant.

To install:
1. Untar the tar archive using `tar xvf mimno-Mallet-v202108-35-g130c614.tar.gz`
2. Build it using `ant`: `cd mimno-Mallet-130c614`, `ant` (this requires an installation of Apache `ant`). You should get `BUILD_SUCCESSFUL`.

Good to go!

### Testing

This packages uses `unittest` and `coverage` for providing unit testing and statement coverage reports respectively.
Place any unit tests under the `test/` directory and name them `test_*.py`

- To run the unit tests without generating a coverage report: `python -m unittest discover`
- To run the unit tests with a coverage report: `coverage run -m unittest discover`
- To then view the coverage report: `coverage report`

### Code Quality

- Any code that does something, should be encased within `if __name__ == '__main__':` as this prevents code from being run on import
  (All commands assume in being in the base directory)

### Development Workflow - Creating a Pull Request

TL;DR
1. `git checkout main; git pull`
2. `git checkout -b <branch-name>`
3. Make changes and periodically commit them using `git commit`
4. `git checkout main; git pull; git checkout -; git merge main`
5. `git push --set-upstream origin <branch-name>`
6. Go to Github and create pull reqest, adding reviewer(s).
7. Make sure build is green.
8. Once green and approved, merge.

When using Git, typically the `main` branch represents the 'master' version of the current source code which is expected to always be correct
and up-to-date. To make sure any new changes we bring in don't break any code on the `main` branch, we create changes using separate branches
and merge them in via pull requests.
Here's how to create a new change which can be safely merged into the `main` branch without breaking the code for everyone else.
1. In your local repository, make sure your current code reflects the latest version of `main` on Github using `git pull`, or equivalent. This
will fetch the latest version of `main` from Github and merge it into your local version of `main`.
2. Create a new branch, preferably with a concise but descriptive name which reflects what you'll be working on. With git CLI this can be done
 using `git checkout -b <branch-name>`
3. You're now free to implement whatever changes you like on this new branch. My personal recommendation is to `git commit` little and often 
with commit messages accurately describing changes, so its easier to track bugs if we have to see where there's been a regression.
4. Once you're ready to submit your changes for **Pull Request**, make sure you do step 1 to update your version of main if there's been any 
changes and then either **merge or rebase** main **into your branch**. This means your changes are made 'on-top-of' the latest changes brought 
into `main` by others. There may be some merge conflicts here. This can be done using `git checkout main; git pull; git checkout -; git merge main`.
 The last command can be `git rebase main`
5. Run `git push --set-upstream origin <branch-name>`. This will create your branch on the remote repository on Github and upload the changes
 you've made.
6. Go to Github - you should see a pop-up saying something like "branch-name had changes less than a second ago". Click "Compare and Pull Request".
7. Write a short descripting title and any description that you think will help the person reviewing your code to understand what's going on.
 Add somebody as a reviewer (can be anyone, more the merrier).
8. Create the pull request and make sure the unit test check passes.
9. Once your PR has been approved by a reviewer and all checks pass, you can merge the pull request into main.

Note: If someone has made a pull request and you want to make changes to it, its possible to do so. You can edit the changes they've added in their PR by
doing:
1. `git fetch`
2. `git checkout origin/<their-branch-name>`
3. `git switch -c <new-branch-name>`
4. Make changes
5. `git push --set-upstream origin <their-branch-name>`

