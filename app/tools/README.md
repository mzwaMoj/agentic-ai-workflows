# OpenAI Tool Definitions Guide

This guide explains how OpenAI tools are defined, comparing the newer approach (introduced in 2023-2024) with the older function calling approach.

## New Tool Definitions (Current Approach)

The current approach to defining tools uses the `tools` parameter with the `responses.create` endpoint. This method provides a more standardized way to define tools as external functions that the model can call.

```python
from openai import OpenAI

client = OpenAI()

tools = [{
    "type": "function",
    "name": "get_weather",
    "description": "Get current temperature for a given location.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City and country e.g. Bogotá, Colombia"
            }
        },
        "required": [
            "location"
        ],
        "additionalProperties": False
    }
}]

response = client.responses.create(
    model="gpt-4.1",
    input=[{"role": "user", "content": "What is the weather like in Paris today?"}],
    tools=tools
)

print(response.output)
```

### Key Features of New Tool Definitions:

- Uses the `responses.create` endpoint
- Tools are defined with a standardized schema including a `type` field
- Supports multiple tool types (currently "function")
- Tool responses are handled via the `output` property
- Compatible with newer models like GPT-4.1
- Tools are passed directly in the API call as a list of tool definitions
- The response format is more structured and consistent

## Older Tool Definitions (Function Calling)

The older approach to tool definition used the `functions` parameter with the `chat.completions.create` endpoint. This was the initial implementation of function calling in OpenAI models.

```python
from openai import OpenAI
import json

client = OpenAI()

functions = [
    {
        "name": "get_weather",
        "description": "Get current temperature for a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and country e.g. Bogotá, Colombia"
                }
            },
            "required": ["location"]
        }
    }
]

response = client.chat.completions.create(
    model="gpt-3.5-turbo-0613",
    messages=[{"role": "user", "content": "What is the weather like in Paris today?"}],
    functions=functions,
    function_call="auto"  # auto is default, but we'll be explicit
)

# Extract the function call
function_call = response.choices[0].message.function_call
if function_call:
    function_name = function_call.name
    function_args = json.loads(function_call.arguments)
    
    # In a real implementation, you would call your actual function here
    # weather_data = get_weather(function_args["location"])
    
    # Then continue the conversation with the function results
    second_response = client.chat.completions.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "user", "content": "What is the weather like in Paris today?"},
            {"role": "assistant", "content": None, "function_call": {
                "name": "get_weather", 
                "arguments": json.dumps(function_args)
            }},
            {"role": "function", "name": "get_weather", "content": json.dumps({"temperature": "22", "unit": "celsius"})}
        ]
    )
    
    print(second_response.choices[0].message.content)
```

### Key Features of Older Function Calling:

- Uses the `chat.completions.create` endpoint
- Functions are defined without a `type` field
- Manual handling of function calls and responses is required
- The response processing involves multiple steps and potentially multiple API calls
- First introduced with models like GPT-3.5-turbo-0613 and GPT-4-0613

## Comparison Between Old and New Approaches

| Feature | Old Approach (Function Calling) | New Approach (Tools) |
|---------|--------------------------------|---------------------|
| API Endpoint | `chat.completions.create` | `responses.create` |
| Parameter Name | `functions` | `tools` |
| Schema | No `type` field | Includes `type` field (e.g., "function") |
| Response Handling | Manual extraction from response object | Direct access via `response.output` |
| Flow Control | Multiple API calls for function execution | Streamlined single call |
| Complexity | More verbose, requires manual response handling | Simplified, more declarative |
| First Available | GPT-3.5-turbo-0613, GPT-4-0613 | GPT-4.1 and newer models |
| Multiple Tool Types | Limited to functions | Designed for expansion to more tool types |
| Error Handling | Manual | More standardized |

## When to Use Each Approach

### Use the New Tools Approach When:
- Working with the latest models (GPT-4.1+)
- You need a simpler, more streamlined implementation
- You want to future-proof your code
- You want cleaner response handling

### Use the Older Function Calling Approach When:
- Working with older models that don't support the new tools parameter
- You have existing code that uses function calling and don't want to refactor
- You need specific control over the conversation flow with functions

## Implementation Best Practices

1. **Tool Descriptions**:
   - Write clear, concise descriptions
   - Be specific about what the tool does
   - Explain required input formats

2. **Parameter Definitions**:
   - Use descriptive names
   - Include detailed descriptions for each parameter
   - Specify required vs optional parameters
   - Use the appropriate JSON Schema types

3. **Error Handling**:
   - Implement robust error handling for tool execution
   - Validate inputs before processing
   - Provide helpful error messages

4. **Response Processing**:
   - Parse tool outputs carefully
   - Handle cases where the model might not use your tools
   - Consider rate limits and token usage

## Further Resources

- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [OpenAI Cookbook: Function Calling Examples](https://cookbook.openai.com/examples/how_to_call_functions_with_chat_models)
- [JSON Schema Documentation](https://json-schema.org/learn/getting-started-step-by-step)