import React from 'react';
import './EditorLayout.css';

// This is a simple component that just provides the two-column grid structure.
// The `children` prop is a special React prop that renders whatever components
// are placed inside this one.
const EditorLayout = ({ children }) => {
  return (
    <div className="main-content-grid">
      {children}
    </div>
  );
};

export default EditorLayout;