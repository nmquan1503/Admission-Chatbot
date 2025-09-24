import type { Message } from '../types'
import MessageItem from './MessageItem'
import TypingIndicator from './TypingIndicator'

interface Probs {
    messages: Message[],
    isTyping: boolean
}

export default function MessageList({ messages, isTyping }: Probs) {
    return (
        <div className='w-full flex justify-center'>
            <div className='max-w-[680px] w-full flex flex-col gap-[10px]'>
                {messages.map((msg) => (
                    <MessageItem message={msg} />
                ))}
                {isTyping && <TypingIndicator />}
            </div>
        </div>
    );
}