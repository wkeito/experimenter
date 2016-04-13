import os
import time
import json
import logging
from git import Repo, TagReference

__all__ = ['ExperimentLogger']

class ExperimentLogger:
    def __init__(self, name, parameters, directory=".", tag_prefix="experiments/", description=None):
        '''
        Start logging a new experiment.
        :param name: the name of the experiment
        :type name: str
        :param parameters: a dictionary with all the parameters of the experiment.
        :type parameters: dict
        :param directory: a string of the directory of the git repository, where the experiment will be logged.
        :type directory: str
        :param tag_prefix: the prefix of the "folder" where the experiment-related tags will be placed
        :type tag_prefix: str
        '''
        self.__experiment_name = "exp_" + name + str(int(time.time()))
        self.__results_recorded = False
        self.__repository = Repo(directory, search_parent_directories=True)
        if len(self.__repository.untracked_files) > 0:
            logging.warning("Untracked files will not be recorded: %s", self.__repository.untracked_files)
        if tag_prefix[-1] != '/':
            tag_prefix += '/'
        self.__tag_name = tag_prefix + self.__experiment_name
        self.__parameters = parameters
        self.__description = description

    def __enter__(self):
        self.__tag_object = self.__start_experiment(self.__parameters)
        logging.info("Started experiment %s", self.__tag_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.__results_recorded:
            self.__repository.delete_tag(self.__tag_name)
            logging.warning("Experiment %s cancelled, since no results were recorded.", self.__tag_name)
        logging.info("Experiment %s completed", self.__tag_name)

    def record_results(self, results):
        """
        Record the results of this experiment, by updating the tag.
        :param results: A dictionary containing the results of the experiment.
        :type results: dict
        """
        data = json.loads(self.__tag_object.tag.message)
        data["results"] = results
        TagReference.create(self.__repository, self.__tag_name, message=json.dumps(data),
                            ref=self.__tag_object.tag.object, force=True)
        self.__results_recorded = True

    def record_results_and_push(self, results, remote_name='origin'):
        """
        Record the results of this experiment, by updating the tag and push to remote
        :param results:  A dictionary containing the results of the experiment.
        :type results: dict
        :param remote_name: the name of the remote to push the tags (or None for the default)
        :type remote_name: str
        """
        #self.record_results(results)
        #self.__repository.remote(name=remote_name).push() #TODO: Create refspecs for tag
        raise NotImplemented()

    def name(self):
        return self.__tag_name

    def __tag_repo(self, data):
        """
        Tag the current repository.
        :param data: a dictionary containing the data about the experiment
        :type data: dict
        """
        assert self.__tag_name not in [t.name for t in self.__repository.tags]
        return TagReference.create(self.__repository, self.__tag_name, message=json.dumps(data))

    def __get_files_to_be_added(self):
        """
        :return: the files that have been modified and can be added
        """
        for root, dirs, files in os.walk(self.__repository.working_dir):
            for f in files:
                relative_path = os.path.join(root, f)[len(self.__repository.working_dir)+1:]
                try:
                    self.__repository.head.commit.tree[relative_path] # will fail if not tracked
                    yield relative_path
                except:
                    pass

    def __start_experiment(self, parameters):
        """
        Start an experiment by capturing the state of the code
        :param parameters: a dictionary containing the parameters of the experiment
        :type parameters: dict
        :return: the tag representing this experiment
        :rtype: TagReference
        """
        current_commit = self.__repository.head.commit
        started_state_is_dirty = self.__repository.is_dirty()

        if started_state_is_dirty:
            self.__repository.index.add([p for p in self.__get_files_to_be_added()])
            commit_obj = self.__repository.index.commit("Temporary commit for experiment " + self.__experiment_name)
            sha = commit_obj.hexsha
        else:
            sha = self.__repository.head.object.hexsha

        data = {"parameters": parameters, "started": time.time(), "description": self.__description,
                "commit_sha": sha}
        tag_object = self.__tag_repo(data)

        if started_state_is_dirty:
            self.__repository.head.reset(current_commit, working_tree=False, index=True)

        return tag_object
