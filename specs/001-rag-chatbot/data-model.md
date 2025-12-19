# Data Model: RAG Chatbot for Physical AI & Humanoid Robotics Documentation

## Entities

### DocumentChunk
- **id**: string (unique identifier)
- **content**: string (text content of the document chunk)
- **metadata**: object
  - relative_path: string (path to source document)
  - title: string (document title)
  - section: string (document section, if applicable)
- **embedding**: array<float> (vector representation of content)
- **created_at**: datetime (timestamp of creation)

### Query
- **id**: string (unique identifier)
- **content**: string (user's question/query)
- **timestamp**: datetime (when query was made)
- **user_id**: string (optional, for tracking purposes)

### Response
- **id**: string (unique identifier)
- **query_id**: string (reference to related query)
- **content**: string (generated response text)
- **sources**: array<object>
  - document_id: string (reference to document chunk)
  - relative_path: string (path to source document)
  - score: float (relevance score)
  - content_preview: string (preview of source content)
- **timestamp**: datetime (when response was generated)

### Session
- **id**: string (unique identifier)
- **user_id**: string (user identifier)
- **created_at**: datetime (session start time)
- **last_activity**: datetime (last interaction time)
- **conversation_history**: array<object>
  - role: string (user or assistant)
  - content: string (message content)
  - timestamp: datetime (message timestamp)

## Relationships

- **Session** contains many **Query** objects (one-to-many)
- **Query** connects to one **Response** (one-to-one)
- **Response** references many **DocumentChunk** objects through sources (many-to-many via junction)

## Validation Rules

### DocumentChunk
- content must not be empty
- embedding must have consistent dimension (1024 for Cohere multilingual model)
- metadata.relative_path must be a valid path reference

### Query
- content must not be empty
- content must be less than 1000 characters
- timestamp must be current or past

### Response
- content must not be empty
- sources array must contain at least one source for non-error responses
- each source must have a valid document reference and score between 0 and 1

### Session
- conversation_history must not exceed 50 messages
- last_activity must be updated on each interaction
- session must expire after 24 hours of inactivity

## State Transitions

### Query Processing
- NEW → EMBEDDING (query received, embedding in progress)
- EMBEDDING → SEARCHING (embedding complete, searching for relevant documents)
- SEARCHING → GENERATING (relevant documents found, response being generated)
- GENERATING → COMPLETE (response generated and returned to user)
- *_ERROR → ERROR (any step failed, error response returned)