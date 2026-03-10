module.exports = {
  content: [
    './templates/**/*.html',
    './static/**/*.js',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        'th-bg':      'rgb(var(--c-bg) / <alpha-value>)',
        'th-surface': 'rgb(var(--c-surface) / <alpha-value>)',
        'th-text':    'rgb(var(--c-text) / <alpha-value>)',
        'th-accent':  'rgb(var(--c-accent) / <alpha-value>)',
        'th-muted':   'rgb(var(--c-muted) / <alpha-value>)',
        'th-error':   'rgb(var(--c-error) / <alpha-value>)',
      },
      animation: {
        'float-slow': 'float 20s ease-in-out infinite',
        'float-slower': 'float 25s ease-in-out infinite reverse',
        'float-medium': 'float 15s ease-in-out infinite',
        'fade-in': 'fadeIn 0.3s ease-out',
        'pulse-glow': 'pulseGlow 1.5s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translate(0, 0)' },
          '33%': { transform: 'translate(30px, -30px)' },
          '66%': { transform: 'translate(-20px, 20px)' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 8px var(--glow-lo)' },
          '50%': { boxShadow: '0 0 20px var(--glow-hi)' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
};
