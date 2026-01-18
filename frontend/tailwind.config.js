/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          bg: '#f8fafc',      // Very light gray background
          card: '#ffffff',    // White card background
          primary: '#0ea5e9', // Bright Sky Blue
          secondary: '#e0f2fe', // Soft Blue for active states
          text: '#334155',    // Professional Slate Gray
          danger: '#ef4444',  // Red (for low trust)
          success: '#22c55e', // Green (for verified)
        }
      },
    },
  },
  plugins: [],
}