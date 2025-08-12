# Chainlit-React Chat Integration Specification v1.1 (IMPLEMENTED)

## Executive Summary

This specification defines the integration of Chainlit chat functionality directly into the React frontend, creating a unified interface where users can manage files and interact with AI agents without switching between tabs.

## 1. Problem Statement

### Current State
- File management: React app on localhost:5173
- AI chat: Chainlit on localhost:8000
- Users must switch between two separate browser tabs
- No real-time synchronization between interfaces
- Disconnected user experience

### Desired State
- Single unified interface combining file management and chat
- Real-time bidirectional communication
- Shared context between file operations and chat
- Seamless user experience

## 2. Architecture Design

### 2.1 Integration Approach

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                       │
│                   localhost:5173                        │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌────────────────────────────┐  │
│  │  File Manager    │  │    Chat Component          │  │
│  │  (70% width)     │  │    (30% width)             │  │
│  │                  │  │                            │  │
│  │  - File tree     │  │  - Message history        │  │
│  │  - Upload area   │  │  - Input field            │  │
│  │  - Preview pane  │  │  - File attachments       │  │
│  └──────────────────┘  └────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                 @chainlit/react-client                  │
│                  WebSocket Connection                   │
├─────────────────────────────────────────────────────────┤
│                  Chainlit Backend                       │
│                   localhost:8000                        │
│              (LangGraph Agents + Tools)                 │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

- **Frontend Library**: @chainlit/react-client
- **Protocol**: WebSocket for real-time communication
- **State Management**: React Context API + Chainlit session
- **Message Format**: JSON with structured data types

## 3. Implementation Components

### 3.1 React Chat Component

```jsx
// src/components/ChatPanel.jsx
import { useChainlit } from '@chainlit/react-client';

export function ChatPanel({ currentFolder, selectedFiles }) {
  const { messages, sendMessage, isConnected } = useChainlit({
    url: 'ws://localhost:8000',
    context: { currentFolder, selectedFiles }
  });
  
  // Chat UI implementation
}
```

### 3.2 Chainlit React Client Setup

```jsx
// src/App.jsx
import { ChainlitProvider } from '@chainlit/react-client';

function App() {
  return (
    <ChainlitProvider
      config={{
        chainlitUrl: 'http://localhost:8000',
        theme: 'light',
        features: {
          fileUpload: true,
          voiceInput: false,
          markdown: true
        }
      }}
    >
      <MainLayout />
    </ChainlitProvider>
  );
}
```

### 3.3 Layout Structure

```jsx
// src/layouts/MainLayout.jsx
function MainLayout() {
  return (
    <div className="app-container">
      <Header />
      <div className="content-area">
        <FileManager className="file-panel" />
        <ChatPanel className="chat-panel" />
      </div>
    </div>
  );
}
```

## 4. Features

### 4.1 Core Features
- [ ] Embedded chat interface in React app
- [ ] WebSocket connection management
- [ ] Message history persistence
- [ ] File attachment from file manager
- [ ] Shared context (current folder, selected files)
- [ ] Real-time status updates
- [ ] Error handling and reconnection

### 4.2 UI Features
- [ ] Resizable panels (drag to resize)
- [ ] Collapsible chat panel
- [ ] Message threading
- [ ] Code syntax highlighting
- [ ] Markdown rendering
- [ ] File preview in chat
- [ ] Loading indicators
- [ ] Connection status indicator

### 4.3 Integration Features
- [ ] Drag files from manager to chat
- [ ] Click-to-attach selected files
- [ ] Auto-attach uploaded files to chat
- [ ] Navigate to folder from chat mentions
- [ ] Execute file operations from chat

## 5. User Workflows

### 5.1 Basic Chat Workflow
1. User opens unified interface
2. File manager loads on left, chat on right
3. User types message in chat
4. AI responds with analysis/suggestions
5. User can reference files directly

### 5.2 File-Aware Chat
```
User: [selects data.csv in file manager]
User: "Analyze this data"
AI: [automatically receives data.csv context]
AI: "I can see data.csv from exp_001. The results show..."
```

### 5.3 Action Execution
```
User: "Create a new PCR experiment folder"
AI: "Creating folder..."
[File manager updates in real-time]
AI: "Created exp_002_pcr_2025-08-12"
```

## 6. Technical Requirements

### 6.1 Dependencies
```json
{
  "@chainlit/react-client": "^1.0.0",
  "socket.io-client": "^4.0.0",
  "react-markdown": "^9.0.0",
  "react-syntax-highlighter": "^15.0.0",
  "react-resizable-panels": "^1.0.0"
}
```

### 6.2 Backend Modifications
- Enable CORS for WebSocket from localhost:5173
- Add session sharing between HTTP and WebSocket
- Implement context passing in message handlers
- Add file reference resolution

