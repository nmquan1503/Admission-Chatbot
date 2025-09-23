import type { Message } from "../types"

interface Probs {
    message: Message
}

export default function MessageItem({ message }: Probs) {
    const isUser = message.sender === 'user'
    return (
        <div>{ message.text }</div>
    );
}