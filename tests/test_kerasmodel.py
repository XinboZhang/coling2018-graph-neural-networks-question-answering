import keras
import pytest
import yaml
import logging

from questionanswering.datasets import webquestions_io
import models

with open("../questionanswering/default_config.yaml", 'r') as config_file:
    config = yaml.load(config_file.read())

logger = logging.getLogger(__name__)
logger.setLevel(config['logger']['level'])
ch = logging.StreamHandler()
ch.setLevel(config['logger']['level'])
logger.addHandler(ch)

config['webquestions']['extensions'] = []
config['webquestions']['max.entity.options'] = 1
config['webquestions']['target.dist'] = True
del config['webquestions']['path.to.dataset']['train_validation']
config['model']['graph.choices'] = config['webquestions'].get("max.negative.samples", 30)
config['model']['epochs'] = 2


def test_model_train():
    webquestions = webquestions_io.WebQuestions(config['webquestions'], logger=logger)
    trainablemodel = models.CharCNNModel(parameters=config['model'], logger=logger,  train_tokens=webquestions.get_question_tokens())
    assert type(trainablemodel._model) == keras.engine.training.Model
    input_set, targets = webquestions.get_training_samples()
    input_set, targets = input_set[:200], targets[:200]
    trainablemodel.train((input_set, targets),
                         validation_with_targets=webquestions.get_validation_samples()
                         if 'train_validation' in config['webquestions']['path.to.dataset'] else None)
    print('Training finished')


if __name__ == '__main__':
    pytest.main([__file__])
