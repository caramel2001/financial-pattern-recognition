import abc
from typing import (
    List,
    Dict,
    Tuple,
    Optional,
)
import os
import base64
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

import backoff
import tiktoken
import numpy as np
from openai import OpenAI, AzureOpenAI, APIError, RateLimitError, BadRequestError, APITimeoutError

class LLMProvider(abc.ABC):
    """Interface for LLM models."""

    @abc.abstractmethod
    def create_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        stop_tokens: Optional[List[str]] = None,
    ) -> Tuple[str, Dict[str, int]]:
        """Create a completion from messages in text (and potentially also encoded images)."""
        pass

    @abc.abstractmethod
    def init_provider(self, provider_cfg) -> None:
        """Initialize a provider via a json config."""
        pass

    @abc.abstractmethod
    def assemble_prompt(self, system_prompts: List[str], user_inputs: List[str], image_filenames: List[str]) -> List[str]:
        """Combine parametes in the appropriate way for the provider to use."""
        pass


class LLMOpenAI(LLMProvider):
    """OpenAI LLM provider."""

    client: Any = None
    llm_model: str = ""
    embedding_model: str = ""

    allowed_special: Union[Literal["all"], Set[str]] = set()
    disallowed_special: Union[Literal["all"], Set[str], Sequence[str]] = "all"
    chunk_size: int = 1000
    embedding_ctx_length: int = 8191
    request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    tiktoken_model_name: Optional[str] = None

    """Whether to skip empty strings when embedding or raise an error."""
    skip_empty: bool = False

    def __init__(self, model_name = "gpt-4oturbo",embedding_model_name='text-embedding-large', temperature = 0.0,provider="azure"):
        self.model_name = model_name
        self.temperature = temperature
        self.provider = provider
        if provider == "openai":
            # chech OPENAI_API_KEY in env
            if "OPENAI_API_KEY" not in os.environ:
                raise ValueError("OPENAI_API_KEY environment variable is not set.")
            self.openai_client = OpenAI(model_name=model_name, temperature=temperature)
        elif provider == "azure":
            # check AZURE_OPENAI_API_KEY in env
            if "AZURE_OPENAI_API_KEY" not in os.environ:
                raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set.")
            self.openai_client = AzureOpenAI(model_name=model_name, temperature=temperature)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        self.embedding_model = embedding_model_name
        self.embedding_ctx_length = 8191
        self.chunk_size = 1000
        self.tiktoken_model_name = "cl100k_base"
        self.allowed_special = set()
        self.disallowed_special = "all"
    
        
    def _get_len_safe_embeddings(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        embeddings: List[List[float]] = [[] for _ in range(len(texts))]
        try:
            import tiktoken
        except ImportError:
            raise ImportError(
                "Could not import tiktoken python package. "
                "This is needed in order to for OpenAIEmbeddings. "
                "Please install it with `pip install tiktoken`."
            )

        tokens = []
        indices = []
        model_name = self.tiktoken_model_name or self.embedding_model
        try:
            encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding to count token numbers.")
            model = "cl100k_base"
            encoding = tiktoken.get_encoding(model)
        for i, text in enumerate(texts):
            token = encoding.encode(
                text,
                allowed_special=self.allowed_special,
                disallowed_special=self.disallowed_special,
            )
            for j in range(0, len(token), self.embedding_ctx_length):
                tokens.append(token[j : j + self.embedding_ctx_length])
                indices.append(i)

        batched_embeddings: List[List[float]] = []
        _chunk_size = self.chunk_size
        _iter = range(0, len(tokens), _chunk_size)

        for i in _iter:
            response = self.embed_with_retry(
                input=tokens[i : i + self.chunk_size],
                **self._emb_invocation_params,
            )
            batched_embeddings.extend(r.embedding for r in response.data)

        results: List[List[List[float]]] = [[] for _ in range(len(texts))]
        num_tokens_in_batch: List[List[int]] = [[] for _ in range(len(texts))]
        for i in range(len(indices)):
            if self.skip_empty and len(batched_embeddings[i]) == 1:
                continue
            results[indices[i]].append(batched_embeddings[i])
            num_tokens_in_batch[indices[i]].append(len(tokens[i]))

        for i in range(len(texts)):
            _result = results[i]
            if len(_result) == 0:
                average = self.embed_with_retry(
                    input="",
                    **self._emb_invocation_params,
                ).data[0].embedding
            else:
                average = np.average(_result, axis=0, weights=num_tokens_in_batch[i])
            embeddings[i] = (average / np.linalg.norm(average)).tolist()

        return embeddings