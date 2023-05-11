# SampleFlow Frontend

The vue.js frontend for [circuitseq.iwr.uni-heidelberg.de](https://circuitseq.iwr.uni-heidelberg.de/).

Note: these are development install/use instructions, see
[README_DEV.md](https://github.com/ssciwr/sample_flow/blob/main/README_DEV.md)
for instructions on running the full production docker-compose setup locally.

## Installation

```bash
npm install
```

### Use

```bash
npm run dev
```

### Build

Type-check, compile and minify for production:

```bash
npm run build
```

### Lint

[ESLint](https://eslint.org/) code linting:

```bash
npm run lint
```

### Test

Vitest unit tests:

```bash
npm run npm run test:unit:ci
```

Cypress e2e tests:

```bash
npm run npm run test:e2e
```
