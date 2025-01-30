import { useEffect, useState } from "react";
import Image from "next/image";

export default function Navbar() {
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedMode = localStorage.getItem("darkMode") === "true";
      setDarkMode(savedMode);
      document.documentElement.classList.toggle("dark", savedMode);
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
    <nav className="flex justify-between items-center p-4 shadow-md dark:bg-gray-900 dark:text-white bg-white text-black">
      <div className="flex items-center">
        <Image src="/logo.png" alt="Logo" width={50} height={50} className="mr-2" />
        <h1 className="text-xl font-bold">Healthcare Assistant</h1>
      </div>
      <button
        onClick={toggleDarkMode}
        className="bg-gray-500 text-white px-3 py-1 rounded-md hover:bg-gray-600 transition"
      >
        {darkMode ? "☀️ Light Mode" : "🌙 Dark Mode"}
      </button>
    </nav>
  );
}
