# sampling
Gradient-free sampling techniques


## Getting started
1. Set up a virtual environment. From the root folder (`sampling`), run  
   ```
   $ python3.11 -m venv .venv  
   ```  
   This will create a virtual environment and store its files in a folder `sampling/.venv/`. You can choose another folder name or location, but `.venv` is already in .gitignore.

2. Activate the virtual environment:
   ```  
   $ source .venv/bin/activate  
   ```

   Make sure your IDE is using the Python interpreter of the venv. In VSCode, bring up VSCode preferences, e.g. with `shift + command + P`, search for `Python: Select Interpreter`, and enter the path to the interpreter: `./sampling/.venv/bin/python3.11`.

3. Update pip:  
   ```  
   $ pip install --upgrade pip  
   ```

4. Install the gradient-free sampling (gfs) package, either with developer packages or without:

   With dev packages:  
   ```  
   $ pip install -e '.[dev]'  
   ```  
   Without dev packages:  
   ```  
   $ pip install -e .  
   ```

   Check that the package has installed successfully by running  
   ```  
   $ gfs --help  
   ```
