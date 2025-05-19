import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.evaluators.base_evaluator import BaseEvaluator
from src.evaluators.accuracy_evaluator import AccuracyEvaluator
from src.evaluators.hallucination_evaluator import HallucinationEvaluator
from src.evaluators.efficiency_evaluator import EfficiencyEvaluator
from src.evaluators.context_evaluator import ContextEvaluator
from src.evaluators.instruction_evaluator import InstructionEvaluator
from src.evaluators.reasoning_evaluator import ReasoningEvaluator
from src.evaluators.prompt_quality_evaluator import PromptQualityEvaluator


class TestBaseEvaluator(unittest.TestCase):
    def test_initialization(self):
        evaluator = BaseEvaluator()
        self.assertEqual(evaluator.name, "base_evaluator")

    def test_evaluate_not_implemented(self):
        evaluator = BaseEvaluator()
        with self.assertRaises(NotImplementedError):
            evaluator.evaluate("test_input", "test_output", "test_ground_truth", {})


class TestAccuracyEvaluator(unittest.TestCase):
    def test_initialization(self):
        evaluator = AccuracyEvaluator()
        self.assertEqual(evaluator.name, "accuracy")

    def test_evaluate_with_high_similarity(self):
        evaluator = AccuracyEvaluator()
        model_response = "The capital of France is Paris"
        ground_truth = "Paris is the capital of France"
        score = evaluator.evaluate("", model_response, ground_truth, {})
        self.assertGreater(score, 0.7)

    def test_evaluate_with_low_similarity(self):
        evaluator = AccuracyEvaluator()
        model_response = "The capital of Spain is Madrid"
        ground_truth = "Paris is the capital of France"
        score = evaluator.evaluate("", model_response, ground_truth, {})
        self.assertLess(score, 0.5)


class TestHallucinationEvaluator(unittest.TestCase):
    def test_initialization(self):
        evaluator = HallucinationEvaluator()
        self.assertEqual(evaluator.name, "hallucination")

    def test_evaluate_with_no_hallucination(self):
        evaluator = HallucinationEvaluator()
        input_text = "Tell me about Paris"
        model_response = "Paris is the capital of France"
        ground_truth = "Paris is the capital and most populous city of France"
        score = evaluator.evaluate(input_text, model_response, ground_truth, {})
        self.assertGreater(score, 0.7)

    def test_evaluate_with_hallucination(self):
        evaluator = HallucinationEvaluator()
        input_text = "Tell me about Paris"
        model_response = "Paris is the capital of Italy and has a population of 30 million"
        ground_truth = "Paris is the capital and most populous city of France"
        score = evaluator.evaluate(input_text, model_response, ground_truth, {})
        self.assertLess(score, 0.5)


class TestEfficiencyEvaluator(unittest.TestCase):
    def test_initialization(self):
        evaluator = EfficiencyEvaluator()
        self.assertEqual(evaluator.name, "efficiency")

    @patch('src.evaluators.efficiency_evaluator.tiktoken.encoding_for_model')
    def test_evaluate_token_efficiency(self, mock_encoding):
        mock_encoder = MagicMock()
        mock_encoder.encode.side_effect = lambda x: [1] * len(x.split())  # One token per word
        mock_encoding.return_value = mock_encoder

        evaluator = EfficiencyEvaluator()
        prompt = "Create a presentation about climate change"
        response = "This is a concise response about climate change"
        score = evaluator.evaluate(prompt, response, "", {"model": "gpt-4"})
        
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)


class TestContextEvaluator(unittest.TestCase):
    def test_initialization(self):
        evaluator = ContextEvaluator()
        self.assertEqual(evaluator.name, "context")

    def test_evaluate_high_context_utilization(self):
        evaluator = ContextEvaluator()
        context = "Climate change is causing rising sea levels and extreme weather events"
        response = "The presentation covers the impact of climate change, including rising sea levels and extreme weather patterns"
        score = evaluator.evaluate(context, response, "", {})
        self.assertGreater(score, 0.7)

    def test_evaluate_low_context_utilization(self):
        evaluator = ContextEvaluator()
        context = "Climate change is causing rising sea levels and extreme weather events"
        response = "This presentation is about environmental topics"
        score = evaluator.evaluate(context, response, "", {})
        self.assertLess(score, 0.5)


class TestInstructionEvaluator(unittest.TestCase):
    def test_initialization(self):
        evaluator = InstructionEvaluator()
        self.assertEqual(evaluator.name, "instruction")

    def test_evaluate_follows_instructions(self):
        evaluator = InstructionEvaluator()
        instruction = "Create a 5-slide presentation about climate change with bullet points"
        response = """
        # Climate Change Presentation
        ## Slide 1: Introduction
        - Definition of climate change
        - Global significance
        ## Slide 2: Causes
        - Human activities
        - Greenhouse gases
        ## Slide 3: Effects
        - Rising temperatures
        - Extreme weather
        ## Slide 4: Mitigation
        - Renewable energy
        - Policy changes
        ## Slide 5: Conclusion
        - Summary
        - Call to action
        """
        score = evaluator.evaluate(instruction, response, "", {})
        self.assertGreater(score, 0.8)


class TestReasoningEvaluator(unittest.TestCase):
    def test_initialization(self):
        evaluator = ReasoningEvaluator()
        self.assertEqual(evaluator.name, "reasoning")

    def test_evaluate_good_reasoning(self):
        evaluator = ReasoningEvaluator()
        prompt = "Explain the greenhouse effect and why it's important"
        response = """
        The greenhouse effect is a natural process where certain gases in Earth's atmosphere (like CO2) trap heat from the sun.
        This process is crucial because:
        1. It maintains Earth's temperature at a livable level
        2. Without it, Earth would be too cold to support life as we know it
        3. However, human activities have enhanced this effect, leading to global warming
        The careful balance of greenhouse gases is important for maintaining Earth's climate stability.
        """
        score = evaluator.evaluate(prompt, response, "", {})
        self.assertGreater(score, 0.7)


class TestPromptQualityEvaluator(unittest.TestCase):
    def test_initialization(self):
        evaluator = PromptQualityEvaluator()
        self.assertEqual(evaluator.name, "prompt_quality")

    def test_evaluate_good_prompt(self):
        evaluator = PromptQualityEvaluator()
        meta_prompt = "Create a prompt for generating an engaging climate change presentation"
        generated_prompt = """
        Create a visually engaging 10-slide presentation on climate change that includes:
        1. An attention-grabbing title slide with a compelling statistic
        2. Clear definition of climate change with current scientific consensus
        3. Visual representation of key climate data from the last century
        4. Slide showing major causes of climate change with percentages
        5. Slide detailing 3-5 most significant impacts on ecosystems
        6. Economic impacts section with cost projections
        7. Solutions slide categorized by individual, community, and global actions
        8. Case studies of successful climate initiatives
        9. Future scenarios slide (both action and inaction paths)
        10. Call-to-action conclusion with specific, actionable steps
        
        Use bullet points for clarity, include suggested visual elements for each slide, and ensure content is factually accurate and backed by recent scientific consensus.
        """
        score = evaluator.evaluate(meta_prompt, generated_prompt, "", {})
        self.assertGreater(score, 0.7)


if __name__ == '__main__':
    unittest.main()