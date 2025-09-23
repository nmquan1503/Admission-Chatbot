import type { Message } from '../types'
import MessageItem from './MessageItem'

interface Probs {
    messages: Message[]
}

export default function MessageList({ messages }: Probs) {
    return (
        <div>
            {messages.map((msg) => (
                <MessageItem message={msg} />
            ))}
        </div>
    );
}