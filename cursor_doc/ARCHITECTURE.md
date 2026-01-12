# System Architecture

## Overview

The Instagram Reels AI Creator is a multi-agent workflow system that automates the creation of Instagram Reels using AI. The system uses LangGraph for orchestration and integrates with multiple AI services.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
│  ┌──────────────┐              ┌──────────────┐            │
│  │  Streamlit   │              │     CLI      │            │
│  │     UI       │              │  Interface   │            │
│  └──────┬───────┘              └──────┬───────┘            │
└─────────┼──────────────────────────────┼────────────────────┘
          │                              │
          └──────────────┬───────────────┘
                         │
          ┌──────────────▼──────────────┐
          │   ReelsWorkflow Orchestrator │
          │      (LangGraph StateGraph)  │
          └──────────────┬───────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │               │
    ┌─────▼─────┐  ┌────▼─────┐  ┌─────▼─────┐
    │  Agent A  │  │ Agent B  │  │ Agent C  │
    │ Concept   │  │Script    │  │  Media   │
    │Strategist │  │Writer    │  │ Generator│
    └─────┬─────┘  └────┬─────┘  └─────┬─────┘
          │             │              │
          │             │              │
    ┌─────▼─────────────▼──────────────▼─────┐
    │         Agent D: Video Assembler        │
    └───────────────────┬────────────────────┘
                        │
          ┌─────────────┼─────────────┐
          │             │             │
    ┌─────▼─────┐ ┌────▼─────┐ ┌────▼─────┐
    │  OpenAI   │ │ElevenLabs│ │Replicate │
    │   API     │ │   API    │ │   API    │
    └───────────┘ └──────────┘ └──────────┘
```

## Components

### 1. Orchestrator Layer

**ReelsWorkflow** (`orchestrator/workflow.py`)
- Manages the overall workflow using LangGraph
- Coordinates between agents
- Handles state transitions
- Manages error recovery

**StateManager** (`orchestrator/state_manager.py`)
- Persists workflow state at each step
- Allows resuming interrupted workflows
- Stores all intermediate outputs

### 2. Agent Layer

#### Agent A: Concept Strategist
- **File**: `agents/concept_strategist.py`
- **Purpose**: Generates 3 distinct, high-engagement Reel concepts
- **Input**: Niche/keywords
- **Output**: 3 ReelConcept objects with hooks, value propositions, visual styles
- **API**: OpenAI GPT-4

#### Agent B: Scriptwriter
- **File**: `agents/scriptwriter.py`
- **Purpose**: Creates optimized scripts and image generation prompts
- **Input**: Selected concept
- **Output**: ReelScript with transcript and sequential image prompts
- **API**: OpenAI GPT-4

#### Agent C: Media Generator
- **File**: `agents/media_generator.py`
- **Purpose**: Generates high-quality images from prompts
- **Input**: Image prompts from Agent B
- **Output**: Image files
- **API**: OpenAI DALL-E 3 or Replicate

#### Agent D: Video Assembler
- **File**: `agents/video_assembler.py`
- **Purpose**: Creates voiceover and assembles final video
- **Input**: Transcript and images
- **Output**: Final video file
- **APIs**: ElevenLabs (TTS), MoviePy (video assembly)

### 3. Utility Layer

**API Clients** (`utils/api_clients.py`)
- `OpenAIClient`: Text generation and image generation
- `ElevenLabsClient`: Text-to-speech
- `ReplicateClient`: Alternative image generation
- All include rate limiting and retry logic

**Rate Limiter** (`utils/rate_limiter.py`)
- Thread-safe rate limiting
- Configurable limits per API
- Prevents API quota exhaustion

**Video Processor** (`utils/video_utils.py`)
- Video assembly using MoviePy
- Image-to-video conversion
- Audio synchronization
- Instagram Reels format optimization

## Workflow States

The system progresses through these states:

1. **concept_generation**: Generating initial concepts
2. **concept_selection**: Waiting for user to select a concept
3. **script_generation**: Creating script and image prompts
4. **image_generation**: Generating images from prompts
5. **video_assembly**: Creating voiceover and assembling video
6. **completed**: Workflow finished successfully
7. **failed**: Error occurred (can be retried)

## Data Flow

```
User Input (niche/keywords)
    ↓
Agent A: Generate 3 concepts
    ↓
User Selection
    ↓
Agent B: Generate script + image prompts
    ↓
Agent C: Generate images (parallel)
    ↓
Agent D: Generate voiceover
    ↓
Agent D: Assemble video
    ↓
Final Video Output
```

## State Persistence

State is saved at each step:
- After concept generation
- After script generation
- After image generation
- After video assembly

This allows:
- Resuming interrupted workflows
- Reviewing intermediate outputs
- Refining specific stages

## Error Handling

- **Retry Logic**: Automatic retries with exponential backoff
- **Rate Limiting**: Prevents API quota exhaustion
- **State Recovery**: Can resume from last successful step
- **Error Messages**: Detailed error information for debugging

## Scalability Considerations

- **Async Processing**: All API calls are asynchronous
- **Concurrent Image Generation**: Images generated in parallel
- **Rate Limiting**: Prevents overwhelming APIs
- **State Management**: Efficient state storage and retrieval

## Extensibility

The system is designed to be easily extended:

- **New Agents**: Add new agent classes following the existing pattern
- **New APIs**: Add new API clients in `utils/api_clients.py`
- **New Workflow Steps**: Add nodes to the LangGraph workflow
- **Custom Processing**: Extend video/audio processing utilities
