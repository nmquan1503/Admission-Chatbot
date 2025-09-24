import type { Message } from "../types"
import ReactMarkdown from 'react-markdown'

interface Probs {
    message: Message
}

export default function MessageItem({ message }: Probs) {
    const isUser = message.sender === 'user'
    return (
        <div className={`w-full flex ${isUser ? 'justify-end' : 'justify-start'}`}>
            <div className={`prose prose-sm break-words rounded-3xl px-5 py-2 ${
                isUser 
                ? 'max-w-[90%] max-w-[500px] bg-gray-400 text-white' 
                : 'max-w-full'
            }`}
            >
                <ReactMarkdown>{message.text}</ReactMarkdown>
            </div>
        </div>
    );
}