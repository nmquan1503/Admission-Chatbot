import type { Message } from "../types"

interface Probs {
    message: Message
}

export default function MessageItem({ message }: Probs) {
    const isUser = message.sender === 'user'
    return (
        <div className={`w-full flex ${isUser ? 'justify-end' : 'justify-start'}`}>
            <div className={`break-words rounded-3xl px-5 py-2 ${
                isUser 
                ? 'max-w-[90%] max-w-[500px] bg-gray-400 text-white' 
                : 'max-w-full'
            }`}>{message.text}</div>
        </div>
    );
}