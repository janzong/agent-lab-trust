# Method Notes

## Scope

Read-only normalization of synthetic GenMentor archive artifacts. This package is deliberately small and runs without network access.

## Invariants

- source artifacts are read-only;
- malformed archives raise explicit parse errors;
- no prompt, response, credential, or private run is included;
- synthetic fixtures are the only data shipped here.

## Limitations

Coverage, learner evidence, and model quality are outside this package.
