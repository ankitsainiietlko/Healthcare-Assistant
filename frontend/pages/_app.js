import { useEffect, useState } from "react";
import "../styles/globals.css"; // ✅ Load Tailwind styles

export default function App({ Component, pageProps }) {
  const [darkMode, setDarkMode] = useState(false);

  // ✅ Load dark mode preference when the page loads
  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedMode = localStorage.getItem("darkMode") === "true";
      setDarkMode(savedMode);
      if (savedMode) {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
    }
  }, []);

  const toggleDarkMode = () => {
    setDarkMode((prevMode) => {
      const newMode = !prevMode;
      document.documentElement.classList.toggle("dark", newMode);
      localStorage.setItem("darkMode", newMode);
      return newMode;
    });
  };

  return (
    <div className={`min-h-screen transition-all ${darkMode ? "dark bg-gray-900 text-white" : "bg-white text-black"}`}>
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Healthcare Assistant</h1>
          <button
            onClick={toggleDarkMode}
            className="bg-gray-500 text-white px-3 py-1 rounded-md hover:bg-gray-600 transition"
          >
            {darkMode ? "☀️ Light Mode" : "🌙 Dark Mode"}
          </button>
        </div>
        <Component {...pageProps} />
      </div>
    </div>
  );
}
