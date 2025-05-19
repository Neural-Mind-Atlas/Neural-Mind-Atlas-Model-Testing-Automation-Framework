# src/main.py
import os
import sys
import argparse
import yaml
import logging
from src.utils.config import load_config
from src.test_runner.executor import TestExecutor
from src.reporting.yaml_generator import YAMLReporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_run.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def get_available_models():
    """Load available models from configuration files"""
    models = {}
    model_dir = os.path.join("config", "models")
    if not os.path.exists(model_dir):
        model_dir = os.path.join("config")  # Fallback to main config directory

    for file_name in os.listdir(model_dir):
        if file_name.endswith('.yaml'):
            file_path = os.path.join(model_dir, file_name)
            try:
                # Determine provider from filename
                provider = file_name.replace('.yaml', '').lower()

                with open(file_path, 'r') as file:
                    model_config = yaml.safe_load(file)
                    if model_config and 'models' in model_config:
                        # Handle list-style model configurations
                        if isinstance(model_config['models'], list):
                            for model in model_config['models']:
                                if 'name' in model:
                                    model_id = model['name']
                                    # Add provider if not present
                                    if 'provider' not in model:
                                        if provider == 'others':
                                            # For others.yaml, try to determine provider from name
                                            if 'cohere' in model_id:
                                                model['provider'] = 'cohere'
                                            elif 'dbrx' in model_id or 'databricks' in model_id:
                                                model['provider'] = 'databricks'
                                            elif 'qwen' in model_id:
                                                model['provider'] = 'qwen'
                                            elif 'falcon' in model_id:
                                                model['provider'] = 'falcon'
                                            else:
                                                model['provider'] = 'unknown'
                                        else:
                                            model['provider'] = provider
                                    models[model_id] = model
                        # Handle dictionary-style model configurations
                        elif isinstance(model_config['models'], dict):
                            for model_id, model in model_config['models'].items():
                                # Add provider if not present
                                if 'provider' not in model:
                                    if provider == 'others':
                                        # For others.yaml, try to determine provider from name
                                        if 'cohere' in model_id:
                                            model['provider'] = 'cohere'
                                        elif 'dbrx' in model_id or 'databricks' in model_id:
                                            model['provider'] = 'databricks'
                                        elif 'qwen' in model_id:
                                            model['provider'] = 'qwen'
                                        elif 'falcon' in model_id:
                                            model['provider'] = 'falcon'
                                        else:
                                            model['provider'] = 'unknown'
                                    else:
                                        model['provider'] = provider
                                models[model_id] = model
            except Exception as e:
                logger.error(f"Error loading model config file {file_path}: {e}")

    return models

def main():
    parser = argparse.ArgumentParser(description="LLM Testing Framework")
    parser.add_argument('--model', type=str, help='Specific model to test')
    parser.add_argument('--models', type=str, help='Comma-separated list of models to test')
    parser.add_argument('--all-models', action='store_true', help='Test all available models')
    parser.add_argument('--test', type=str, default='ppt_generation',
                        help='Test category to run (default: ppt_generation)')
    parser.add_argument('--context', type=str, default='short',
                        choices=['short', 'medium', 'long'],
                        help='Context length for testing')
    parser.add_argument('--output', type=str, default='console',
                        choices=['console', 'json', 'yaml', 'html'],
                        help='Output format for results')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load available models
    available_models = get_available_models()
    if not available_models:
        logger.error("No models found in configuration files.")
        return

    logger.info(f"Found {len(available_models)} models in configuration")

    # Determine which models to test
    models_to_test = []
    if args.all_models:
        models_to_test = list(available_models.keys())
    elif args.models:
        models_to_test = [model.strip() for model in args.models.split(',')]
    elif args.model:
        models_to_test = [args.model]
    else:
        logger.error("No model specified. Use --model, --models, or --all-models")
        return

    # Validate models
    valid_models = []
    for model_id in models_to_test:
        if model_id in available_models:
            valid_models.append(model_id)
        else:
            logger.warning(f"Model {model_id} not found in configuration")

    if not valid_models:
        logger.error("No valid models to test")
        return

    logger.info(f"Testing {len(valid_models)} models: {', '.join(valid_models)}")

    # Create test executor
    executor = TestExecutor()

    # Run tests for each model
    results = {}
    for model_id in valid_models:
        logger.info(f"Testing model: {model_id}")
        try:
            model_config = available_models[model_id]
            test_result = executor.run_test(
                model_id=model_id,
                model_config=model_config,
                test_category=args.test,
                context_length=args.context
            )
            results[model_id] = test_result
            logger.info(f"Testing completed for {model_id}")
        except Exception as e:
            logger.error(f"Error testing model {model_id}: {e}")

    # Generate reports
    output_dir = os.path.join("results", args.test)
    os.makedirs(output_dir, exist_ok=True)

    # Choose reporter based on output format
    if args.output == 'yaml':
        reporter = YAMLReporter()
        output_file = os.path.join(output_dir, f"test_results_{args.context}.yaml")
        reporter.generate_report(results, output_file)
        logger.info(f"Results saved to {output_file}")
    elif args.output == 'json':
        from src.reporting.json_generator import JSONReporter
        reporter = JSONReporter()
        output_file = os.path.join(output_dir, f"test_results_{args.context}.json")
        reporter.generate_report(results, output_file)
        logger.info(f"Results saved to {output_file}")
    elif args.output == 'html':
        from src.reporting.html_generator import HTMLReporter
        reporter = HTMLReporter()
        output_file = os.path.join(output_dir, f"test_results_{args.context}.html")
        reporter.generate_report(results, output_file)
        logger.info(f"Results saved to {output_file}")
    else:
        # Console output
        for model_id, result in results.items():
            print(f"\n=== Results for {model_id} ===")
            print(f"Overall score: {result.get('overall_score', 'N/A')}")
            for metric, score in result.get('metrics', {}).items():
                print(f"  {metric}: {score}")

    logger.info("Testing completed successfully")

if __name__ == "__main__":
    main()