import React, { useState, useRef } from 'react';
import axios from 'axios';
import { Button, ListGroup, Spinner, Alert } from 'react-bootstrap';

function Record() {
    const [isRecording, setIsRecording] = useState(false);
    const [recordings, setRecordings] = useState([]);
    const [feedbackMessage, setFeedbackMessage] = useState('');
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    const startRecording = async () => {
        // Clear previous recordings
        setRecordings([]);
        setFeedbackMessage('');
        
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorderRef.current = new MediaRecorder(stream);
                mediaRecorderRef.current.start();
                setIsRecording(true);

                mediaRecorderRef.current.ondataavailable = (event) => {
                    audioChunksRef.current.push(event.data);
                };
            } catch (error) {
                console.error('Error accessing the microphone:', error);
                setFeedbackMessage('Failed to access the microphone.');
            }
        } else {
            alert('Audio recording is not supported by your browser.');
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
            mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
            setIsRecording(false);

            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/mpeg' });
            const audioUrl = URL.createObjectURL(audioBlob);
            setRecordings([audioUrl]); // Set with new recording only
            audioChunksRef.current = [];
            setFeedbackMessage('Recording stopped.');
        }
    };

    const handleUpload = async (audioUrl) => {
        try {
            const audioBlob = await fetch(audioUrl).then(r => r.blob());
            const formData = new FormData();
            formData.append('file', audioBlob, 'recording.mp3');

            const response = await axios.post('http://localhost:5000/upload_audio', formData);
            console.log('Server response:', response.data);
            setFeedbackMessage('Upload successful!');
        } catch (error) {
            console.error('Upload failed:', error);
            setFeedbackMessage('Upload failed.');
        }
    };

    return (
        <div>
            {feedbackMessage && <Alert variant="info">{feedbackMessage}</Alert>}
            <Button onClick={isRecording ? stopRecording : startRecording} variant={isRecording ? "danger" : "primary"}>
                {isRecording ? 'Stop Recording' : 'Start Recording'}
                {isRecording && <Spinner as="span" animation="border" size="sm" className="ml-2" />}
            </Button>
            <ListGroup className="mt-3">
                {recordings.map((recording, index) => (
                    <ListGroup.Item key={index} className="d-flex justify-content-between align-items-center">
                        <audio controls src={recording}></audio>
                        <Button onClick={() => handleUpload(recording)} variant="success">Upload</Button>
                    </ListGroup.Item>
                ))}
            </ListGroup>
        </div>
    );
}

export default Record;