import React, { useState, useEffect } from 'react';

const ToolCallIndicator = ({ sessionId }) => {
  const [toolCalls, setToolCalls] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    if (!sessionId) return;

    // Connect to WebSocket
    const ws = new WebSocket(`ws://localhost:8002/ws/agent/${sessionId}`);
    
    ws.onopen = () => {
      setIsConnected(true);
      setSocket(ws);
      console.log('Tool call WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'tool_call') {
          const toolCall = {
            id: Date.now() + Math.random(),
            tool: data.tool,
            status: data.status,
            args: data.args || {},
            timestamp: new Date().toLocaleTimeString()
          };
          
          setToolCalls(prev => {
            // Remove any previous calls with same tool if completed
            const filtered = data.status === 'running' 
              ? prev.filter(call => call.tool !== data.tool || call.status === 'completed')
              : prev;
            return [...filtered, toolCall];
          });

          // Auto-remove completed tool calls after 5 seconds
          if (data.status === 'completed' || data.status === 'error') {
            setTimeout(() => {
              setToolCalls(prev => prev.filter(call => call.id !== toolCall.id));
            }, 5000);
          }
        }
      } catch (error) {
        console.error('Error parsing tool call message:', error);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      setSocket(null);
      console.log('Tool call WebSocket disconnected');
    };

    ws.onerror = (error) => {
      console.error('Tool call WebSocket error:', error);
      setIsConnected(false);
    };

    // Cleanup on unmount
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [sessionId]);

  // Send ping to keep connection alive
  useEffect(() => {
    if (socket && isConnected) {
      const pingInterval = setInterval(() => {
        try {
          socket.send('ping');
        } catch (error) {
          console.error('Error sending ping:', error);
        }
      }, 30000); // Ping every 30 seconds

      return () => clearInterval(pingInterval);
    }
  }, [socket, isConnected]);

  if (!isConnected || toolCalls.length === 0) {
    return null;
  }

  return (
    <div className="tool-call-indicator">
      <div className="tool-calls-header">
        <span className="tool-calls-title">🔧 Agent Tools</span>
        <span className="tool-calls-count">{toolCalls.length}</span>
      </div>
      <div className="tool-calls-list">
        {toolCalls.map(call => (
          <div key={call.id} className={`tool-call-item ${call.status}`}>
            <div className="tool-call-main">
              <span className="tool-icon">
                {call.status === 'running' ? '⚡' : 
                 call.status === 'completed' ? '✅' : 
                 call.status === 'error' ? '❌' : '🔧'}
              </span>
              <span className="tool-name">{call.tool}</span>
              <span className="tool-status">{call.status}</span>
            </div>
            {Object.keys(call.args).length > 0 && (
              <div className="tool-args">
                {Object.entries(call.args).slice(0, 2).map(([key, value]) => (
                  <span key={key} className="tool-arg">
                    {key}: {String(value).substring(0, 30)}{String(value).length > 30 ? '...' : ''}
                  </span>
                ))}
              </div>
            )}
            <div className="tool-timestamp">{call.timestamp}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ToolCallIndicator;