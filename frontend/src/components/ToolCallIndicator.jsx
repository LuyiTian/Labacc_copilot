import React, { useState, useEffect } from 'react';

const ToolCallIndicator = ({ sessionId }) => {
  const [toolCalls, setToolCalls] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    if (!sessionId) {
      console.log('ToolCallIndicator: No sessionId yet');
      return;
    }

    console.log(`ToolCallIndicator: Connecting to WebSocket for session ${sessionId}`);
    
    // Connect to WebSocket
    const ws = new WebSocket(`ws://localhost:8002/ws/agent/${sessionId}`);
    
    ws.onopen = () => {
      setIsConnected(true);
      setSocket(ws);
      console.log(`Tool call WebSocket connected for session ${sessionId}`);
    };

    ws.onmessage = (event) => {
      // Skip ping/pong messages
      if (event.data === 'pong') {
        return;
      }
      
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'tool_call') {
          setToolCalls(prev => {
            if (data.status === 'starting') {
              // Add new tool call with starting status
              const toolCall = {
                id: `${data.tool}_${Date.now()}`,
                tool: data.tool,
                status: 'starting',
                args: data.args || {},
                timestamp: new Date().toLocaleTimeString()
              };
              console.log(`Tool starting: ${data.tool}`);
              
              // Keep only the 3 most recent tools
              const newCalls = [...prev, toolCall];
              if (newCalls.length > 3) {
                return newCalls.slice(-3);
              }
              return newCalls;
              
            } else if (data.status === 'completed' || data.status === 'error') {
              // Find and update the existing tool call, or add new if not found
              const existingIndex = prev.findIndex(c => 
                c.tool === data.tool && c.status === 'starting'
              );
              
              if (existingIndex >= 0) {
                // Update existing tool call
                const updated = [...prev];
                updated[existingIndex] = {
                  ...updated[existingIndex],
                  status: data.status,
                  completedAt: new Date().toLocaleTimeString()
                };
                
                // Auto-remove after 10 seconds for completed tools
                if (data.status === 'completed') {
                  setTimeout(() => {
                    setToolCalls(current => 
                      current.filter(c => c.id !== updated[existingIndex].id)
                    );
                  }, 10000);  // Changed from 3000ms to 10000ms
                }
                
                console.log(`Tool ${data.status}: ${data.tool}`);
                return updated;
              } else {
                // No starting event was captured, add as completed directly
                const toolCall = {
                  id: `${data.tool}_${Date.now()}`,
                  tool: data.tool,
                  status: data.status,
                  args: data.args || {},
                  timestamp: new Date().toLocaleTimeString()
                };
                
                // Auto-remove after 10 seconds
                if (data.status === 'completed') {
                  setTimeout(() => {
                    setToolCalls(current => current.filter(c => c.id !== toolCall.id));
                  }, 10000);  // Changed from 3000ms to 10000ms
                }
                
                // Keep only the 3 most recent tools
                const newCalls = [...prev, toolCall];
                if (newCalls.length > 3) {
                  return newCalls.slice(-3);
                }
                return newCalls;
              }
            }
            
            return prev;
          });
        }
      } catch (error) {
        console.error('Error parsing tool call message:', error);
      }
    };

    ws.onclose = (event) => {
      setIsConnected(false);
      setSocket(null);
      console.log(`Tool call WebSocket disconnected: code=${event.code}, reason=${event.reason}`);
    };

    ws.onerror = (error) => {
      console.error('Tool call WebSocket error:', error);
      console.error('WebSocket readyState:', ws.readyState);
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

  // Always show if connected, even with no tool calls (for debugging)
  if (!isConnected) {
    return (
      <div className="tool-call-indicator connecting">
        <div className="tool-calls-header">
          <span className="tool-calls-title">
            <span className="connecting-spinner">⚡</span>
            Agent Tools
          </span>
          <span className="tool-calls-status">Connecting...</span>
        </div>
        <div className="tool-calls-connecting-body">
          <div className="connecting-message">
            Establishing connection to agent tools...
          </div>
        </div>
      </div>
    );
  }
  
  if (toolCalls.length === 0) {
    return (
      <div className="tool-call-indicator ready">
        <div className="tool-calls-header">
          <span className="tool-calls-title">🔧 Agent Tools</span>
          <span className="tool-calls-status ready">Ready</span>
        </div>
      </div>
    );
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
                {call.status === 'starting' ? '⚡' : 
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