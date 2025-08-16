# Memory System Specification v2.0

**Status**: 🔧 NEEDS REFACTORING (currently broken with pattern matching)  
**Philosophy**: Trust the LLM. No parsing, no patterns, no complex structures.

## The Problem with Current System

The current memory system (`src/memory/readme_memory.py`) is fundamentally broken:

1. **Pattern matching violates core rules** - Looks for English keywords like "**Motivation:**"
2. **Complex structure serves no purpose** - 12 fields, only `raw_content` actually works
3. **Can't read its own output** - Parser expects patterns that don't exist in generated READMEs
4. **Fails silently** - Returns empty structures, falls back to raw content anyway

## The Solution: Simple is Better

### Core Design

```python
class SimpleMemory:
    """Just store the README content as-is"""
    experiment_id: str
    raw_content: str        # The entire README.md file
    file_path: Path        # Where it's stored
    last_modified: datetime # When it changed
```

That's it. No parsing, no sections, no structured fields.

### How It Works

1. **Storage**: Save README as plain markdown text
2. **Retrieval**: Read the file, return the content
3. **Extraction**: When user asks for specific info, use LLM to extract it
4. **Updates**: LLM modifies the markdown directly

### Language-Agnostic Tools

```python
@tool
async def get_experiment_info(experiment_id: str, what_info: str) -> str:
    """
    Get any information from experiment README.
    Works in ANY language - no patterns!
    
    Examples:
    - "What is the overview?"
    - "概要を教えて" (Japanese)
    - "显示结果" (Chinese)
    """
    memory = load_readme(experiment_id)
    
    # Let LLM extract the info
    prompt = f"Extract {what_info} from: {memory.raw_content}"
    return await llm.extract(prompt)

@tool
async def update_experiment(experiment_id: str, updates: str) -> str:
    """
    Update experiment README with new information.
    LLM figures out how to integrate it.
    """
    memory = load_readme(experiment_id)
    
    # Let LLM update the content
    prompt = f"Update this README: {memory.raw_content}\nWith: {updates}"
    new_content = await llm.update(prompt)
    
    memory.save(new_content)
    return "Updated"
```

## Benefits

1. **Works in any language** - Japanese, Chinese, Arabic, etc.
2. **No maintenance** - No patterns to update
3. **Can't break** - Just text storage
4. **Human-editable** - It's just markdown
5. **Git-friendly** - Track changes easily
6. **LLM understands** - Natural language processing

## What Gets Deleted

```bash
# These files are overengineered garbage:
src/memory/readme_memory.py      # Complex parser that doesn't work
src/memory/auto_memory_updater.py # Updates structures that don't exist
src/memory/file_summarizer.py    # Depends on broken parser
```

## What Gets Created

```bash
src/memory/simple_memory.py      # Just stores/loads README text
src/memory/simple_tools.py       # LLM-based extraction tools
```

## Migration Path

1. **No data migration needed** - READMEs stay as-is
2. **Tools get simpler interface** - Same names, simpler implementation
3. **Agent just works better** - No more parsing failures

## Example Usage

**User**: "这个实验的结果如何？" (Chinese: "What are the results of this experiment?")

**Old System**: 
- Looks for "**Results:**" pattern
- Fails because README is in Chinese
- Returns empty

**New System**:
- Passes Chinese question + README to LLM
- LLM understands both Chinese question and content
- Returns accurate results in Chinese

## Implementation Priority

1. **HIGH**: Create `simple_memory.py` with basic storage
2. **HIGH**: Update memory tools to use LLM extraction  
3. **MEDIUM**: Update agent to use new tools
4. **LOW**: Delete old broken files

## Testing

```python
# Test multilingual extraction
japanese_readme = "# 実験\n## 概要\n目的：PCR最適化"
result = await get_experiment_info("test", "概要を教えて")
assert "PCR最適化" in result  # Works!

# Test natural updates
await update_experiment("test", "Add result: 60°C optimal")
# LLM figures out where to put it
```

## Design Principles

1. **No patterns ever** - Violates multi-language principle
2. **Trust the LLM** - It understands context better than regex
3. **Keep it simple** - Complexity without benefit is stupid
4. **Storage ≠ Intelligence** - Store raw, extract smartly

---

**Version**: 2.0  
**Date**: 2025-01-16  
**Philosophy**: "Perfection is achieved when there is nothing left to take away" - Antoine de Saint-Exupéry