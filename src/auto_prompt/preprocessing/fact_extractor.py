import logging

import dspy
from dspy import Prediction
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic_core import ValidationError

from pericope.dspy_components.metric_components import (
    KeyFactExtraction
)
from pericope.preprocessing.chunker import (
    Chunker,
    RecursiveCharacterChunker,
)

DEFAULT_CHUNK_SIZE = 1000


class FactExtractor:
    def __init__(
            self,
            chunking_strategy: Chunker | None = None,
            extractor: dspy.Module | None = None,
    ):
        """
        A tool to extract facts from a piece of text. To ensure good performance
        on text of any size an in-built chunking mechanism splits the input data
        into shorter pieces of text that are more manageable for the model.

        :param chunking_strategy: Strategy for chunking text into smaller pieces
        :param extractor: DSPy module for extracting facts
        """
        self.extractor = extractor or dspy.Predict(KeyFactExtraction)

        self.chunking_strategy = (
            chunking_strategy
            if chunking_strategy
            else RecursiveCharacterChunker(
                RecursiveCharacterTextSplitter(
                    chunk_size=DEFAULT_CHUNK_SIZE,
                    chunk_overlap=0,
                    length_function=len,
                    separators=[".", ",", "?"],
                )
            )
        )

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        ch = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)


    def extract_facts_with_chunking(
            self,
            text_for_facts: str,
    ) -> list[str]:
        """
        Extracts key facts from text, by first chunking the text,
        then extracting the text pieces.

        :param text_for_facts: The text from which to extract facts
        :return: List of extracted facts
        """
        text_chunks = self.chunking_strategy.chunk_text(text_for_facts)
        all_facts = self.extract_facts_from_chunks(text_chunks)
        return all_facts

    def extract_facts_from_chunks(
            self,
            text_chunks: list[str],
    ) -> list[str]:
        """
        Extracts key facts from given text chunks.

        :param text_chunks: List of text chunks to process
        :return: List of extracted facts
        """
        all_facts = []
        total_not_extracted = 0

        for chunk in text_chunks:
            extracted_facts, did_it_fail = self.extract_molecular_facts(chunk)
            total_not_extracted += did_it_fail
            all_facts.extend(extracted_facts)

        self.logger.info(
            f"TOTAL FAILED EXTRACTIONS: {total_not_extracted}"
        )
        return all_facts

    def forward(self, text: str) -> Prediction:
        """
        Applies the extractor on the passed text.

        :param text: The text to extract facts from
        :return: Prediction object containing extracted facts
        """
        return self.extractor(
            text=text
        )

    def extract_molecular_facts(
            self,
            text: str,
    ) -> tuple[list[str], int]:
        """
        Extracts the molecular facts for the fact checking from the input.

        :param text: The text from which to extract molecular facts
        :return: Tuple containing list of extracted facts and failure count
        """
        try:
            extracted_facts = (
                self.forward(text=text).atomic_facts
            )
            did_it_fail = 0
            self.logger.info(
                f"SUCCESS: Extracted facts from chunk with length {len(text)}"
            )
        except ValidationError as e:
            extracted_facts = []
            did_it_fail = 1
            self.logger.info(
                f"Failed to extract facts from chunk with length {len(text)}: {e}"
            )

        return extracted_facts, did_it_fail