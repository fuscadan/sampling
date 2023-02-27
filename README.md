# Bayesian inference using gradient-free sampling
This is a personal project exploring a naive approach to sampling probability distributions without using any calculus (so no integration to compute cumulative distributions, and no gradients to do something like Hamiltonian Markov chain Monte Carlo).  I expect that at some point this approach will fail to scale, but I want to see how far I can push it.

The sampling technique is applied to Bayesian inference problems. As an MVP, I have an example of inferring the bias in a weighted coin.

![Screenshot 2023-02-27 at 2 22 50 PM](https://user-images.githubusercontent.com/50221483/221666038-e093872b-7410-479a-ac80-5d64da3e3500.png)

## Getting started
1. Set up a virtual environment. From the root folder (`sampling`), run  
   ```
   python3.11 -m venv .venv  
   ```  
   This will create a virtual environment and store its files in a folder `sampling/.venv/`. You can choose another folder name or location, but `.venv` is already in .gitignore.

2. Activate the virtual environment:
   ```  
   source .venv/bin/activate  
   ```

   Make sure your IDE is using the Python interpreter of the venv. In VSCode, bring up VSCode preferences, e.g. with `shift + command + P`, search for `Python: Select Interpreter`, and enter the path to the interpreter: `./sampling/.venv/bin/python3.11` (or wherever you stored your venv files).

3. Update pip:  
   ```  
   pip install --upgrade pip  
   ```

4. Install the gradient-free sampling (gfs) package, either with developer packages or without:

   With dev packages:  
   ```  
   pip install -e '.[dev]'  
   ```  
   Without dev packages:  
   ```  
   pip install -e .  
   ```

   Check that the package has installed successfully by running  
   ```  
   gfs --help  
   ```

## Inferring parameters

1. Inference projects are specified with a yaml config file
   ```
   src/gfs/projects/<project_name>/configuration/<config_file>
   ```

2. Data is stored in the directory
   ```
   src/gfs/projects/<project_name>/data/<data_file>
   ```

3. Parameter inference is performed by calling
   ```
   gfs infer --project=<project_name> --config=<config_file>
   ```
   The project settings in the config file can be overwritten by passing command line arguments. For example:
   ```
   gfs infer --project=biased_coin --config=biased_coin.yaml --n_samples=50000
   ```
   See `gfs infer --help` for a list of arguments that may be passed to `infer`.
