import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';
import { generateCVPackage } from '../services/api';

const GeneratorPage = () => {
  const [jobTitle, setJobTitle] = useState('Frontend Developer');
  const [topSkills, setTopSkills] = useState('React, Tailwind CSS, REST APIs');
  const [experienceLevel, setExperienceLevel] = useState('3-5 years');
  const [personalStrengths, setPersonalStrengths] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});
  
  // New timeout state
  const [generationTimeout, setGenerationTimeout] = useState(null);
  
  const { user } = useAuth();
  const navigate = useNavigate();

  // Cleanup timeout on component unmount
  useEffect(() => {
    return () => {
      if (generationTimeout) {
        clearTimeout(generationTimeout);
      }
    };
  }, [generationTimeout]);

  // Validation function
  const validateForm = () => {
    const errors = {};
    
    if (!jobTitle.trim()) {
      errors.jobTitle = 'Job title is required';
    }
    
    if (!topSkills.trim()) {
      errors.topSkills = 'At least one skill is required';
    }
    
    if (!experienceLevel) {
      errors.experienceLevel = 'Experience level is required';
    }
    
    // Check if user has required fields
    if (!user?.fullName) {
      errors.user = 'User full name is missing. Please update your profile.';
    }
    
    if (!user?.email) {
      errors.user = 'User email is missing. Please update your profile.';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleGenerate = async () => {
    // Clear previous errors
    setError('');
    setValidationErrors({});
    
    // Validate form
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    // Set a timeout for generation
    const timeout = setTimeout(() => {
      setIsLoading(false);
      setError('The AI is thinking hard... (This might take 1-2 mins on local GPUs)');
      setGenerationTimeout(null);
    }, 180000); // 45 seconds
    
    setGenerationTimeout(timeout);

    try {
      // Parse skills from comma-separated string
      const skillsArray = topSkills.split(',').map(skill => skill.trim()).filter(skill => skill);
      
      if (skillsArray.length === 0) {
        clearTimeout(timeout);
        setError('Please provide at least one skill');
        setIsLoading(false);
        setGenerationTimeout(null);
        return;
      }

      const payload = {
        full_name: user.fullName,
        email: user.email,
        desired_job_title: jobTitle.trim(),
        top_skills: skillsArray,
        experience_level: experienceLevel,
        personal_strengths: personalStrengths.trim() || undefined
      };

      console.log("Sending payload to AI Engine:", payload);
      
      const response = await generateCVPackage(payload);
      console.log("Received AI-generated package:", response);

      // Clear timeout on successful response
      clearTimeout(timeout);
      setGenerationTimeout(null);
      setIsLoading(false);

      // Navigate to editor with generated content
      navigate('/editor', { 
        state: { 
          generatedContent: response,
          originalRequest: payload
        } 
      });

    } catch (err) {
      console.error("AI Generation failed:", err);
      
      // Clear timeout on error
      clearTimeout(timeout);
      setGenerationTimeout(null);
      setIsLoading(false);
      
      // Handle different types of errors
      if (err.response?.status === 422) {
        setError('Invalid input data. Please check your entries and try again.');
      } else if (err.response?.status === 401) {
        setError('Authentication failed. Please log in again.');
      } else if (err.response?.status === 500) {
        setError('Server error occurred. Please try again later.');
      } else {
        setError(err.response?.data?.detail || 'An unexpected error occurred while generating the CV.');
      }
    }
  };

  // Handle input changes and clear related validation errors
  const handleJobTitleChange = (e) => {
    setJobTitle(e.target.value);
    if (validationErrors.jobTitle) {
      setValidationErrors(prev => ({ ...prev, jobTitle: undefined }));
    }
  };

  const handleTopSkillsChange = (e) => {
    setTopSkills(e.target.value);
    if (validationErrors.topSkills) {
      setValidationErrors(prev => ({ ...prev, topSkills: undefined }));
    }
  };

  const handleExperienceLevelChange = (e) => {
    setExperienceLevel(e.target.value);
    if (validationErrors.experienceLevel) {
      setValidationErrors(prev => ({ ...prev, experienceLevel: undefined }));
    }
  };

  // Loading state for when user data is not available
  if (!user) {
    return (
      <div className="generator-page">
        <div className="loading-container">
          <p>Loading user information...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="generator-page">
      <div className="generator-header">
        <h1>Welcome, {user.fullName}!</h1>
        <p>Provide a few details, and our AI will create a professional CV tailored to your needs.</p>
        
        {/* NEW: Smart CV Assistant Button */}
        <div style={{ 
          margin: '20px 0',
          padding: '16px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '12px',
          textAlign: 'center'
        }}>
          <p style={{ 
            color: 'white', 
            marginBottom: '12px',
            fontSize: '1rem',
            fontWeight: '500'
          }}>
            💡 Already have a CV? Let AI improve it!
          </p>
          <button 
            onClick={() => navigate('/interactive')}
            style={{
              padding: '12px 32px',
              background: 'white',
              color: '#667eea',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '1rem',
              fontWeight: '600',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
              transition: 'transform 0.2s'
            }}
            onMouseOver={(e) => e.target.style.transform = 'scale(1.05)'}
            onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
          >
            🤖 Try Smart CV Assistant (Upload & Improve)
          </button>
        </div>
      </div>
      
      <div className="generator-form">
        <div className="form-group">
          <label htmlFor="jobTitle">Desired Job Title *</label>
          <input 
            id="jobTitle"
            type="text" 
            value={jobTitle} 
            onChange={handleJobTitleChange}
            className={validationErrors.jobTitle ? 'error' : ''}
            placeholder="e.g., Frontend Developer, Marketing Manager"
          />
          {validationErrors.jobTitle && (
            <span className="error-text">{validationErrors.jobTitle}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="topSkills">Your Top Skills (comma-separated) *</label>
          <input 
            id="topSkills"
            type="text" 
            value={topSkills} 
            onChange={handleTopSkillsChange}
            className={validationErrors.topSkills ? 'error' : ''}
            placeholder="e.g., React, JavaScript, Node.js, Python"
          />
          {validationErrors.topSkills && (
            <span className="error-text">{validationErrors.topSkills}</span>
          )}
          <small className="help-text">Separate skills with commas</small>
        </div>

        <div className="form-group">
          <label htmlFor="experienceLevel">Experience Level *</label>
          <select 
            id="experienceLevel"
            value={experienceLevel} 
            onChange={handleExperienceLevelChange}
            className={validationErrors.experienceLevel ? 'error' : ''}
          >
            <option value="">Select experience level</option>
            <option value="Entry-level">Entry-level</option>
            <option value="1-3 years">1-3 years</option>
            <option value="3-5 years">3-5 years</option>
            <option value="5+ years">5+ years</option>
          </select>
          {validationErrors.experienceLevel && (
            <span className="error-text">{validationErrors.experienceLevel}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="personalStrengths">Personal Strengths (optional)</label>
          <textarea 
            id="personalStrengths"
            value={personalStrengths} 
            onChange={(e) => setPersonalStrengths(e.target.value)}
            placeholder="e.g., Strong problem-solving abilities, excellent communication skills, leadership experience"
            rows="3"
          />
          <small className="help-text">Describe your key personal strengths and qualities</small>
        </div>

        {validationErrors.user && (
          <div className="error-message user-error">
            <p>{validationErrors.user}</p>
          </div>
        )}

        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}

        <button 
          onClick={handleGenerate} 
          disabled={isLoading} 
          className={`submit-button ${isLoading ? 'loading' : ''}`}
        >
          {isLoading ? (
            <>
              <span className="spinner"></span>
              Generating... Please Wait
            </>
          ) : (
            'Generate My AI CV'
          )}
        </button>

        <div className="form-footer">
          <p>
            <strong>Note:</strong> The AI will generate a complete CV package including 
            professional summary, experience points, education suggestions, and a cover letter.
          </p>
        </div>
      </div>
    </div>
  );
};

export default GeneratorPage;