import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';
import { generateCVPackage } from '../services/api';

const InteractiveCVGenerator = () => {
  const [step, setStep] = useState('upload'); // upload, questions, generating
  const [uploadedCV, setUploadedCV] = useState(null);
  const [answers, setAnswers] = useState({
    targetJob: '',
    whatToAdd: '',
    whatToRemove: '',
    currentIssues: '',
    specificChanges: ''
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const { user } = useAuth();
  const navigate = useNavigate();

  const questions = [
    {
      id: 'targetJob',
      question: '🎯 What job are you applying for?',
      placeholder: 'e.g., Senior Frontend Developer at Google',
      required: true
    },
    {
      id: 'currentIssues',
      question: '🔍 What issues do you see in your current CV?',
      placeholder: 'e.g., Too long, lacks achievements, outdated design'
    },
    {
      id: 'whatToAdd',
      question: '➕ What do you want to ADD to your CV?',
      placeholder: 'e.g., Leadership experience, certifications, recent projects'
    },
    {
      id: 'whatToRemove',
      question: '➖ What do you want to REMOVE from your CV?',
      placeholder: 'e.g., Old jobs, irrelevant skills, outdated technologies'
    },
    {
      id: 'specificChanges',
      question: '✨ Any specific changes or highlights?',
      placeholder: 'e.g., Emphasize AI/ML projects, highlight team management'
    }
  ];

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('http://localhost:8000/ai/upload-resume', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });

      const result = await response.json();
      if (result.success) {
        setUploadedCV(result.extracted_text);
        setStep('questions');
      }
    } catch (err) {
      alert('Failed to upload CV: ' + err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAnswerChange = (id, value) => {
    setAnswers(prev => ({ ...prev, [id]: value }));
  };

  const handleGenerate = async () => {
    if (!answers.targetJob) {
      alert('Please specify the target job!');
      return;
    }

    setIsProcessing(true);
    setStep('generating');

    try {
      // Build enhanced prompt with conversation context
      const enhancedPrompt = `
ORIGINAL CV CONTENT:
${uploadedCV}

TARGET JOB: ${answers.targetJob}
${answers.currentIssues ? `ISSUES TO FIX: ${answers.currentIssues}` : ''}
${answers.whatToAdd ? `THINGS TO ADD: ${answers.whatToAdd}` : ''}
${answers.whatToRemove ? `THINGS TO REMOVE: ${answers.whatToRemove}` : ''}
${answers.specificChanges ? `SPECIFIC REQUESTS: ${answers.specificChanges}` : ''}

INSTRUCTIONS:
- Tailor this CV specifically for "${answers.targetJob}"
- Extract and keep: full name, email, phone number
- Fix the mentioned issues
- Add requested new elements
- Remove unnecessary content as requested
- Highlight relevant achievements for the target job
- Maintain professional tone
      `.trim();

      const payload = {
        full_name: user?.fullName || 'Professional',
        email: user?.email || 'email@example.com',
        desired_job_title: answers.targetJob,
        experience_level: '3-5 years',
        personal_strengths: `SUMMARIZE THIS RESUME: ${enhancedPrompt}`,
        top_skills: []
      };

      console.log('Sending enhanced payload to AI:', payload);

      const response = await generateCVPackage(payload);
      
      // Navigate to editor with generated content
      navigate('/editor', {
        state: {
          generatedContent: response,
          originalRequest: payload
        }
      });
    } catch (err) {
      console.error('AI Generation error:', err);
      alert('AI Generation failed: ' + err.message);
      setStep('questions');
    } finally {
      setIsProcessing(false);
    }
  };

  // Render Upload Step
  if (step === 'upload') {
    return (
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '32px' }}>
        <div style={{ background: 'white', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', padding: '32px' }}>
          <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '16px', color: '#1f2937' }}>
            🤖 AI CV Assistant
          </h1>
          <p style={{ color: '#6b7280', marginBottom: '24px' }}>
            Upload your current CV and I'll help you improve it by asking targeted questions
          </p>
          
          <div style={{ 
            border: '4px dashed #93c5fd', 
            borderRadius: '8px', 
            padding: '48px', 
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'border-color 0.3s'
          }}>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
              id="cv-upload"
              disabled={isProcessing}
            />
            <label htmlFor="cv-upload" style={{ cursor: 'pointer' }}>
              <div style={{ fontSize: '4rem', marginBottom: '16px' }}>📄</div>
              <p style={{ fontSize: '1.25rem', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                {isProcessing ? 'Reading your CV...' : 'Click to upload your CV'}
              </p>
              <p style={{ fontSize: '0.875rem', color: '#9ca3af' }}>PDF format only</p>
            </label>
          </div>

          <button
            onClick={() => navigate('/generator')}
            style={{ 
              marginTop: '24px', 
              color: '#2563eb', 
              fontWeight: '500',
              background: 'none',
              border: 'none',
              cursor: 'pointer'
            }}
          >
            ← Or create from scratch
          </button>
        </div>
      </div>
    );
  }

  // Render Questions Step
  if (step === 'questions') {
    return (
      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '32px' }}>
        <div style={{ background: 'white', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', padding: '32px' }}>
          <div style={{ marginBottom: '24px' }}>
            <h1 style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1f2937', marginBottom: '8px' }}>
              Let's improve your CV! 💡
            </h1>
            <p style={{ color: '#6b7280' }}>
              I've read your CV. Now tell me how you want to improve it:
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {questions.map((q) => (
              <div key={q.id} style={{ background: '#f9fafb', borderRadius: '8px', padding: '24px' }}>
                <label style={{ display: 'block', fontSize: '1.125rem', fontWeight: '600', color: '#1f2937', marginBottom: '12px' }}>
                  {q.question} {q.required && <span style={{ color: '#ef4444' }}>*</span>}
                </label>
                <textarea
                  value={answers[q.id]}
                  onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                  placeholder={q.placeholder}
                  rows="3"
                  style={{ 
                    width: '100%', 
                    padding: '12px', 
                    border: '1px solid #d1d5db', 
                    borderRadius: '8px',
                    fontSize: '1rem',
                    resize: 'vertical'
                  }}
                />
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', gap: '16px', marginTop: '32px' }}>
            <button
              onClick={() => setStep('upload')}
              style={{ 
                padding: '12px 24px', 
                background: '#e5e7eb', 
                color: '#374151', 
                borderRadius: '8px',
                border: 'none',
                cursor: 'pointer',
                fontWeight: '500'
              }}
            >
              ← Back
            </button>
            <button
              onClick={handleGenerate}
              disabled={!answers.targetJob || isProcessing}
              style={{ 
                flex: 1,
                padding: '12px 24px', 
                background: answers.targetJob && !isProcessing ? '#2563eb' : '#d1d5db', 
                color: 'white', 
                borderRadius: '8px',
                border: 'none',
                cursor: answers.targetJob && !isProcessing ? 'pointer' : 'not-allowed',
                fontWeight: '500',
                fontSize: '1.125rem'
              }}
            >
              {isProcessing ? 'Processing...' : '✨ Generate Improved CV'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Render Generating Step
  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '32px' }}>
      <div style={{ background: 'white', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', padding: '48px', textAlign: 'center' }}>
        <div style={{ marginBottom: '24px' }}>
          <div style={{ fontSize: '4rem', marginBottom: '16px' }}>🧠</div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1f2937', marginBottom: '8px' }}>
            AI is working on your CV...
          </h2>
          <p style={{ color: '#6b7280' }}>
            This may take 1-2 minutes. Please don't close this page.
          </p>
        </div>
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <div style={{ width: '256px', height: '8px', background: '#e5e7eb', borderRadius: '9999px', overflow: 'hidden' }}>
            <div style={{ height: '100%', background: '#2563eb', animation: 'pulse 2s infinite' }}></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InteractiveCVGenerator;