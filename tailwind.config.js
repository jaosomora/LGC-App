module.exports = {
  content: [
    './templates/**/*.html', // Plantillas Jinja
    './static/**/*.js', // JS en la carpeta estática
  ],
  darkMode: 'class', // Permite activar el modo oscuro con 'class'
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#4A90E2',
          50: '#EBF5FF',
          100: '#CCE4FF',
          200: '#99CAFF',
          300: '#66B0FF',
          400: '#3396FF',
          500: '#4A90E2',
          600: '#2563eb',
          700: '#1E40AF',
          900: '#1E3A8A',
        },
        secondary: {
          DEFAULT: '#50B5E9',
          50: '#EAF8FF',
          100: '#D4EEFC',
          500: '#50B5E9',
          700: '#1D8ACD',
        },
        accent: {
          DEFAULT: '#25567B',
          50: '#E1ECF5',
          100: '#DCE6F1',
          500: '#25567B',
          700: '#173A57',
        },
        light: '#F5F8FB',
        green: {
          500: '#22c55e',
          600: '#15803d',
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
        xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
      },
      borderRadius: {
        xl: '1rem',
        '2xl': '1.5rem',
      },
      animation: {
        pulse: 'pulse 1.5s infinite',
        fadeIn: 'fadeIn 0.5s ease-in-out',
        bell: 'bell 1.5s ease-in-out infinite', // Animación por defecto
        'bell-hover': 'bell 0.7s ease-in-out infinite', // Versión más rápida en hover
        'bell-fast': 'bell 0.5s ease-in-out infinite', // Versión más rápida en touch
        bounceIn: 'bounceIn 0.7s ease-out', // Efecto de entrada en herramientas
        wiggle: 'wiggle 0.8s ease-in-out infinite', // Movimiento leve en las herramientas
      },
      keyframes: {
        pulse: {
          '0%, 100%': { transform: 'scale(1)', boxShadow: '0 0 8px rgba(255, 223, 0, 0.7)' },
          '50%': { transform: 'scale(1.2)', boxShadow: '0 0 16px rgba(255, 223, 0, 1)' },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        bell: {
          '0%, 100%': { transform: 'rotate(0deg)' },
          '25%': { transform: 'rotate(-10deg)' },
          '50%': { transform: 'rotate(10deg)' },
          '75%': { transform: 'rotate(-5deg)' },
        },
        bounceIn: {
          '0%': { transform: 'scale(0.8)', opacity: 0 },
          '50%': { transform: 'scale(1.05)', opacity: 1 },
          '100%': { transform: 'scale(1)', opacity: 1 },
        },
        wiggle: {
          '0%, 100%': { transform: 'rotate(0deg)' },
          '25%': { transform: 'rotate(-2deg)' },
          '50%': { transform: 'rotate(2deg)' },
          '75%': { transform: 'rotate(-1deg)' },
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