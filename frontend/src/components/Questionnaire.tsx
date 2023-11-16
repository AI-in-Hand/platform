import React, { useState } from 'react';
import { sendMessage } from '../services/api';

const Questionnaire = ({ threadId }: { threadId: string }) => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const response = await sendMessage(threadId, answer);
    setQuestion(response.data.nextQuestion); // Assuming the backend sends the next question
    setAnswer('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>{question}</label>
      <input type="text" value={answer} onChange={(e) => setAnswer(e.target.value)} />
      <button type="submit">Submit</button>
    </form>
  );
};

export default Questionnaire;
