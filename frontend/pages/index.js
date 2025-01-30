import Chatbot from "../components/Chatbot";

export default function Home() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold">Welcome to Healthcare Assistant</h1>
      <Chatbot />
    </div>
  );
}