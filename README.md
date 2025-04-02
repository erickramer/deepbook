# DeepBook - Children's Storybook Generator

DeepBook is an AI-powered children's storybook generator that creates complete, illustrated books from simple prompts.

## Features

- Create custom children's books with a simple text prompt
- Generate story elements including:
  - Book title and author
  - Character descriptions with AI-generated illustrations
  - Chapter outlines
  - Full story text

## How It Works

1. Enter your OpenAI API key
2. Enter a prompt describing the story you want to create
3. DeepBook sequentially generates all story elements:
   - Metadata (title, author, themes)
   - Characters with personalities and descriptions
   - Character illustrations using DALL-E
   - Story outline with chapter structure
   - Full text content for each chapter
4. All elements are presented in a reader-friendly format

## Technology Stack

- **Streamlit**: Web interface
- **OpenAI**: GPT models for text generation and DALL-E for illustrations
- **LangChain**: Structured interactions with language models
- **Pydantic**: Data validation and structural typing for story components

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/deepbook.git
cd deepbook

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
make run
```

## Usage

1. Open the application in your browser (typically at http://localhost:8501)
2. Enter your OpenAI API key in the first text box
3. Enter a prompt for your children's book (e.g., "A story about a brave turtle who helps his forest friends")
4. Wait for the generation process to complete
5. Enjoy your custom children's book!

## Project Structure

- `app/__init__.py`: Main application and UI layout
- `app/models.py`: Data models for story components
- `app/prompts.py`: Templates for story generation
- `app/contants.py`: Configuration settings
- `tests/`: Test suite for the application

## Testing

The project includes a comprehensive test suite to ensure functionality and reliability:

```bash
# Run all tests
make test

# Run tests with coverage report
make coverage

# Run linting checks
make lint

# Auto-format code
make format
```

See the [tests/README.md](tests/README.md) file for more information about the test suite.

### Continuous Integration

This project uses GitHub Actions for continuous integration. The following checks are run on every push and pull request:

- Code linting with flake8, black, and isort
- Unit tests with pytest
- Test coverage reporting with pytest-cov and CodeCov

## Notes

- You need to provide your own OpenAI API key
- The generation process may take a few minutes depending on the length and complexity of the story
- This project uses the gpt-4o-2024-08-06 model by default