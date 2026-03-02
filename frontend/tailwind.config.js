/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          50: '#f0f4fa',
          100: '#dce6f5',
          200: '#b9cdeb',
          300: '#8aaad9',
          400: '#5a82c4',
          500: '#3560ad',
          600: '#1e3a6e',
          700: '#162b52',
          800: '#0f1e38',
          900: '#0a1526',
        },
        sky: {
          accent: '#4db8ff',
        }
      },
      fontFamily: {
        display: ['"Playfair Display"', 'serif'],
        body: ['"DM Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      animation: {
        'slide-up': 'slideUp 0.4s ease-out',
        'fade-in': 'fadeIn 0.3s ease-out',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
        'ticket-appear': 'ticketAppear 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)',
      },
      keyframes: {
        slideUp: { from: { opacity: 0, transform: 'translateY(20px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        fadeIn: { from: { opacity: 0 }, to: { opacity: 1 } },
        pulseSoft: { '0%, 100%': { opacity: 1 }, '50%': { opacity: 0.5 } },
        ticketAppear: { from: { opacity: 0, transform: 'scale(0.9) translateY(10px)' }, to: { opacity: 1, transform: 'scale(1) translateY(0)' } },
      }
    },
  },
  plugins: [],
}
