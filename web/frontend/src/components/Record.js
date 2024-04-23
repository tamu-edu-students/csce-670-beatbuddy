// src/AudioRecorder.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from "../Config.json"

const Record = ({onAudioReady}) => {
  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [audioURL, setAudioURL] = useState('');
  const [audioBlob, setAudioBlob] = useState(null);

  const startRecording = async () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      let chunks = [];

      recorder.ondataavailable = e => chunks.push(e.data);
      recorder.onstop = () => {
        const blob = new Blob(chunks, { 'type' : 'audio/mp3' });
        chunks = [];
        const url = URL.createObjectURL(blob);
        setAudioURL(url);
        setAudioBlob(blob);
      };

      recorder.start();
      setMediaRecorder(recorder);
      setRecording(true);
    } else {
      alert('Recording is not supported in this browser.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setRecording(false);
    }
  };

  const uploadAudio = async () => {
    if (audioBlob) {
      const formData = new FormData();
      formData.append('file', audioBlob, 'audio.mp3');

      try {
        const response = await axios.post(config.python_url + '/upload_audio', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        console.log('File uploaded successfully', response.data);
      } catch (error) {
        console.error('Error uploading file', error);
      }
    }
    onAudioReady();
  };

  return (
    <div className="d-flex flex-column align-items-center pt-4 pb-4">
    <h3 className="mb-3 text-center">Search Audio</h3>
    <button
      className={`btn ${recording ? 'btn-danger' : 'btn-primary'} mb-3`}
      onClick={recording ? stopRecording : startRecording}
    >
      <i className={`fas ${recording ? 'fa-stop-circle' : 'fa-microphone'}`}></i>
      {recording ? ' Stop Recording' : ' Start Recording'}
    </button>
    {audioURL && (
      <div className="d-flex flex-column align-items-center">
        {/* <audio className="mb-3 w-100" controls src={audioURL}></audio> */}
        <button className="btn btn-success" onClick={uploadAudio}>
          <i className="fas fa-upload"></i> Upload
        </button>
      </div>
    )}
  </div>

  );
  
};

export default Record;