### 6.3 State Synchronization
```javascript
// Shared state between file manager and chat
const sharedContext = {
  currentFolder: '/exp_001',
  selectedFiles: ['data.csv', 'image.png'],
  recentOperations: [],
  userSession: 'user123:session456'
};
```

## 7. API Endpoints

### 7.1 WebSocket Events

**Client → Server:**
- `connect`: Initialize connection with auth
- `message`: Send user message
- `file_attach`: Attach file reference
- `context_update`: Update shared context
- `action_execute`: Execute file operation

**Server → Client:**
- `message`: AI response
- `status`: Processing status
- `file_update`: File system changes
- `action_result`: Operation results
- `error`: Error messages

### 7.2 REST Endpoints (existing)
- Keep existing FastAPI endpoints for file operations
- Chat component can trigger these via shared context

## 8. Security Considerations

### 8.1 Authentication
- Share session tokens between React and Chainlit
- Validate WebSocket connections
- Implement rate limiting

### 8.2 File Access
- Validate file paths in chat references
- Maintain project root restrictions
- Sanitize file content before display

## 9. Development Plan

### Phase 1: Basic Integration (2-3 days)
1. Install @chainlit/react-client
2. Create basic chat component
3. Establish WebSocket connection
4. Test message exchange

### Phase 2: UI Polish (2 days)
1. Implement resizable panels
2. Add markdown rendering
3. Style chat interface
4. Add loading states

### Phase 3: Context Sharing (2 days)
1. Pass file context to chat
2. Implement file attachments
3. Add folder navigation from chat
4. Test integrated workflows

### Phase 4: Advanced Features (3 days)
1. Message threading
2. Code execution from chat
3. Real-time file updates
4. Error recovery

## 10. Testing Strategy

### 10.1 Unit Tests
- Chat component rendering
- Message formatting
- WebSocket mock testing
- Context updates

### 10.2 Integration Tests
- File attachment flow
- Context synchronization
- Error handling
- Reconnection logic

### 10.3 E2E Tests
- Complete user workflows
- Multi-tab scenarios
- Network interruption
- Large file handling

## 11. Success Metrics

- **Connection Reliability**: >99% uptime
- **Message Latency**: <100ms
- **Context Sync**: Immediate (<50ms)
- **User Satisfaction**: Single-tab workflow
- **Error Rate**: <0.1% message failures

## 12. Migration Path

### 12.1 Gradual Rollout
1. Keep Chainlit standalone available
2. Add embedded chat as beta feature
3. Gather user feedback
4. Make embedded default
5. Deprecate standalone

### 12.2 Backward Compatibility
- Maintain existing REST APIs
- Support both interfaces temporarily
- Preserve message history
- Export/import conversations

## Implementation Summary (v1.1)

### Architecture Implemented:
```
┌─────────────────────────────────────────────────────────┐
│                React Frontend (5173)                   │
│  ┌──────────────────┐  ┌────────────────────────────┐  │
│  │  File Manager    │  │    ChatPanel Component     │  │
│  │  (70% width)     │  │    (30% width)             │  │
│  └──────────────────┘  └────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│              REST API Bridge (8002)                    │
│  /api/chat/init    /api/chat/message    /api/files     │
├─────────────────────────────────────────────────────────┤
│              LangGraph Agents (8000)                   │
│           Planner → Retriever → Analyst               │
└─────────────────────────────────────────────────────────┘
```

### Key Components Implemented:
- **ChatPanel.jsx**: React component with real-time chat interface
- **react_bridge.py**: FastAPI bridge connecting React to LangGraph
- **Split-panel layout**: 70% file manager, 30% chat with toggle
- **Context sharing**: Current folder and selected files passed to AI
- **Session management**: Unique session IDs for conversation tracking

### Services Running:
- React Frontend: http://localhost:5173
- Chat Bridge API: http://localhost:8002 (includes file operations)
- Chainlit Backend: http://localhost:8000 (standalone, optional)

### Features Implemented:
✅ Embedded chat interface in React app
✅ REST API communication (replaced WebSocket for simplicity)
✅ Message history with markdown rendering
✅ File context sharing (current folder, selected files)
✅ Real-time status updates and loading states
✅ Error handling with user-friendly messages
✅ Collapsible chat panel with toggle button
✅ Syntax highlighting for code blocks
✅ Mobile-responsive design
✅ Session-based conversation tracking

## Summary

✅ **COMPLETED**: LabAcc Copilot now features a unified interface combining file management and AI assistance. Users can seamlessly interact with AI agents while managing their experimental data in a single application.

**Version**: 1.1 (Implemented)
**Date**: 2025-08-12
**Status**: ✅ OPERATIONAL