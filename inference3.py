# Copyright 2019 The TensorFlow Authors All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Inference demo for YAMNet."""
from __future__ import division, print_function

import sys

import numpy as np
import resampy
import soundfile as sf
import tensorflow as tf

import params
import yamnet as yamnet_model


def main(argv):
  assert argv

  # Load the TFLite model and allocate tensors.
  interpreter = tf.lite.Interpreter(model_path="yamnet.tflite")
  interpreter.allocate_tensors()
  inputs = interpreter.get_input_details()
  outputs = interpreter.get_output_details()

  yamnet_classes = yamnet_model.class_names('yamnet_class_map.csv')

  for file_name in argv:
    # Decode the WAV file.
    wav_data, sr = sf.read(file_name, dtype=np.int16)
    assert wav_data.dtype == np.int16, 'Bad sample type: %r' % wav_data.dtype
    waveform = wav_data / 32768.0  # Convert to [-1.0, +1.0]

    # Convert to mono and the sample rate expected by YAMNet.
    if len(waveform.shape) > 1:
      waveform = np.mean(waveform, axis=1)
    if sr != params.SAMPLE_RATE:
      waveform = resampy.resample(waveform, sr, params.SAMPLE_RATE)

    # Predict YAMNet classes.
    # Second output is log-mel-spectrogram array (used for visualizations).
    # (steps=1 is a work around for Keras batching limitations.)
    with graph.as_default():
      scores, _ = yamnet.predict(np.reshape(waveform, [1, -1]), steps=1)
    # Scores is a matrix of (time_frames, num_classes) classifier scores.
    # Average them along time to get an overall classifier output for the clip.
    prediction = np.mean(scores, axis=0)

    print('yamnet_classes:\n', yamnet_classes)
    #print('prediction:\n', prediction)

    # Report the highest-scoring classes and their scores.
    top5_i = np.argsort(prediction)[::-1][:5]
    
    print('top 5 predictions:\n', top5_i)
    
    print(file_name, ':\n' + 
          '\n'.join('  {:12s}: {:.3f}'.format(yamnet_classes[i], prediction[i])
                    for i in top5_i))
    
    #Encoding Classificafication (Feedback)
    encodedClasses = [('Bark', 'A'),('Beep, bleep', 'B'), ('Buzzer','C'), ('Speech', 'D'), ('Baby cry, infant cry', 'E')]
    encodedClassesDict = dict(encodedClasses)

    for i in top5_i:
        if (yamnet_classes[i] in encodedClassesDict.keys()):
            #Chamar script que envia a mensagem para o ESP32 por Bluetooth
            print ('Enviando pattern', encodedClassesDict[yamnet_classes[i]], 'para o ESP32' )              
    
if __name__ == '__main__':
  main(sys.argv[1:])
