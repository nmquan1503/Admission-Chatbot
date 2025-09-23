import type { Message } from '../types'
import MessageItem from './MessageItem'

interface Probs {
    messages: Message[]
}

export default function MessageList({ messages }: Probs) {
    return (
        <div className='w-full flex justify-center'>
            <div className='max-w-[680px] w-full flex flex-col gap-[10px]'>
                {messages.map((msg) => (
                    <MessageItem message={msg} />
                ))}
            </div>
        </div>
    );
}