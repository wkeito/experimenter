Experimenter
=======
Use git tags to log experiments and the exact code that was used to run those experiments.

Use Cases
-----
  * It is the case that you might make some changes in your machine learning code, not necessarily worth committing, and
spawn a process to run an experiment that uses these changes. However, by the time the experiment has finished you don't
know what changes you were testing.
  * You need a distributed way of collecting all the experiments (parameters and results), making sure that they have 
been run on the exact same version of the code.

Usage
-----
Create an `Experiment` object, passing the parameters of the experiment. When the experiment is finished, call
the `record_results()` method of that object, ie:
```
experiment_logger = Experiment(name="NameOfExperiment", parameters=parameters_dict)
...
experiment_logger.record_results(dict_of_results)
```

Behind the scenes, a git tag will be created (committing any changes you may have in the working tree, into a
different branch). The tag will have a name of the form `exp_NameOfExperiment_timestamp` and in the message it will 
have a JSON representation of the parameters and the results (when/if recorded). The working state of the current 
branch will seemingly remain unaffected.
 
 
TODO
------
   * A command line tool for parsing all experiments and outputing them into CSVs or another format
