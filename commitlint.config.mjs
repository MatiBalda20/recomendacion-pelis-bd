// Reglas de commits del proyecto (ver README, "Convenciones de commits").
const PATRONES_IA = [
  /^co-authored-by:.*\b(claude|anthropic|copilot|chatgpt|openai|gpt|gemini|cursor|codeium|tabnine|devin|ai)\b/im,
  /generated with/i,
];

export default {
  extends: ['@commitlint/config-conventional'],
  plugins: [
    {
      rules: {
        'sin-autoria-ia': ({ raw }) => {
          const encontrado = PATRONES_IA.find((patron) => patron.test(raw ?? ''));
          return [
            !encontrado,
            'el mensaje no puede nombrar a un asistente de IA como coautor ni incluir "Generated with"',
          ];
        },
      },
    },
  ],
  rules: {
    'header-max-length': [2, 'always', 72],
    'subject-full-stop': [2, 'never', '.'],
    'scope-enum': [1, 'always', ['api', 'front', 'carga', 'db', 'modelo']],
    'sin-autoria-ia': [2, 'always'],
  },
};
