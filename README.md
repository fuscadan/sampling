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

## Setting up a project

Projects must have a configuration stored in a TOML file. See `src/gfs/projects/biased_coin.toml` for an example. The configuration specifies filepaths to data and output files, the stastical model to be used, and parameters like the number of posterior samples to take.

It is suggested, but not necessary, that project configuration files be placed in `src/gfs/projects/` and data files be placed in `src/gfs/data/< project_name >`.

## Infering parameters / training a model

The `update_prior` command will use the given training data to update the prior distribution on the model's parameters. The command saves the posterior distribution as a JSON file in a format used by the gradient-free sampling algorithm. 
```
gfs < path/to/config.toml > [Options] update_prior [Options]
```

The posterior can then be sampled to understand the distribution of model parameters or to make predictions, or used as a prior distribution for future updates with more data. The `sample_posterior` command loads the posterior JSON file, samples it a specified number of times, and saves those samples as a CSV.
```
gfs < path/to/config.toml > [Options] sample_posterior [Options]
```

For models with only one or two parameters, it may be useful to view a histogram of the posterior samples to get an idea of the shape of the posterior distribution. Running the `histogram` command will save a histogram as a CSV with the same name as the `posterior_samples` file but with the suffix `__histogram`.
```
gfs < path/to/config.toml > [Options] histogram [Options]
```

## Making predictions

Currently, these tools can train classifier models. Given an input, the model assigns (or "predicts") that input to a category. Two important remarks on making predictions:
1. A model's "prediction" of the input's category is actually a "predictive distribution" - a probability distribution over the possible categories.

2. The question of which model parameters to use when making a prediction is handled in the Bayesian way; for each set of parameters sampled from a posterior distribution, a predictive distribution is computed, and the final predictive distribution is taken to be the average of the results.

The `predict` command computes the predictive distributions of a set of inputs. The results are stored as a series of CSV files - one for each input. Each CSV file contains one predictive distribution for each posterior sample. As a convenience, the average predictive distribution is printed to the terminal.
```
gfs < path/to/config.toml > [Options] predict [Options]
```
