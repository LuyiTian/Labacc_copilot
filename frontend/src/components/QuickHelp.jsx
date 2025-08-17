import React, { useState } from 'react';
import './QuickHelp.css';

const QuickHelp = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const capabilities = [
    {
      category: "📁 Project & Files",
      items: [
        "Create new project from hypothesis",
        "Import existing data (ZIP/folders)",
        "Upload PDFs/Word/PowerPoint (auto-converts)",
        "Browse and select multiple files"
      ]
    },
    {
      category: "🔬 Analysis",
      items: [
        "Analyze experiment data",
        "Compare multiple experiments",
        "Diagnose experimental issues",
        "Get optimization suggestions"
      ]
    },
    {
      category: "📚 Research",
      items: [
        "Search scientific literature",
        "Get standard protocols",
        "Find recent papers on topics",
        "Ask questions in any language"
      ]
    },
    {
      category: "💡 Tips",
      items: [
        "Ctrl+click to select multiple files",
        "Drag & drop to upload files",
        "Works in Chinese/English/Spanish",
        "Agent remembers your insights"
      ]
    }
  ];
  
  const quickCommands = [
    "Scan my experiments",
    "What went wrong with exp_001?",
    "Compare all PCR results",
    "Find CRISPR papers from 2024",
    "列出所有实验",
    "分析这个数据"
  ];
  
  return (
    <div className={`quick-help ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <div className="quick-help-header" onClick={() => setIsExpanded(!isExpanded)}>
        <span className="help-icon">💡</span>
        <span className="help-title">Quick Help</span>
        <span className="toggle-icon">{isExpanded ? '▼' : '▶'}</span>
      </div>
      
      {isExpanded && (
        <div className="quick-help-content">
          <div className="capabilities-section">
            <h4>What You Can Do:</h4>
            {capabilities.map((cat, idx) => (
              <div key={idx} className="capability-group">
                <h5>{cat.category}</h5>
                <ul>
                  {cat.items.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          
          <div className="commands-section">
            <h4>Example Commands:</h4>
            <div className="command-list">
              {quickCommands.map((cmd, idx) => (
                <div key={idx} className="command-example">
                  <code>{cmd}</code>
                </div>
              ))}
            </div>
          </div>
          
          <div className="help-footer">
            <p>💡 <strong>Tip:</strong> Just describe what you need in natural language!</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuickHelp;