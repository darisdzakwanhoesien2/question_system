# Exam Prep AI

An AI-powered exam preparation system built with Streamlit that supports multiple exam types, question formats, and provides intelligent grading and feedback.

## Features

- **Multiple Exam Types**: Support for SAT, GRE, and TOEFL exams
- **Question Types**: Multiple Choice Questions (MCQ), Short Answer, and Essay questions
- **AI-Powered Grading**: Automated grading using Large Language Models
- **Real-time Feedback**: Instant feedback and explanations for answers
- **Performance Analytics**: Detailed analytics and progress tracking
- **Learning Recommendations**: Personalized study recommendations
- **Session Management**: Persistent exam sessions with timer support

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd exam-prep-ai
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure LLM providers in `config/llm_config.yaml`

4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Project Structure

```
exam-prep-ai/
├── app.py                 # Main Streamlit application
├── pages/                 # Streamlit pages
├── core/                  # Core business logic
├── components/            # Reusable UI components
├── services/              # Service layer (LLM, grading, analytics)
├── prompts/               # LLM prompt templates
├── datasets/              # Exam question datasets
├── schemas/               # Data models and validation
├── storage/               # Data storage directories
├── config/                # Configuration files
├── utils/                 # Utility functions
└── notebooks/             # Analysis notebooks
```

## Configuration

### LLM Configuration

Edit `config/llm_config.yaml` to configure LLM providers:

```yaml
providers:
  ollama:
    base_url: "http://localhost:11434"
    model: "llama2"
  lmstudio:
    base_url: "http://localhost:1234"
    model: "local-model"
  openrouter:
    api_key: "your-api-key"
    model: "anthropic/claude-3"
```

### Exam Configuration

Edit `config/exam_config.yaml` for exam settings.

## Usage

1. **Select Exam**: Choose from available exam types and sets
2. **Take Exam**: Answer questions with timer support
3. **Review Answers**: Check correct answers and explanations
4. **View Analytics**: Analyze performance and progress
5. **Get Feedback**: Receive AI-powered feedback and recommendations

## Development

The application uses:
- **Streamlit** for the web interface
- **Pydantic** for data validation
- **OpenAI/ Anthropic APIs** for LLM services
- **Pandas/Plotly** for data analysis and visualization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test
4. Submit a pull request

## License

MIT License