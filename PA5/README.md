# ciscode

Example code for CIS. This is a functioning program for PA1 and may serve as a starting point for
the rest of the assignments.

Do not distribute. If you use any of this code in your projects, please cite

```bibtex
@misc{benjamindkilleen2021Nov,
	author = {benjamindkilleen},
	title = {{ciscode}},
	journal = {GitHub},
	year = {2021},
	month = {Nov},
	note = {[Online; accessed 12. Nov. 2021]},
	url = {https://github.com/benjamindkilleen/ciscode}
}
```

being sure to alter the access date.

## Aside on SSH Keys

SSH keys are a more secure, less annoying alternative to typing your password every time you commit
your code. This allows you to commit more often, leading to more granular code updates and a better
sense of progress. When working on group projects, this is desirable to make sure everyone is
working on the same code.

[Here](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)
are the instructions for adding an ssh key to GitHub. If you don't know what an ssh key, first
[check to see if your computer already has
one](https://docs.github.com/en/articles/checking-for-existing-ssh-keys). If not, [generate
one](https://docs.github.com/en/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent),
then add it to GitHub.

## Dependencies

We recommend using [Anaconda3](https://www.anaconda.com/products/individual) to manage your environments.

- MacOS: use the command line installer. From the terminal, run

  ```sh
  wget https://repo.anaconda.com/archive/Anaconda3-2021.05-MacOSX-x86_64.sh
  sh Anaconda3-2021.05-MacOSX-x86_64.sh
  ```

  and follow the install instructions with `~/anaconda3` as the install location (unless you really know what you're doing).

- Linux: similarly:

  ```sh
  wget https://repo.anaconda.com/archive/Anaconda3-2021.05-Linux-x86_64.sh
  sh Anaconda3-2021.05-Linux-x86_64.sh
  ```

- Windows: I recommend using the linux subsystem with VS Code remote. Then follow the linux install
  instructions. Windows isn't great for Python development.

## Install

In a terminal, clone this repo:

```sh
git clone git@github.com:benjamindkilleen/ciscode.git # or unzip from file.
```

Then change into the directory, create the Anacoconda environment, and activate it.

```bash
cd ciscode
conda env create -f environment.yml
conda activate ciscode
```

## Usage

```bash
python pa1.py -n pa1-debug-a
```

## Unit Tests

Use [pytest](https://docs.pytest.org/en/6.2.x/). In the `tests/` directory, place `.py` files that
start with `test_`, and contain functions that start with `test_`. Then use `assert` statements to
evaluate parts of your code.

Run all tests with

```sh
pytest -s
```

Or focus on a particular test, for example a function called `test_registration()` in `test_frame.py`:

```sh
pytest -s tests/test_frame.py::test_registration
```

The `-s` option tells pytest to allow `print` statements and other logging (use
[logging](https://docs.python.org/3/library/logging.html)!) to be passed through.
