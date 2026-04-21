# Spec-Driven Development (SDD) — GenAI Study Project

Metodologia AIOX adaptada para Python. Toda feature nova começa aqui, não no código.

## Por que SDD?

Em projetos de IA generativa, o "o que" (contrato de entrada/saída) é tão importante quanto o "como" (implementação). SDD força clareza antes de código: você define o schema, os critérios e os exemplos primeiro — o LLM e o código são consequência.

## Workflow em 5 Passos

```
1. @analyst  →  Pesquisa (contexto, papers, libs disponíveis)
2. @pm       →  PRD (objetivo, user stories, critérios de aceite)
3. @architect →  Architecture Doc (diagrama, classes, decisões de design)
4. @sm       →  Stories (tasks atômicas com critérios verificáveis)
5. @dev + @qa → Implementação + Testes (seguindo stories)
```

## Estrutura de Artefatos

```
docs/sdd/
├── README.md                   ← este arquivo
└── <módulo>/
    ├── prd.md                  ← o quê e por quê
    ├── architecture.md         ← como (design técnico)
    └── stories/
        ├── 01_<feature>.md     ← tasks atômicas
        └── ...
```

## Módulos com SDD

| Módulo | Status | PRD | Arch | Stories |
|--------|--------|-----|------|---------|
| [structured_output](structured_output/) | ✅ Spec completa | [prd](structured_output/prd.md) | [arch](structured_output/architecture.md) | [4 stories](structured_output/stories/) |

## Regras

1. **Spec antes de código** — nenhum arquivo `.py` sem story correspondente
2. **Checkboxes** — marque `[x]` ao completar cada task
3. **Critérios primeiro** — os testes derivam diretamente dos acceptance criteria
4. **Sem escopo-creep** — implemente apenas o que a story especifica; abra nova story para extensões
