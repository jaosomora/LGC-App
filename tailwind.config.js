module.exports = {
  content: [
    './templates/**/*.html', // Todas las plantillas Jinja
    './static/**/*.js', // Archivos JS dentro de la carpeta estática
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4A90E2',
        secondary: '#50B5E9',
        accent: '#25567B',
        light: '#F5F8FB',
        green: {
          500: '#22c55e',
          600: '#15803d',
        },
        blue: {
          500: '#3b82f6',
          600: '#2563eb',
        },
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          900: '#111827',
        },
      },
      fontFamily: {
        sans: ['Poppins', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      },
      animation: {
        pulse: 'pulse 1.5s infinite',
      },
      keyframes: {
        pulse: {
          '0%, 100%': { transform: 'scale(1)', boxShadow: '0 0 8px rgba(255, 223, 0, 0.7)' },
          '50%': { transform: 'scale(1.2)', boxShadow: '0 0 16px rgba(255, 223, 0, 1)' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/aspect-ratio'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};