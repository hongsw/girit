
# Girit CLI

Girit is a command-line tool that leverages OpenAI's GPT to convert natural language instructions into executable Git commands by analyzing your current repository state.

## Features

- **Repository Analysis:** Automatically gathers Git status, diffs, remotes, and recent commits.
- **Natural Language Interface:** Translates user-provided descriptions into Git commands.
- **Interactive Mode:** Prompts for user selection when multiple command options are available.
- **CLI Packaging:** Installable via pip for easy integration and use as a CLI tool.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd girit
   ```

2. **Install the package:**
   ```bash
   pip install .
   ```

## Configuration

- **OpenAI API Key:**  
  Girit requires an OpenAI API key to function. Set it in your environment:
  ```bash
  export OPENAI_API_KEY=your_api_key_here
  ```

## Usage

Simply run the CLI tool:
```bash
girit
```
Follow the prompt to input your Git command description. Girit will analyze your repository and execute the appropriate Git commands based on your input.

## Contributing

Contributions are welcome! Please open issues or submit pull requests on GitHub.

## License

This project is licensed under the MIT License.
