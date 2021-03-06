#import tfx
#from tfx.v1 import orchestration, dsl
import tensorflow as tf
from tfx import v1 as tfx
import os


PIPELINE_NAME = "penguin-simple"

# Output directory to store artifacts generated from the pipeline.
PIPELINE_ROOT = os.path.join('pipelines', PIPELINE_NAME)
# Path to a SQLite DB file to use as an MLMD storage.
METADATA_PATH = os.path.join('metadata', PIPELINE_NAME, 'metadata.db')
# Output directory where created models from the pipeline will be exported.
SERVING_MODEL_DIR = os.path.join('serving_model', PIPELINE_NAME)
DATA_ROOT = "tfx-data"
 
from absl import logging
logging.set_verbosity(logging.INFO)  # Set default logging level.

def _create_pipeline(pipeline_name: str, pipeline_root: str, data_root: str,
                     module_file: str, serving_model_dir: str,
                     metadata_path: str): # -> tfx.v1.dsl.Pipeline:
  """Creates a three component penguin pipeline with TFX."""
  # Brings data into the pipeline.
  example_gen = tfx.components.CsvExampleGen(input_base=data_root)

  # Uses user-provided Python function that trains a model.
  trainer = tfx.components.Trainer(
      module_file=module_file,
      examples=example_gen.outputs['examples'],
      train_args=tfx.proto.TrainArgs(num_steps=100),
      eval_args=tfx.proto.EvalArgs(num_steps=5))

  # Pushes the model to a filesystem destination.
  pusher = tfx.components.Pusher(
      model=trainer.outputs['model'],
      push_destination=tfx.proto.PushDestination(
          filesystem=tfx.proto.PushDestination.Filesystem(
              base_directory=serving_model_dir)))

  # Following three components will be included in the pipeline.
  components = [
      example_gen,
      trainer,
      pusher,
  ]

  return tfx.dsl.Pipeline(
      pipeline_name=pipeline_name,
      pipeline_root=pipeline_root,
      metadata_connection_config=tfx.orchestration.metadata
      .sqlite_metadata_connection_config(metadata_path),
      components=components)

dsl_pipeline = _create_pipeline(
      pipeline_name=PIPELINE_NAME,
      pipeline_root=PIPELINE_ROOT,
      data_root=DATA_ROOT,
      module_file="penguin_trainer.py",
      serving_model_dir=SERVING_MODEL_DIR,
      metadata_path=METADATA_PATH)

tfx.orchestration.LocalDagRunner().run(dsl_pipeline)
#tfx.orchestration.LocalDagRunner().run(
#  _create_pipeline(
#      pipeline_name=PIPELINE_NAME,
#      pipeline_root=PIPELINE_ROOT,
#      data_root=DATA_ROOT,
#      module_file="penguin_trainer.py",
#      serving_model_dir=SERVING_MODEL_DIR,
#      metadata_path=METADATA_PATH))
