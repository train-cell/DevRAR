# Optional local model analysis

Local analysis is an optional second pass over the normalized evidence already
selected by DevRAR. It runs an installed Ollama executable as a short-lived,
owned child process. It does not use an existing Ollama daemon, download a model,
or execute commands found in transcript evidence.

## Requirements and use

Install Ollama separately and pull a local GGUF model yourself. Choose a model
already listed by the local server, for example one returned by ollama list.
DevRAR does not fetch missing models.

The CLI integration uses:

~~~console
devrar wrap --source claude --analysis local --local-model phi4-mini:latest
~~~

You may select a specific installed executable with --ollama-path <path-to-ollama>.
The model name must be exact and must not identify a cloud model. If Ollama is
missing, the model is not installed locally, its local manifest is not
verifiable, or the server fails, local analysis fails clearly. No report is
silently relabeled as model-analyzed.

## Local boundary

DevRAR chooses an unused port and starts only its own ollama serve child bound
to 127.0.0.1. It sets OLLAMA_NO_CLOUD=1 and OLLAMA_HOST for that child, removes
proxy environment variables, and requires the startup log to confirm that
Ollama cloud is disabled. Requests use direct loopback HTTP, reject redirects,
and enforce bounded timeouts and response size. On every exit path DevRAR
terminates and waits for its own child, then kills it if graceful termination
times out. It does not stop or alter another Ollama server.

Before sending evidence, DevRAR checks /api/tags for one exact installed model,
requires a GGUF manifest with a digest and positive size, then verifies the
model details and local FROM metadata using /api/show. Generation uses
/api/generate with a JSON schema and non-streaming response.

The local Ollama executable is trusted software and may access the network if it
is compromised or ignores its documented environment configuration. DevRAR
does not install or update that executable. Keep Ollama current and install it
from its official distribution.

## Evidence and interpretation

The model receives at most 40 normalized evidence rows, at most 500 characters
each and 20,000 excerpt characters total. Rows are re-redacted before use.
Only IDs, roles, evidence kinds, and excerpts are sent; source paths, locators,
session IDs, Git history, raw files, metrics, and scores are not included.
The model does not return author attribution. DevRAR derives it deterministically
from exact cited roles: user prompts are human-authored; assistant responses and
tool calls are agent-authored; tool results are environment output; mixed or
unrecognized roles are unknown. Unexpected model-authored attribution fields
are rejected.

The model returns at most two proposals in total, with each prose field
limited to 160 characters, at most two citations per proposal, and a 768-token
generation ceiling. Each proposal is a constrained structured output: workflow
dimension, strength/growth polarity, observation, action, alternative
explanation, counterevidence, and exact citations. DevRAR checks that every ID
exists, the derived attribution follows cited roles, the quoted text is an exact
substring of the redacted source, and generated prose is bounded and contains no
digits. Growth is
conditional coaching, not a finding that an omitted practice failed. A failed
schema or citation check fails the local analysis.

The schema is included in both the API `format` argument and the prompt, following
[Ollama's grounding guidance](https://docs.ollama.com/capabilities/structured-outputs).
DevRAR requires one complete JSON object; it never accepts a valid-looking prefix
while discarding trailing model output.

Accepted findings are marked candidate_only with low confidence, fixed
attribution and uncertainty language, plus a human-review note. Model-authored
prose is retained as a hypothesis; exact quotation does not establish that its
interpretation is semantically correct. Prompt wording does not prove execution,
outcome, code quality, skill, or a stable trait. The analysis cannot change
activity metrics, rubric dimensions, numeric grades, score availability, or
human-rater agreement gates. Numerical grades remain unavailable.

Model answers can still be wrong. Review the private report and its citations;
automated redaction is not a guarantee of anonymization.

## Ollama API references

The local adapter follows Ollama's documented local model listing,
model-information, structured generation, and cloud-disable interfaces:

- [List local models (/api/tags)](https://docs.ollama.com/api/tags)
- [Show model details (/api/show)](https://github.com/ollama/ollama/blob/main/docs/api.md#show-model-information)
- [Generate structured output (/api/generate)](https://docs.ollama.com/api/generate)
- [Disable cloud features with OLLAMA_NO_CLOUD=1](https://docs.ollama.com/faq#how-do-i-disable-ollamas-cloud-features)

Ollama documents JSON-schema output through the format field and the
stream=false option for a single response. The cloud-disabled startup log
message is Ollama cloud disabled: true.
